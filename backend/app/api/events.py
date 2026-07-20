from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.event import Event, Task
from app.models.auth import User
from app.models.crm import Account, Contact, Opportunity
from app.schemas.event import (
    EventCreate, EventUpdate, EventOut, EventDetailOut,
    TaskCreate, TaskUpdate, TaskOut,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/events", tags=["events"])


# ── Event CRUD ────────────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    status_filter: str = Query("", max_length=50),
    type_filter: str = Query("", max_length=50),
    what_id: str | None = Query(None),
    what_type: str = Query("", max_length=50),
    who_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(Event).options(selectinload(Event.tasks)).where(Event.is_deleted == False)
    count_query = select(func.count(Event.id)).where(Event.is_deleted == False)

    if search:
        search_filter = Event.subject.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if status_filter:
        query = query.where(Event.status == status_filter)
        count_query = count_query.where(Event.status == status_filter)

    if type_filter:
        query = query.where(Event.type == type_filter)
        count_query = count_query.where(Event.type == type_filter)

    if what_id is not None and what_type:
        query = query.where(Event.what_id == what_id, Event.what_type == what_type)
        count_query = count_query.where(Event.what_id == what_id, Event.what_type == what_type)

    if who_id is not None:
        query = query.where(Event.who_id == who_id)
        count_query = count_query.where(Event.who_id == who_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Event.start_datetime.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [EventOut.model_validate(e).model_dump() for e in items],
    }


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    event = Event(**payload.model_dump(exclude_unset=True))
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/{event_id}", response_model=EventDetailOut)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.tasks))
        .where(Event.id == event_id, Event.is_deleted == False)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventOut)
async def update_event(
    event_id: str,
    payload: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Event).where(Event.id == event_id, Event.is_deleted == False))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Event).where(Event.id == event_id, Event.is_deleted == False))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event.is_deleted = True
    event.deleted_at = datetime.now()
    await db.commit()


# ── Check-in / Check-out ──────────────────────────────────────────────

@router.post("/{event_id}/check-in", response_model=EventOut)
async def check_in(
    event_id: str,
    location: str = Query("", max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Event).where(Event.id == event_id, Event.is_deleted == False))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.status != "planned":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only planned events can be checked in")

    event.status = "in_progress"
    event.actual_start_time = datetime.now()
    if location:
        event.location = location
    await db.commit()
    await db.refresh(event)
    return event


@router.post("/{event_id}/check-out", response_model=EventOut)
async def check_out(
    event_id: str,
    description: str = Query("", max_length=2000),
    outcome: str = Query("", max_length=50),
    next_steps: str = Query("", max_length=2000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Event).where(Event.id == event_id, Event.is_deleted == False))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only in-progress events can be checked out")

    now = datetime.now()
    event.status = "completed"
    event.actual_end_time = now
    if event.actual_start_time:
        delta = now - event.actual_start_time
        event.duration_minutes = int(delta.total_seconds() // 60)
    if description:
        event.description = description
    if outcome:
        event.outcome = outcome
    if next_steps:
        event.next_steps = next_steps
    await db.commit()
    await db.refresh(event)
    return event


# ── Task CRUD (sub-resource of Event) ─────────────────────────────────

@router.get("/{event_id}/tasks", response_model=list[TaskOut])
async def list_tasks(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Task).where(Task.event_id == event_id).order_by(Task.sort_order)
    )
    return result.scalars().all()


@router.post("/{event_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    event_id: str,
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Verify event exists
    result = await db.execute(select(Event).where(Event.id == event_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    task = Task(event_id=event_id, **payload.model_dump(exclude_unset=True))
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.put("/{event_id}/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    event_id: str,
    task_id: str,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.event_id == event_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{event_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    event_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.event_id == event_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await db.delete(task)
    await db.commit()


# ── Related object event history (Activity Timeline) ─────────────────

@router.get("/by-account/{account_id}", response_model=list[EventOut])
async def get_account_events(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Event)
        .where(Event.what_id == account_id, Event.what_type == "account", Event.is_deleted == False)
        .order_by(Event.start_datetime.desc())
    )
    return result.scalars().all()


@router.get("/by-contact/{contact_id}", response_model=list[EventOut])
async def get_contact_events(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Event)
        .where(Event.who_id == contact_id, Event.is_deleted == False)
        .order_by(Event.start_datetime.desc())
    )
    return result.scalars().all()


@router.get("/by-opportunity/{opportunity_id}", response_model=list[EventOut])
async def get_opportunity_events(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Event)
        .where(Event.what_id == opportunity_id, Event.what_type == "opportunity", Event.is_deleted == False)
        .order_by(Event.start_datetime.desc())
    )
    return result.scalars().all()
