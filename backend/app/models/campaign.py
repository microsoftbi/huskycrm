"""
Campaign management models — Campaign and CampaignMember.
"""
from sqlalchemy import Column, String, Text, Date, DECIMAL, Integer, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id
from app.models.mixins import SoftDeleteMixin


class Campaign(SoftDeleteMixin, Base):
    """Marketing campaign — tracks budget, members, ROI, and converted opportunities."""
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("camp_"))
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), default="other", comment="conference/exhibition/email/ad/other")
    status = Column(String(20), default="planning", comment="planning/in_progress/completed/cancelled")
    budget = Column(DECIMAL(15, 2), nullable=True, comment="Budget amount")
    actual_cost = Column(DECIMAL(15, 2), nullable=True, comment="Actual cost")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="campaigns")
    members = relationship("CampaignMember", back_populates="campaign", cascade="all, delete-orphan")


class CampaignMember(Base):
    """Campaign member — tracks contacts associated with a campaign."""
    __tablename__ = "campaign_members"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("campm_"))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=True)
    status = Column(String(20), default="invited", comment="invited/attended/converted/not_interested")
    created_at = Column(DateTime, default=func.now(), server_default=func.now())

    campaign = relationship("Campaign", back_populates="members")
    contact = relationship("Contact", back_populates="campaign_members")

    __table_args__ = (
        Index("idx_campaign_member", "campaign_id", "contact_id", unique=True),
    )