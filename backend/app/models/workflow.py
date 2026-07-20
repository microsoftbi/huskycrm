from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.id_gen import generate_id


class WorkflowRule(Base):
    """Defines an automated workflow rule."""
    __tablename__ = "workflow_rules"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("wf_"))
    name = Column(String(255), nullable=False)
    object_type = Column(String(120), nullable=False, index=True)  # "account", "contact", "opportunity", or custom API name
    trigger_event = Column(String(50), nullable=False)              # "create", "update", "create_or_update"
    condition_expression = Column(Text)                             # JSON: [{"field":"amount","operator":"gt","value":10000}]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    actions = relationship("WorkflowAction", back_populates="workflow",
                           cascade="all, delete-orphan", order_by="WorkflowAction.display_order")


class WorkflowAction(Base):
    """An action to execute when a workflow rule's conditions are met."""
    __tablename__ = "workflow_actions"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("wfa_"))
    workflow_id = Column(String(36), ForeignKey("workflow_rules.id"), nullable=False)
    action_type = Column(String(50), nullable=False)      # "update_field", "create_record", "send_notification"
    action_config = Column(Text, nullable=False)           # JSON config
    display_order = Column(Integer, default=0)

    workflow = relationship("WorkflowRule", back_populates="actions")


class WorkflowExecutionLog(Base):
    """Audit trail of workflow rule executions."""
    __tablename__ = "workflow_execution_logs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("wfl_"))
    workflow_id = Column(String(36), ForeignKey("workflow_rules.id"), nullable=False)
    object_type = Column(String(120), nullable=False)
    record_id = Column(String(36), nullable=False)
    workflow_name = Column(String(255))
    conditions_met = Column(Boolean, default=False)
    action_executed = Column(Boolean, default=False)
    result_message = Column(Text)
    executed_at = Column(DateTime, default=func.now(), server_default=func.now(), index=True)