from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


# ── Event ─────────────────────────────────────────────────────────────

class EventBase(BaseModel):
    subject: str
    type: Optional[str] = "Visit"
    status: Optional[str] = "planned"
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    is_all_day_event: Optional[bool] = False
    show_as: Optional[str] = "busy"
    what_id: Optional[str] = None
    what_type: Optional[str] = None
    who_id: Optional[str] = None
    owner_id: Optional[str] = None
    purpose: Optional[str] = None
    preparation_notes: Optional[str] = None
    description: Optional[str] = None
    outcome: Optional[str] = None
    next_steps: Optional[str] = None
    location: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    subject: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    is_all_day_event: Optional[bool] = None
    show_as: Optional[str] = None
    what_id: Optional[str] = None
    what_type: Optional[str] = None
    who_id: Optional[str] = None
    owner_id: Optional[str] = None
    purpose: Optional[str] = None
    preparation_notes: Optional[str] = None
    description: Optional[str] = None
    outcome: Optional[str] = None
    next_steps: Optional[str] = None
    location: Optional[str] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None


class EventOut(EventBase):
    id: str
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Event detail with tasks ──────────────────────────────────────────

class TaskOutBrief(BaseModel):
    id: str
    subject: str
    status: str
    priority: str
    activity_date: Optional[date] = None
    assignee_id: Optional[str] = None
    sort_order: int

    class Config:
        from_attributes = True


class EventDetailOut(EventOut):
    tasks: list[TaskOutBrief] = []


# ── Task ──────────────────────────────────────────────────────────────

class TaskBase(BaseModel):
    subject: str
    status: Optional[str] = "not_started"
    priority: Optional[str] = "normal"
    activity_date: Optional[date] = None
    what_id: Optional[str] = None
    what_type: Optional[str] = None
    who_id: Optional[str] = None
    assignee_id: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    subject: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    activity_date: Optional[date] = None
    what_id: Optional[str] = None
    what_type: Optional[str] = None
    who_id: Optional[str] = None
    assignee_id: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class TaskOut(TaskBase):
    id: str
    event_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
