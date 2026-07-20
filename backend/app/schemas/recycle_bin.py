from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RecycleBinItem(BaseModel):
    id: str
    object_type: str
    object_name: str
    deleted_by: Optional[str] = None
    deleted_at: datetime
    days_remaining: int

    class Config:
        from_attributes = True


class RecycleBinListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RecycleBinItem]


class RecycleBinRestoreResponse(BaseModel):
    id: str
    object_type: str
    message: str