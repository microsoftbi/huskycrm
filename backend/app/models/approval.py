"""
Approval process models — ApprovalRule, ApprovalRequest, ApprovalStep.
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class ApprovalRule(Base):
    """Approval rule — defines trigger conditions and approvers."""
    __tablename__ = "approval_rules"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("apr_"))
    name = Column(String(255), nullable=False)
    object_type = Column(String(100), nullable=False, index=True, comment="Target object type: opportunity")
    is_active = Column(Boolean, default=True, index=True)
    condition_expression = Column(Text, nullable=False, comment="JSON array of conditions")
    approver_type = Column(String(50), nullable=False, default="manager", comment="manager/role/specific_user")
    approver_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, comment="Specific approver if approver_type=specific_user")
    approval_order = Column(Integer, default=1, comment="Approval step order")
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())


class ApprovalRequest(Base):
    """Approval request — an instance of an approval process."""
    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("apreq_"))
    rule_id = Column(String(36), ForeignKey("approval_rules.id"), nullable=False)
    object_type = Column(String(100), nullable=False)
    object_id = Column(String(36), nullable=False)
    submitter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending", index=True, comment="pending/approved/rejected/cancelled")
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    rule = relationship("ApprovalRule")
    submitter = relationship("User", foreign_keys=[submitter_id])
    steps = relationship("ApprovalStep", back_populates="request", order_by="ApprovalStep.step_order",
                          cascade="all, delete-orphan")


class ApprovalStep(Base):
    """Approval step — each step in an approval request."""
    __tablename__ = "approval_steps"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("apstep_"))
    request_id = Column(String(36), ForeignKey("approval_requests.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    approver_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending", comment="pending/approved/rejected")
    comment = Column(Text, nullable=True)
    acted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())

    request = relationship("ApprovalRequest", back_populates="steps")
    approver = relationship("User", foreign_keys=[approver_id])