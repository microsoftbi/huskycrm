"""
Validation service — evaluates validation rules before record save.
Reuses the workflow condition evaluator.
"""
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.validation_rule import ValidationRule
from app.services.workflow_service import evaluate_conditions


async def validate_record(
    db: AsyncSession,
    object_type: str,
    record_data: dict,
) -> list[dict]:
    """
    Validate a record against all active validation rules.
    Returns a list of validation errors.
    Each error: {"field": "...", "message": "..."}
    """
    result = await db.execute(
        select(ValidationRule).where(
            ValidationRule.object_type == object_type,
            ValidationRule.is_active == True,
        )
    )
    rules = result.scalars().all()

    errors = []
    for rule in rules:
        conditions = rule.condition_expression
        if isinstance(conditions, str):
            conditions = json.loads(conditions) if conditions else []

        conditions_met = evaluate_conditions(record_data, conditions or [])
        if conditions_met:
            errors.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "message": rule.error_message,
            })

    return errors