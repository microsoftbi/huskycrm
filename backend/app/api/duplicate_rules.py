"""
Duplicate Rules API — CRUD for duplicate rules, check duplicates, merge records.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.auth import User
from app.models.duplicate_rule import DuplicateRule
from app.schemas.duplicate_rule import (
    DuplicateRuleCreate, DuplicateRuleUpdate, DuplicateRuleOut,
    DuplicateCheckRequest, DuplicateCheckResponse, DuplicateMatch,
    MergeRequest,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.duplicate_service import check_duplicates, merge_records

router = APIRouter(prefix="/api/duplicate-rules", tags=["duplicate-rules"])


# ── Rule CRUD ────────────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_duplicate_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    object_type: str = Query("", max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(DuplicateRule)
    count_query = select(func.count(DuplicateRule.id))

    if object_type:
        query = query.where(DuplicateRule.object_type == object_type)
        count_query = count_query.where(DuplicateRule.object_type == object_type)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(DuplicateRule.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [DuplicateRuleOut.model_validate(r).model_dump() for r in items],
    }


@router.post("", response_model=DuplicateRuleOut, status_code=status.HTTP_201_CREATED)
async def create_duplicate_rule(
    payload: DuplicateRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Validate matching_fields is valid JSON
    try:
        fields = json.loads(payload.matching_fields)
        if not isinstance(fields, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="matching_fields must be a valid JSON array")

    rule = DuplicateRule(**payload.model_dump(exclude_unset=True))
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=DuplicateRuleOut)
async def get_duplicate_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(DuplicateRule).where(DuplicateRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Duplicate rule not found")
    return rule


@router.put("/{rule_id}", response_model=DuplicateRuleOut)
async def update_duplicate_rule(
    rule_id: str,
    payload: DuplicateRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(DuplicateRule).where(DuplicateRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Duplicate rule not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "matching_fields" in update_data:
        try:
            fields = json.loads(update_data["matching_fields"])
            if not isinstance(fields, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="matching_fields must be a valid JSON array")

    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_duplicate_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(DuplicateRule).where(DuplicateRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Duplicate rule not found")
    await db.delete(rule)
    await db.commit()


# ── Duplicate Checking & Merging ────────────────────────────────────

@router.post("/check", response_model=DuplicateCheckResponse)
async def check_duplicates_endpoint(
    payload: DuplicateCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Check a record for duplicates."""
    matches = await check_duplicates(db, payload.object_type, payload.record_data)
    return DuplicateCheckResponse(
        has_duplicates=len(matches) > 0,
        matches=[DuplicateMatch(**m) for m in matches],
    )


@router.post("/merge")
async def merge_duplicates(
    payload: MergeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    """Merge two duplicate records."""
    try:
        result = await merge_records(db, payload.object_type, payload.master_id, payload.slave_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result