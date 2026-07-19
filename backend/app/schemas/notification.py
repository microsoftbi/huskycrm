from pydantic import BaseModel
from datetime import datetime


class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str | None = None
    notification_type: str
    reference_type: str | None = None
    reference_id: str | None = None
    is_read: bool = False
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UnreadCountOut(BaseModel):
    count: int