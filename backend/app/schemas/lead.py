from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ── Lead ─────────────────────────────────────────────────────────────

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    company: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    status: str = "New"
    source: str = "Other"
    description: Optional[str] = None
    owner_id: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class LeadOut(LeadBase):
    id: str
    is_converted: Optional[bool] = False
    converted_account_id: Optional[str] = None
    converted_contact_id: Optional[str] = None
    converted_opportunity_id: Optional[str] = None
    converted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Lead Conversion ──────────────────────────────────────────────────

class ConvertLeadRequest(BaseModel):
    create_account: bool = True
    account_name: Optional[str] = None  # If creating new account
    account_id: Optional[str] = None    # If converting to existing account
    create_opportunity: bool = True
    opportunity_name: Optional[str] = None
    opportunity_amount: Optional[float] = None


class ConvertLeadResponse(BaseModel):
    lead_id: str
    account_id: str
    contact_id: str
    opportunity_id: Optional[str] = None
    message: str


# ── Lead Assignment Rule ─────────────────────────────────────────────

class LeadAssignmentRuleBase(BaseModel):
    name: str
    is_active: bool = True
    condition_expression: str = "[]"
    assign_to_user_id: str
    priority: int = 0


class LeadAssignmentRuleCreate(LeadAssignmentRuleBase):
    pass


class LeadAssignmentRuleUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    condition_expression: Optional[str] = None
    assign_to_user_id: Optional[str] = None
    priority: Optional[int] = None


class LeadAssignmentRuleOut(LeadAssignmentRuleBase):
    id: str
    assign_to_user_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Web-to-Lead ──────────────────────────────────────────────────────

class WebToLeadRequest(BaseModel):
    first_name: str
    last_name: str
    company: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    source: str = "Web"


class WebToLeadResponse(BaseModel):
    success: bool
    lead_id: Optional[str] = None
    message: str