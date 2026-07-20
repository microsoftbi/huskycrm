from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ── Approval Rule ────────────────────────────────────────────────────

class ApprovalRuleBase(BaseModel):
    name: str
    object_type: str
    is_active: bool = True
    condition_expression: str = "[]"
    approver_type: str = "manager"  # manager/role/specific_user
    approver_user_id: Optional[str] = None
    approval_order: int = 1


class ApprovalRuleCreate(ApprovalRuleBase):
    pass


class ApprovalRuleUpdate(BaseModel):
    name: Optional[str] = None
    object_type: Optional[str] = None
    is_active: Optional[bool] = None
    condition_expression: Optional[str] = None
    approver_type: Optional[str] = None
    approver_user_id: Optional[str] = None
    approval_order: Optional[int] = None


class ApprovalRuleOut(ApprovalRuleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Approval Step ────────────────────────────────────────────────────

class ApprovalStepOut(BaseModel):
    id: str
    request_id: str
    step_order: int
    approver_id: str
    approver_name: Optional[str] = None
    status: str
    comment: Optional[str] = None
    acted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Approval Request ─────────────────────────────────────────────────

class ApprovalRequestOut(BaseModel):
    id: str
    rule_id: str
    rule_name: Optional[str] = None
    object_type: str
    object_id: str
    object_name: Optional[str] = None
    submitter_id: str
    submitter_name: Optional[str] = None
    status: str
    current_step: int
    total_steps: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    steps: list[ApprovalStepOut] = []

    class Config:
        from_attributes = True


class ApprovalRequestListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ApprovalRequestOut]


class ApprovalActionRequest(BaseModel):
    comment: Optional[str] = None


# ── Trigger ──────────────────────────────────────────────────────────

class ApprovalTriggerRequest(BaseModel):
    object_type: str
    object_id: str
    record_data: dict