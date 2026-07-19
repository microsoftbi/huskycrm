from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import json


class FieldDefBase(BaseModel):
    api_name: str
    label: str
    field_type: str
    is_required: bool = False
    is_unique: bool = False
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    picklist_values: Optional[list[str]] = None
    precision_total: Optional[int] = None
    precision_scale: Optional[int] = None
    lookup_object_id: Optional[str] = None
    display_order: int = 0


class FieldDefCreate(FieldDefBase):
    pass


class FieldDefOut(FieldDefBase):
    id: str
    object_id: str
    created_at: datetime
    updated_at: datetime

    @field_validator("picklist_values", mode="before")
    @classmethod
    def parse_picklist(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    class Config:
        from_attributes = True


class ObjectDefBase(BaseModel):
    api_name: str
    label: str
    plural_label: Optional[str] = None
    description: Optional[str] = None


class ObjectDefCreate(ObjectDefBase):
    fields: list[FieldDefCreate] = []


class ObjectDefUpdate(BaseModel):
    label: Optional[str] = None
    plural_label: Optional[str] = None
    description: Optional[str] = None


class ObjectDefOut(ObjectDefBase):
    id: str
    table_name: str
    is_active: bool
    fields: list[FieldDefOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecordData(BaseModel):
    """A generic key-value record for custom objects."""
    fields: dict  # key: field_api_name, value: field value


class RecordOut(BaseModel):
    id: int
    record_id: str
    owner_id: Optional[str] = None
    fields: dict
    created_at: Optional[str] = None
    updated_at: Optional[str] = None