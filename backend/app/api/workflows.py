import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.workflow import WorkflowRule, WorkflowAction, WorkflowExecutionLog
from app.models.auth import User
from app.schemas.workflow import (
    WorkflowRuleCreate, WorkflowRuleUpdate, WorkflowRuleOut, WorkflowLogOut,
)
from app.core.deps import get_current_user
from app.services import workflow_service as wfsvc

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowRuleOut])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkflowRule)
        .options(selectinload(WorkflowRule.actions))
        .order_by(WorkflowRule.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=WorkflowRuleOut, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = WorkflowRule(
        name=payload.name,
        object_type=payload.object_type,
        trigger_event=payload.trigger_event,
        condition_expression=json.dumps(payload.condition_expression) if payload.condition_expression else None,
    )
    db.add(rule)
    await db.flush()

    for action_data in payload.actions:
        action = WorkflowAction(
            workflow_id=rule.id,
            action_type=action_data.action_type,
            action_config=json.dumps(action_data.action_config),
            display_order=action_data.display_order,
        )
        db.add(action)

    await db.commit()
    await db.refresh(rule)

    # Reload with actions
    result = await db.execute(
        select(WorkflowRule)
        .options(selectinload(WorkflowRule.actions))
        .where(WorkflowRule.id == rule.id)
    )
    return result.scalar_one()


@router.get("/{workflow_id}", response_model=WorkflowRuleOut)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkflowRule)
        .options(selectinload(WorkflowRule.actions))
        .where(WorkflowRule.id == workflow_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return rule


@router.put("/{workflow_id}", response_model=WorkflowRuleOut)
async def update_workflow(
    workflow_id: int,
    payload: WorkflowRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(WorkflowRule).where(WorkflowRule.id == workflow_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "condition_expression" in update_data:
        update_data["condition_expression"] = json.dumps(update_data["condition_expression"]) if update_data["condition_expression"] else None
    if "is_active" in update_data:
        rule.is_active = update_data["is_active"]
    if "name" in update_data:
        rule.name = update_data["name"]

    await db.commit()
    await db.refresh(rule)

    result = await db.execute(
        select(WorkflowRule)
        .options(selectinload(WorkflowRule.actions))
        .where(WorkflowRule.id == workflow_id)
    )
    return result.scalar_one()


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(WorkflowRule).where(WorkflowRule.id == workflow_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await db.delete(rule)
    await db.commit()


@router.get("/{workflow_id}/logs", response_model=list[WorkflowLogOut])
async def get_workflow_logs(
    workflow_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WorkflowExecutionLog)
        .where(WorkflowExecutionLog.workflow_id == workflow_id)
        .order_by(WorkflowExecutionLog.executed_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/{workflow_id}/test", response_model=dict)
async def test_workflow(
    workflow_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test a workflow rule against sample record data."""
    result = await db.execute(
        select(WorkflowRule)
        .options(selectinload(WorkflowRule.actions))
        .where(WorkflowRule.id == workflow_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Workflow not found")

    record_data = payload.get("record", {})
    conditions = rule.condition_expression
    if isinstance(conditions, str):
        conditions = json.loads(conditions) if conditions else []

    conditions_met = wfsvc.evaluate_conditions(record_data, conditions or [])

    return {
        "workflow_name": rule.name,
        "conditions_met": conditions_met,
        "conditions": conditions,
        "record": record_data,
    }