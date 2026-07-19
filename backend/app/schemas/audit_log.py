from pydantic import BaseModel
from datetime import datetime


class AuditLogOut(BaseModel):
    id: str
    object_type: str
    object_id: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    action: str
    user_id: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TimelineEntry(BaseModel):
    type: str  # "audit" | "event" | "task"
    action: str | None = None
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    subject: str | None = None
    status: str | None = None
    result: str | None = None
    user_id: str | None = None
    user_display_name: str | None = None
    created_at: datetime | None = None
    reference_id: str | None = None
    reference_type: str | None = None