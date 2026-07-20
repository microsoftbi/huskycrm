"""
Validation Rules API — CRUD for validation rules and test endpoint.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.auth import User
from app.models.validation_rule import ValidationRule
from app.schemas.validation_rule import (
    ValidationRuleCreate, ValidationRuleUpdate, ValidationRuleOut,
    ValidationTestRequest, ValidationTestResponse,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.workflow_service import evaluate_conditions

router = APIRouter(prefix="/api/validation-rules", tags=["validation-rules"])


@router.get("", response_model=dict)
async def list_validation_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    object_type: str = Query("", max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(ValidationRule)
    count_query = select(func.count(ValidationRule.id))

    if object_type:
        query = query.where(ValidationRule.object_type == object_type)
        count_query = count_query.where(ValidationRule.object_type == object_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ValidationRule.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [ValidationRuleOut.model_validate(r).model_dump() for r in items],
    }


@router.post("", response_model=ValidationRuleOut, status_code=status.HTTP_201_CREATED)
async def create_validation_rule(
    payload: ValidationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Validate condition_expression is valid JSON
    try:
        conditions = json.loads(payload.condition_expression)
        if not isinstance(conditions, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="condition_expression must be a valid JSON array")

    rule = ValidationRule(**payload.model_dump(exclude_unset=True))
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=ValidationRuleOut)
async def get_validation_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(ValidationRule).where(ValidationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation rule not found")
    return rule


@router.put("/{rule_id}", response_model=ValidationRuleOut)
async def update_validation_rule(
    rule_id: str,
    payload: ValidationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(ValidationRule).where(ValidationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation rule not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "condition_expression" in update_data:
        try:
            conditions = json.loads(update_data["condition_expression"])
            if not isinstance(conditions, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="condition_expression must be a valid JSON array")

    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_validation_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(ValidationRule).where(ValidationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation rule not found")
    await db.delete(rule)
    await db.commit()


@router.post("/test", response_model=ValidationTestResponse)
async def test_validation_rule(
    payload: ValidationTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Test a condition expression against sample record data without saving a rule."""
    try:
        conditions = json.loads(payload.condition_expression) if payload.condition_expression else []
        if not isinstance(conditions, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="condition_expression must be a valid JSON array")

    conditions_met = evaluate_conditions(payload.record_data, conditions)
    return ValidationTestResponse(
        is_valid=not conditions_met,
        error_message="条件匹配，校验失败" if conditions_met else None,
    )