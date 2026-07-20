"""
Recycle Bin API — list, restore, and permanently delete soft-deleted records.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.auth import User
from app.models.crm import Account, Contact, Opportunity, Product
from app.models.event import Event, Task
from app.schemas.recycle_bin import RecycleBinItem, RecycleBinListResponse
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/recycle-bin", tags=["recycle-bin"])

# Map of object types to their model classes and name display
RECYCLE_MODELS = {
    "account": {"model": Account, "name_field": "name", "label": "账户"},
    "contact": {"model": Contact, "name_field": "name", "label": "联系人"},
    "opportunity": {"model": Opportunity, "name_field": "name", "label": "销售机会"},
    "product": {"model": Product, "name_field": "name", "label": "产品"},
    "event": {"model": Event, "name_field": "subject", "label": "拜访"},
    "task": {"model": Task, "name_field": "subject", "label": "任务"},
}

RETENTION_DAYS = 30


def _get_model_name(record, object_type: str) -> str:
    """Get the display name of a record, handling Contact's first/last name."""
    if object_type == "contact":
        return f"{record.first_name} {record.last_name}"
    cfg = RECYCLE_MODELS[object_type]
    return str(getattr(record, cfg["name_field"], "") or "")


@router.get("", response_model=RecycleBinListResponse)
async def list_deleted_records(
    object_type: str | None = Query(None, description="Filter by object type"),
    search: str = Query("", max_length=255),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """List all soft-deleted records across all object types."""
    items = []
    total = 0

    models_to_query = (
        [m for t, m in RECYCLE_MODELS.items() if t == object_type]
        if object_type
        else list(RECYCLE_MODELS.values())
    )

    for cfg in models_to_query:
        model = cfg["model"]
        obj_type = [t for t, m in RECYCLE_MODELS.items() if m["model"] == model][0]

        query = select(model).where(model.is_deleted == True)
        count_query = select(func.count(model.id)).where(model.is_deleted == True)

        if search and hasattr(model, "name"):
            query = query.where(model.name.ilike(f"%{search}%"))
            count_query = count_query.where(model.name.ilike(f"%{search}%"))
        elif search and obj_type == "contact":
            q = f"%{search}%"
            query = query.where(
                Contact.first_name.ilike(q) | Contact.last_name.ilike(q) | Contact.email.ilike(q)
            )
            count_query = count_query.where(
                Contact.first_name.ilike(q) | Contact.last_name.ilike(q) | Contact.email.ilike(q)
            )
        elif search and obj_type in ("event", "task"):
            query = query.where(model.subject.ilike(f"%{search}%"))
            count_query = count_query.where(model.subject.ilike(f"%{search}%"))

        result = await db.execute(count_query)
        total += result.scalar() or 0

        query = query.order_by(model.deleted_at.desc())
        result = await db.execute(query)
        records = result.scalars().all()

        for record in records:
            if record.deleted_at:
                days_remaining = max(0, RETENTION_DAYS - (datetime.now() - record.deleted_at).days)
            else:
                days_remaining = RETENTION_DAYS

            items.append(RecycleBinItem(
                id=record.id,
                object_type=obj_type,
                object_name=_get_model_name(record, obj_type),
                deleted_by=None,
                deleted_at=record.deleted_at or datetime.now(),
                days_remaining=days_remaining,
            ))

    # Sort by deleted_at desc (all items combined)
    items.sort(key=lambda x: x.deleted_at, reverse=True)

    # Paginate
    start = (page - 1) * page_size
    paged_items = items[start:start + page_size]

    return RecycleBinListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=paged_items,
    )


@router.post("/{object_type}/{record_id}/restore")
async def restore_record(
    object_type: str,
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    """Restore a soft-deleted record."""
    cfg = RECYCLE_MODELS.get(object_type)
    if not cfg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported object type: {object_type}")

    model = cfg["model"]
    result = await db.execute(select(model).where(model.id == record_id, model.is_deleted == True))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found in recycle bin")

    record.is_deleted = False
    record.deleted_at = None
    await db.commit()

    return {
        "id": record_id,
        "object_type": object_type,
        "message": "记录已恢复",
    }


@router.delete("/{object_type}/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def permanently_delete_record(
    object_type: str,
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    """Permanently delete a record from the recycle bin (admin only)."""
    cfg = RECYCLE_MODELS.get(object_type)
    if not cfg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported object type: {object_type}")

    model = cfg["model"]
    result = await db.execute(select(model).where(model.id == record_id, model.is_deleted == True))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found in recycle bin")

    await db.delete(record)
    await db.commit()


@router.post("/cleanup")
async def cleanup_expired_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    """Permanently delete records that have been in the recycle bin for more than 30 days."""
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    total_cleaned = 0

    for cfg in RECYCLE_MODELS.values():
        model = cfg["model"]
        result = await db.execute(
            select(model).where(model.is_deleted == True, model.deleted_at < cutoff)
        )
        expired = result.scalars().all()
        for record in expired:
            await db.delete(record)
            total_cleaned += 1

    if total_cleaned > 0:
        await db.commit()

    return {
        "message": f"已清理 {total_cleaned} 条过期记录",
        "cleaned_count": total_cleaned,
    }