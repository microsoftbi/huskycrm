from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DuplicateRuleBase(BaseModel):
    name: str
    object_type: str
    is_active: bool = True
    matching_fields: str = "[]"  # JSON array of field names


class DuplicateRuleCreate(DuplicateRuleBase):
    pass


class DuplicateRuleUpdate(BaseModel):
    name: Optional[str] = None
    object_type: Optional[str] = None
    is_active: Optional[bool] = None
    matching_fields: Optional[str] = None


class DuplicateRuleOut(DuplicateRuleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DuplicateCheckRequest(BaseModel):
    object_type: str
    record_data: dict


class DuplicateMatch(BaseModel):
    id: str
    name: str
    matched_fields: list[str]


class DuplicateCheckResponse(BaseModel):
    has_duplicates: bool
    matches: list[DuplicateMatch] = []


class MergeRequest(BaseModel):
    master_id: str       # The record to keep
    slave_id: str        # The record to merge into master
    object_type: str