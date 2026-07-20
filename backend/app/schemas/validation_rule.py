from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ValidationRuleBase(BaseModel):
    name: str
    object_type: str
    is_active: bool = True
    condition_expression: str = "[]"  # JSON array of conditions
    error_message: str


class ValidationRuleCreate(ValidationRuleBase):
    pass


class ValidationRuleUpdate(BaseModel):
    name: Optional[str] = None
    object_type: Optional[str] = None
    is_active: Optional[bool] = None
    condition_expression: Optional[str] = None
    error_message: Optional[str] = None


class ValidationRuleOut(ValidationRuleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ValidationTestRequest(BaseModel):
    record_data: dict  # Sample record data to test against
    condition_expression: str


class ValidationTestResponse(BaseModel):
    is_valid: bool
    error_message: str | None = None