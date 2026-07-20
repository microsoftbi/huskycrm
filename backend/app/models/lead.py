"""
Lead model — standard Salesforce Lead object.
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func, Integer
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id
from app.models.mixins import SoftDeleteMixin


class Lead(SoftDeleteMixin, Base):
    """Lead — potential customer / prospect."""
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("lead_"))
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    company = Column(String(255), nullable=False, index=True, comment="Company name")
    email = Column(String(255), index=True)
    phone = Column(String(50))
    mobile_phone = Column(String(50))
    title = Column(String(255), comment="Job title")
    industry = Column(String(100))
    status = Column(String(50), default="New", index=True, comment="New/Contacted/Qualified/Unqualified/Converted")
    source = Column(String(50), default="Other", comment="Web/Phone/Referral/Conference/Email/Other")
    description = Column(Text)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_converted = Column(Boolean, default=False, comment="Whether this lead has been converted")
    converted_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=True)
    converted_contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=True)
    converted_opportunity_id = Column(String(36), ForeignKey("opportunities.id"), nullable=True)
    converted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="leads", foreign_keys=[owner_id])


class LeadAssignmentRule(Base):
    """Lead assignment rule — auto-assign leads based on conditions."""
    __tablename__ = "lead_assignment_rules"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("lass_"))
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    condition_expression = Column(Text, nullable=False, comment="JSON array of conditions (same format as workflow)")
    assign_to_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, comment="User to assign lead to")
    priority = Column(Integer, default=0, comment="Higher priority rules evaluated first")
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    assign_to_user = relationship("User", foreign_keys=[assign_to_user_id])