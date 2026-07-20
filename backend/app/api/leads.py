"""
Leads API — CRUD, conversion, Web-to-Lead, and assignment rules.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.auth import User
from app.models.lead import Lead, LeadAssignmentRule
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadOut,
    ConvertLeadRequest, ConvertLeadResponse,
    LeadAssignmentRuleCreate, LeadAssignmentRuleUpdate, LeadAssignmentRuleOut,
    WebToLeadRequest, WebToLeadResponse,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.lead_service import apply_assignment_rules, convert_lead

router = APIRouter(prefix="/api/leads", tags=["leads"])


# ── Lead CRUD ────────────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    status_filter: str = Query("", max_length=50),
    source_filter: str = Query("", max_length=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(Lead).where(Lead.is_deleted == False)
    count_query = select(func.count(Lead.id)).where(Lead.is_deleted == False)

    if search:
        search_filter = (
            Lead.first_name.ilike(f"%{search}%")
            | Lead.last_name.ilike(f"%{search}%")
            | Lead.company.ilike(f"%{search}%")
            | Lead.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if status_filter:
        query = query.where(Lead.status == status_filter)
        count_query = count_query.where(Lead.status == status_filter)

    if source_filter:
        query = query.where(Lead.source == source_filter)
        count_query = count_query.where(Lead.source == source_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Lead.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [LeadOut.model_validate(l).model_dump() for l in items],
    }


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    lead_data = payload.model_dump(exclude_unset=True)

    # Apply assignment rules if no owner specified
    if not lead_data.get("owner_id"):
        assigned_user = await apply_assignment_rules(db, lead_data)
        if assigned_user:
            lead_data["owner_id"] = assigned_user

    lead = Lead(**lead_data)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.is_deleted == False))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    lead.is_deleted = True
    await db.commit()


# ── Lead Conversion ──────────────────────────────────────────────────

@router.post("/{lead_id}/convert", response_model=ConvertLeadResponse)
async def convert_lead_endpoint(
    lead_id: str,
    payload: ConvertLeadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    try:
        response = await convert_lead(
            db, lead,
            account_name=payload.account_name,
            account_id=payload.account_id,
            create_opportunity=payload.create_opportunity,
            opportunity_name=payload.opportunity_name,
            opportunity_amount=payload.opportunity_amount,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return response


# ── Web-to-Lead (no auth required) ───────────────────────────────────

@router.post("/web-to-lead", response_model=WebToLeadResponse)
async def web_to_lead(
    payload: WebToLeadRequest,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — create lead from web form (no auth required)."""
    try:
        lead_data = payload.model_dump()
        assigned_user = await apply_assignment_rules(db, lead_data)
        if assigned_user:
            lead_data["owner_id"] = assigned_user

        lead = Lead(**lead_data)
        db.add(lead)
        await db.commit()
        await db.refresh(lead)

        return WebToLeadResponse(
            success=True,
            lead_id=lead.id,
            message="Lead created successfully",
        )
    except Exception as e:
        return WebToLeadResponse(
            success=False,
            lead_id=None,
            message=f"Failed to create lead: {str(e)}",
        )


@router.get("/web-to-lead/form")
async def get_web_to_lead_form(
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Generate HTML form snippet for Web-to-Lead."""
    html = '''
<form action="/api/leads/web-to-lead" method="POST" style="max-width: 400px; font-family: sans-serif;">
  <h3>获取报价 / 联系我们</h3>
  <input type="text" name="first_name" placeholder="名 *" required style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #ddd; border-radius:3px;">
  <input type="text" name="last_name" placeholder="姓 *" required style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #ddd; border-radius:3px;">
  <input type="text" name="company" placeholder="公司 *" required style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #ddd; border-radius:3px;">
  <input type="email" name="email" placeholder="邮箱" style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #ddd; border-radius:3px;">
  <input type="tel" name="phone" placeholder="电话" style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #ddd; border-radius:3px;">
  <textarea name="description" placeholder="备注" style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #ddd; border-radius:3px; min-height:80px;"></textarea>
  <button type="submit" style="width:100%; padding:10px; background:#1589ee; color:#fff; border:none; border-radius:3px; cursor:pointer;">提交</button>
</form>
'''
    return {"html": html}


# ── Lead Assignment Rules ────────────────────────────────────────────

@router.get("/assignment-rules", response_model=dict)
async def list_assignment_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(LeadAssignmentRule).order_by(LeadAssignmentRule.priority.desc())
    count_query = select(func.count(LeadAssignmentRule.id))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    enriched = []
    for rule in items:
        name = rule.assign_to_user.display_name if rule.assign_to_user else rule.assign_to_user_id
        enriched.append(LeadAssignmentRuleOut(
            id=rule.id,
            name=rule.name,
            is_active=rule.is_active,
            condition_expression=rule.condition_expression,
            assign_to_user_id=rule.assign_to_user_id,
            assign_to_user_name=name,
            priority=rule.priority,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        ))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [r.model_dump() for r in enriched],
    }


@router.post("/assignment-rules", response_model=LeadAssignmentRuleOut, status_code=status.HTTP_201_CREATED)
async def create_assignment_rule(
    payload: LeadAssignmentRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    try:
        conds = json.loads(payload.condition_expression)
        if not isinstance(conds, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="condition_expression must be a valid JSON array")

    rule = LeadAssignmentRule(**payload.model_dump(exclude_unset=True))
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.put("/assignment-rules/{rule_id}", response_model=LeadAssignmentRuleOut)
async def update_assignment_rule(
    rule_id: str,
    payload: LeadAssignmentRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(LeadAssignmentRule).where(LeadAssignmentRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment rule not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/assignment-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(LeadAssignmentRule).where(LeadAssignmentRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment rule not found")
    await db.delete(rule)
    await db.commit()