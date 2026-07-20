from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


# ── Campaign Member ──────────────────────────────────────────────────

class CampaignMemberBase(BaseModel):
    contact_id: Optional[str] = None
    status: str = "invited"


class CampaignMemberCreate(CampaignMemberBase):
    pass


class CampaignMemberUpdate(BaseModel):
    status: Optional[str] = None


class CampaignMemberOut(CampaignMemberBase):
    id: str
    campaign_id: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Campaign ─────────────────────────────────────────────────────────

class CampaignBase(BaseModel):
    name: str
    type: str = "other"
    status: str = "planning"
    budget: Optional[float] = None
    actual_cost: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    actual_cost: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class CampaignOut(CampaignBase):
    id: str
    member_count: int = 0
    converted_opportunities: int = 0
    converted_amount: float = 0.0
    roi: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignDetailOut(CampaignOut):
    members: list[CampaignMemberOut] = []


class ROIResponse(BaseModel):
    budget: Optional[float]
    actual_cost: Optional[float]
    member_count: int
    converted_opportunities: int
    converted_amount: float
    roi: Optional[float]
    roi_label: str