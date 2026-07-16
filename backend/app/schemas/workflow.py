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
    id: int
    workflow_id: int

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
    id: int
    is_active: bool
    actions: list[WorkflowActionOut] = []
    created_at: datetime
    updated_at: datetime

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
    id: int
    workflow_id: int
    workflow_name: Optional[str] = None
    object_type: str
    record_id: int
    conditions_met: bool
    action_executed: bool
    result_message: Optional[str] = None
    executed_at: datetime

    class Config:
        from_attributes = True