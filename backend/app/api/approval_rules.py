"""
Approval Rules API — CRUD for approval rules.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.auth import User
from app.models.approval import ApprovalRule, ApprovalRequest, ApprovalStep
from app.schemas.approval import (
    ApprovalRuleCreate, ApprovalRuleUpdate, ApprovalRuleOut,
    ApprovalTriggerRequest, ApprovalRequestOut, ApprovalActionRequest,
    ApprovalRequestListResponse, ApprovalStepOut,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.approval_service import trigger_approval, approve_request, reject_request, get_my_queue

router = APIRouter(prefix="/api/approval-rules", tags=["approval"])


async def get_approval_request_detail(db: AsyncSession, request_id: str) -> ApprovalRequestOut:
    """Helper to fetch and enrich a single approval request."""
    result = await db.execute(
        select(ApprovalRequest)
        .options(selectinload(ApprovalRequest.steps))
        .where(ApprovalRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")

    return ApprovalRequestOut(
        id=req.id,
        rule_id=req.rule_id,
        rule_name=req.rule.name if req.rule else None,
        object_type=req.object_type,
        object_id=req.object_id,
        object_name=req.object_id,
        submitter_id=req.submitter_id,
        submitter_name=req.submitter.display_name if req.submitter else None,
        status=req.status,
        current_step=req.current_step,
        total_steps=req.total_steps,
        created_at=req.created_at,
        updated_at=req.updated_at,
        steps=[ApprovalStepOut.model_validate(s) for s in req.steps],
    )


# ── Rule CRUD ────────────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_approval_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    object_type: str = Query("", max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(ApprovalRule)
    count_query = select(func.count(ApprovalRule.id))

    if object_type:
        query = query.where(ApprovalRule.object_type == object_type)
        count_query = count_query.where(ApprovalRule.object_type == object_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ApprovalRule.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [ApprovalRuleOut.model_validate(r).model_dump() for r in items],
    }


@router.post("", response_model=ApprovalRuleOut, status_code=status.HTTP_201_CREATED)
async def create_approval_rule(
    payload: ApprovalRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Validate condition_expression
    try:
        conds = json.loads(payload.condition_expression)
        if not isinstance(conds, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="condition_expression must be a valid JSON array")

    rule = ApprovalRule(**payload.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


# ── Approval Requests ────────────────────────────────────────────────

@router.post("/trigger", response_model=ApprovalRequestOut | None)
async def trigger_approval_endpoint(
    payload: ApprovalTriggerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    """Trigger an approval process for a record."""
    request = await trigger_approval(
        db, payload.object_type, payload.object_id, payload.record_data, current_user.id
    )
    if not request:
        raise HTTPException(status_code=200, detail="No approval rules matched")
    return request


@router.get("/my-queue", response_model=ApprovalRequestListResponse)
async def my_approval_queue(
    status_filter: str = Query("", max_length=50),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    items, total = await get_my_queue(db, current_user.id, status_filter or None, page, page_size)

    enriched = []
    for req in items:
        enriched.append(ApprovalRequestOut(
            id=req.id,
            rule_id=req.rule_id,
            rule_name=req.rule.name if req.rule else None,
            object_type=req.object_type,
            object_id=req.object_id,
            object_name=req.object_id,
            submitter_id=req.submitter_id,
            submitter_name=req.submitter.display_name if req.submitter else None,
            status=req.status,
            current_step=req.current_step,
            total_steps=req.total_steps,
            created_at=req.created_at,
            updated_at=req.updated_at,
            steps=[ApprovalStepOut.model_validate(s) for s in req.steps],
        ))

    return ApprovalRequestListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=enriched,
    )


@router.get("/requests", response_model=ApprovalRequestListResponse)
async def list_approval_requests(
    status_filter: str = Query("", max_length=50),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(ApprovalRequest).options(selectinload(ApprovalRequest.steps), selectinload(ApprovalRequest.rule), selectinload(ApprovalRequest.submitter))
    count_query = select(func.count(ApprovalRequest.id))

    if status_filter:
        query = query.where(ApprovalRequest.status == status_filter)
        count_query = count_query.where(ApprovalRequest.status == status_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ApprovalRequest.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    # Enrich with object names
    enriched = []
    for req in items:
        enriched.append(ApprovalRequestOut(
            id=req.id,
            rule_id=req.rule_id,
            rule_name=req.rule.name if req.rule else None,
            object_type=req.object_type,
            object_id=req.object_id,
            object_name=req.object_id,
            submitter_id=req.submitter_id,
            submitter_name=req.submitter.display_name if req.submitter else None,
            status=req.status,
            current_step=req.current_step,
            total_steps=req.total_steps,
            created_at=req.created_at,
            updated_at=req.updated_at,
            steps=[ApprovalStepOut.model_validate(s) for s in req.steps],
        ))

    return ApprovalRequestListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=enriched,
    )


@router.get("/requests/{request_id}", response_model=ApprovalRequestOut)
async def get_approval_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    return await get_approval_request_detail(db, request_id)


@router.post("/requests/{request_id}/approve", response_model=ApprovalRequestOut)
async def approve_approval_request(
    request_id: str,
    payload: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    try:
        request = await approve_request(db, request_id, current_user.id, payload.comment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return await get_approval_request_detail(db, request_id)


@router.post("/requests/{request_id}/reject", response_model=ApprovalRequestOut)
async def reject_approval_request(
    request_id: str,
    payload: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    try:
        request = await reject_request(db, request_id, current_user.id, payload.comment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return await get_approval_request_detail(db, request_id)


# ── Rule CRUD (by ID) — must come AFTER specific routes to avoid conflicts ──

@router.get("/{rule_id}", response_model=ApprovalRuleOut)
async def get_approval_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(ApprovalRule).where(ApprovalRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval rule not found")
    return rule


@router.put("/{rule_id}", response_model=ApprovalRuleOut)
async def update_approval_rule(
    rule_id: str,
    payload: ApprovalRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(ApprovalRule).where(ApprovalRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval rule not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "condition_expression" in update_data:
        try:
            conds = json.loads(update_data["condition_expression"])
            if not isinstance(conds, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="condition_expression must be a valid JSON array")

    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_approval_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(ApprovalRule).where(ApprovalRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval rule not found")
    await db.delete(rule)
    await db.commit()