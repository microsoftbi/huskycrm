from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import json


class WorkflowActionBase(BaseModel):
    action_type: str
    action_config: dict
    display_order: int = 0


class WorkflowRuleBase(BaseModel):
    name: str
    object_type: str
    trigger_event: str
    condition_expression: Optional[list[dict]] = None


class WorkflowRuleCreate(WorkflowRuleBase):
    actions: list[WorkflowActionBase] = []


class WorkflowRuleUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    condition_expression: Optional[list[dict]] = None


class WorkflowActionOut(WorkflowActionBase):
    id: str
    workflow_id: str

    @field_validator("action_config", mode="before")
    @classmethod
    def parse_action_config(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return {}
        return v

    class Config:
        from_attributes = True


class WorkflowRuleOut(WorkflowRuleBase):
    id: str
    is_active: bool
    actions: list[WorkflowActionOut] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("condition_expression", mode="before")
    @classmethod
    def parse_conditions(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    class Config:
        from_attributes = True


class WorkflowLogOut(BaseModel):
    id: str
    workflow_id: str
    workflow_name: Optional[str] = None
    object_type: str
    record_id: str
    conditions_met: bool
    action_executed: bool
    result_message: Optional[str] = None
    executed_at: Optional[datetime] = None

    class Config:
        from_attributes = True