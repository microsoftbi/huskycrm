from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.auth import User
from app.models.event import Event, Task
from app.schemas.audit_log import TimelineEntry
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api", tags=["audit-logs"])


@router.get("/audit-logs/{object_type}/{object_id}", response_model=list[TimelineEntry])
async def get_audit_logs(
    object_type: str,
    object_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Get change history for a specific record."""
    type_map = {
        "account": "Account", "contact": "Contact", "opportunity": "Opportunity",
        "product": "Product", "event": "Event", "task": "Task",
        "territory": "Territory",
    }
    model_type = type_map.get(object_type.lower(), object_type)

    query = (
        select(AuditLog)
        .where(AuditLog.object_type == model_type, AuditLog.object_id == object_id)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    entries = []
    for log in logs:
        user_result = await db.execute(select(User).where(User.id == log.user_id))
        user = user_result.scalar_one_or_none()

        entries.append(TimelineEntry(
            type="audit",
            action=log.action,
            field_name=log.field_name,
            old_value=log.old_value,
            new_value=log.new_value,
            user_id=log.user_id,
            user_display_name=user.display_name if user else "System",
            created_at=log.created_at,
        ))

    return entries


@router.get("/timeline/{object_type}/{object_id}", response_model=list[TimelineEntry])
async def get_timeline(
    object_type: str,
    object_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Get merged timeline: audit logs + related events + tasks."""
    type_map = {
        "account": "Account", "contact": "Contact", "opportunity": "Opportunity",
    }
    model_type = type_map.get(object_type.lower(), object_type)

    # 1. Get audit logs
    audit_query = (
        select(AuditLog)
        .where(AuditLog.object_type == model_type, AuditLog.object_id == object_id)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
    )
    audit_result = await db.execute(audit_query)
    audit_logs = audit_result.scalars().all()

    entries = []
    for log in audit_logs:
        user_result = await db.execute(select(User).where(User.id == log.user_id))
        user = user_result.scalar_one_or_none()
        entries.append(TimelineEntry(
            type="audit",
            action=log.action,
            field_name=log.field_name,
            old_value=log.old_value,
            new_value=log.new_value,
            user_id=log.user_id,
            user_display_name=user.display_name if user else "System",
            created_at=log.created_at,
        ))

    # 2. Get related events (by what_id)
    if object_type.lower() in ("account", "contact", "opportunity"):
        what_type_map = {"account": "Account", "contact": "Contact", "opportunity": "Opportunity"}
        what_type = what_type_map[object_type.lower()]
        event_query = (
            select(Event)
            .where(Event.what_id == object_id, Event.what_type == what_type)
            .order_by(Event.actual_start_time.desc())
            .limit(20)
        )
        event_result = await db.execute(event_query)
        events = event_result.scalars().all()

        for ev in events:
            user_result = await db.execute(select(User).where(User.id == ev.owner_id))
            user = user_result.scalar_one_or_none()
            entries.append(TimelineEntry(
                type="event",
                subject=ev.subject,
                status=ev.status,
                result=ev.result,
                user_id=ev.owner_id,
                user_display_name=user.display_name if user else None,
                created_at=ev.actual_start_time or ev.created_at,
                reference_id=ev.id,
                reference_type="event",
            ))

            # 3. Get tasks for each event
            task_query = select(Task).where(Task.event_id == ev.id).order_by(Task.created_at.desc())
            task_result = await db.execute(task_query)
            tasks = task_result.scalars().all()
            for t in tasks:
                entries.append(TimelineEntry(
                    type="task",
                    subject=t.subject,
                    status="completed" if t.is_completed else "pending",
                    created_at=t.completed_at or t.created_at,
                    reference_id=t.id,
                    reference_type="task",
                ))

    # Sort all entries by created_at desc
    entries.sort(key=lambda e: e.created_at or "", reverse=True)

    # Paginate
    start = (page - 1) * page_size
    return entries[start:start + page_size]