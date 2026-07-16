"""
Workflow engine service.

Evaluates condition expressions against record data and executes actions.
"""
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.workflow import WorkflowRule, WorkflowAction, WorkflowExecutionLog
from app.models.crm import Account, Contact, Opportunity
from app.models.custom_object import CustomObjectDef
from app.services import custom_object_service as cosvc
from app.utils import dynamic_ddl as ddl


OPERATORS = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "gt": lambda a, b: (a or 0) > b,
    "gte": lambda a, b: (a or 0) >= b,
    "lt": lambda a, b: (a or 0) < b,
    "lte": lambda a, b: (a or 0) <= b,
    "contains": lambda a, b: b in str(a or ""),
    "not_contains": lambda a, b: b not in str(a or ""),
    "is_empty": lambda a, _: a is None or a == "",
    "is_not_empty": lambda a, _: a is not None and a != "",
}


def evaluate_conditions(record: dict, conditions: list[dict]) -> bool:
    """
    Evaluate a list of conditions against a record dict.
    Conditions are ANDed together.
    Each condition: {"field": "amount", "operator": "gt", "value": 10000}
    """
    if not conditions:
        return True

    for cond in conditions:
        field = cond.get("field")
        op = cond.get("operator", "eq")
        value = cond.get("value")

        record_value = record.get(field) if field in record else None
        operator_fn = OPERATORS.get(op)

        if operator_fn is None:
            return False

        if not operator_fn(record_value, value):
            return False

    return True


async def execute_actions(
    db: AsyncSession,
    actions: list[WorkflowAction],
    record: dict,
    object_type: str,
    obj_def: CustomObjectDef | None = None,
) -> str:
    """Execute a list of actions and return a result message."""
    results = []
    for action in actions:
        config = action.action_config
        if isinstance(config, str):
            config = json.loads(config)

        if action.action_type == "update_field":
            field = config.get("field")
            value = config.get("value")
            if field and obj_def:
                record_id = record.get("id")
                if record_id:
                    await cosvc.update_record(db, obj_def, record_id, {field: value})
                    results.append(f"Updated {field} = {value}")
                else:
                    results.append("Cannot update: no record ID")

        elif action.action_type == "create_record":
            target_obj_name = config.get("object_type")
            target_fields = config.get("fields", {})
            if target_obj_name:
                try:
                    target_obj = await cosvc.get_object_by_name(db, target_obj_name)
                    await cosvc.create_record(db, target_obj, target_fields)
                    results.append(f"Created record in {target_obj_name}")
                except HTTPException:
                    results.append(f"Failed: object {target_obj_name} not found")

        elif action.action_type == "send_notification":
            message = config.get("message", "Notification triggered")
            results.append(f"Notification: {message}")

    return "; ".join(results) if results else "No actions executed"


async def evaluate_workflow(
    db: AsyncSession,
    object_type: str,
    record_id: int,
    record_data: dict,
    trigger_event: str,
) -> list[dict]:
    """
    Evaluate all active workflow rules for a given object type and trigger event.
    Returns a list of execution log entries.
    """
    result = await db.execute(
        select(WorkflowRule)
        .where(
            WorkflowRule.object_type == object_type,
            WorkflowRule.is_active == True,
            WorkflowRule.trigger_event.in_([trigger_event, "create_or_update"]),
        )
    )
    rules = result.scalars().all()

    # Get custom object def if applicable
    obj_def = None
    try:
        if not object_type.startswith("obj_"):
            obj_def = await cosvc.get_object_by_name(db, object_type)
    except HTTPException:
        pass

    logs = []
    for rule in rules:
        conditions = rule.condition_expression
        if isinstance(conditions, str):
            conditions = json.loads(conditions) if conditions else []

        conditions_met = evaluate_conditions(record_data, conditions or [])

        action_executed = False
        result_message = None

        if conditions_met:
            result_message = await execute_actions(db, rule.actions, record_data, object_type, obj_def)
            action_executed = True

        log_entry = WorkflowExecutionLog(
            workflow_id=rule.id,
            object_type=object_type,
            record_id=record_id,
            workflow_name=rule.name,
            conditions_met=conditions_met,
            action_executed=action_executed,
            result_message=result_message,
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        logs.append(log_entry)

    return logs