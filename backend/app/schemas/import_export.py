from pydantic import BaseModel
from datetime import datetime


class ImportPreviewResponse(BaseModel):
    preview_id: str
    columns: list[str]
    mapping_suggestions: dict[str, str | None]
    available_fields: list[dict]
    preview_rows: list[list[str]]


class ImportConfirmRequest(BaseModel):
    preview_id: str
    mapping: dict[str, str]  # CSV column -> field name


class ImportResultResponse(BaseModel):
    success_rows: int
    error_rows: int
    errors: list[dict] = []


class ImportJobOut(BaseModel):
    id: str
    object_type: str
    filename: str
    total_rows: int
    success_rows: int
    error_rows: int
    errors: str | None = None
    status: str
    created_by: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True