"""
Campaigns API — CRUD for campaigns, member management, ROI analysis.
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.auth import User
from app.models.crm import Contact, Opportunity
from app.models.campaign import Campaign, CampaignMember
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignOut, CampaignDetailOut,
    CampaignMemberCreate, CampaignMemberUpdate, CampaignMemberOut,
    ROIResponse,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


# ── Campaign CRUD ───────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    status_filter: str = Query("", max_length=50),
    type_filter: str = Query("", max_length=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(Campaign).where(Campaign.is_deleted == False)
    count_query = select(func.count(Campaign.id)).where(Campaign.is_deleted == False)

    if search:
        search_filter = Campaign.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if status_filter:
        query = query.where(Campaign.status == status_filter)
        count_query = count_query.where(Campaign.status == status_filter)

    if type_filter:
        query = query.where(Campaign.type == type_filter)
        count_query = count_query.where(Campaign.type == type_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Campaign.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    enriched = []
    for c in items:
        enriched.append(await _enrich_campaign(db, c))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": enriched,
    }


@router.post("", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    campaign = Campaign(**payload.model_dump(exclude_unset=True))
    campaign.owner_id = current_user.id
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return await _enrich_campaign(db, campaign)


@router.get("/{campaign_id}", response_model=CampaignDetailOut)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.members))
        .where(Campaign.id == campaign_id, Campaign.is_deleted == False)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    base = await _enrich_campaign(db, campaign)
    return CampaignDetailOut(
        **base.model_dump(),
        members=[CampaignMemberOut.model_validate(m) for m in campaign.members],
    )


@router.put("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: str,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.is_deleted == False))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)
    return await _enrich_campaign(db, campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.is_deleted == False))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    campaign.is_deleted = True
    await db.commit()


# ── Campaign Members ────────────────────────────────────────────────

@router.get("/{campaign_id}/members", response_model=list[CampaignMemberOut])
async def list_campaign_members(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(CampaignMember)
        .options(selectinload(CampaignMember.contact))
        .where(CampaignMember.campaign_id == campaign_id)
        .order_by(CampaignMember.created_at.desc())
    )
    members = result.scalars().all()
    return [_enrich_member(m) for m in members]


@router.post("/{campaign_id}/members", response_model=CampaignMemberOut, status_code=status.HTTP_201_CREATED)
async def add_campaign_member(
    campaign_id: str,
    payload: CampaignMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Verify campaign exists
    campaign = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    if not campaign.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    member = CampaignMember(campaign_id=campaign_id, **payload.model_dump(exclude_unset=True))
    db.add(member)
    await db.commit()
    await db.refresh(member)

    # Load contact for enrichment
    result = await db.execute(
        select(CampaignMember)
        .options(selectinload(CampaignMember.contact))
        .where(CampaignMember.id == member.id)
    )
    return _enrich_member(result.scalar_one())


@router.put("/{campaign_id}/members/{member_id}", response_model=CampaignMemberOut)
async def update_campaign_member(
    campaign_id: str,
    member_id: str,
    payload: CampaignMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(
        select(CampaignMember)
        .options(selectinload(CampaignMember.contact))
        .where(CampaignMember.id == member_id, CampaignMember.campaign_id == campaign_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign member not found")

    if payload.status is not None:
        member.status = payload.status

    await db.commit()
    await db.refresh(member)
    return _enrich_member(member)


@router.delete("/{campaign_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign_member(
    campaign_id: str,
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(CampaignMember).where(
            CampaignMember.id == member_id,
            CampaignMember.campaign_id == campaign_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign member not found")
    await db.delete(member)
    await db.commit()


# ── ROI Analysis ─────────────────────────────────────────────────────

@router.get("/{campaign_id}/roi", response_model=ROIResponse)
async def get_campaign_roi(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

    # Count members
    member_result = await db.execute(
        select(func.count(CampaignMember.id)).where(CampaignMember.campaign_id == campaign_id)
    )
    member_count = member_result.scalar() or 0

    # Count converted opportunities linked to campaign members' contacts
    # For simplicity, query opportunities linked to campaign contacts
    converted_query = select(func.count(Opportunity.id), func.coalesce(func.sum(Opportunity.amount), 0))
    # Get contacts from this campaign
    contact_ids_result = await db.execute(
        select(CampaignMember.contact_id).where(
            CampaignMember.campaign_id == campaign_id,
            CampaignMember.contact_id.isnot(None),
        )
    )
    contact_ids = [row[0] for row in contact_ids_result.fetchall()]

    converted_opportunities = 0
    converted_amount = 0.0

    if contact_ids:
        # Find opportunities linked to these contacts
        opp_result = await db.execute(
            select(Opportunity).where(
                Opportunity.account_id.in_(
                    select(Contact.account_id).where(Contact.id.in_(contact_ids))
                )
            )
        )
        opps = opp_result.scalars().all()
        converted_opportunities = len(opps)
        converted_amount = sum((o.amount or 0) for o in opps)

    # Calculate ROI
    roi = None
    roi_label = "N/A"
    if campaign.actual_cost and campaign.actual_cost > 0:
        roi = ((converted_amount - campaign.actual_cost) / campaign.actual_cost) * 100
        if roi > 500:
            roi_label = "优秀"
        elif roi > 200:
            roi_label = "良好"
        elif roi > 0:
            roi_label = "一般"
        else:
            roi_label = "亏损"

    return ROIResponse(
        budget=campaign.budget,
        actual_cost=campaign.actual_cost,
        member_count=member_count,
        converted_opportunities=converted_opportunities,
        converted_amount=converted_amount,
        roi=round(roi, 2) if roi is not None else None,
        roi_label=roi_label,
    )


# ── Helpers ──────────────────────────────────────────────────────────

async def _enrich_campaign(db: AsyncSession, campaign: Campaign) -> CampaignOut:
    """Enrich a campaign with member count and ROI data."""
    member_result = await db.execute(
        select(func.count(CampaignMember.id)).where(CampaignMember.campaign_id == campaign.id)
    )
    member_count = member_result.scalar() or 0

    # Get contact IDs from members
    contact_ids_result = await db.execute(
        select(CampaignMember.contact_id).where(
            CampaignMember.campaign_id == campaign.id,
            CampaignMember.contact_id.isnot(None),
        )
    )
    contact_ids = [row[0] for row in contact_ids_result.fetchall()]

    converted_opportunities = 0
    converted_amount = 0.0

    if contact_ids:
        opp_result = await db.execute(
            select(Opportunity).where(
                Opportunity.account_id.in_(
                    select(Contact.account_id).where(Contact.id.in_(contact_ids))
                )
            )
        )
        opps = opp_result.scalars().all()
        converted_opportunities = len(opps)
        converted_amount = sum((o.amount or 0) for o in opps)

    roi = None
    if campaign.actual_cost and campaign.actual_cost > 0:
        roi = round(((converted_amount - campaign.actual_cost) / campaign.actual_cost) * 100, 2)

    return CampaignOut(
        id=campaign.id,
        name=campaign.name,
        type=campaign.type,
        status=campaign.status,
        budget=campaign.budget,
        actual_cost=campaign.actual_cost,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        description=campaign.description,
        owner_id=campaign.owner_id,
        member_count=member_count,
        converted_opportunities=converted_opportunities,
        converted_amount=converted_amount,
        roi=roi,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


def _enrich_member(member: CampaignMember) -> CampaignMemberOut:
    """Enrich a campaign member with contact info."""
    contact_name = None
    contact_email = None
    if member.contact:
        contact_name = f"{member.contact.first_name} {member.contact.last_name}"
        contact_email = member.contact.email

    return CampaignMemberOut(
        id=member.id,
        campaign_id=member.campaign_id,
        contact_id=member.contact_id,
        status=member.status,
        contact_name=contact_name,
        contact_email=contact_email,
        created_at=member.created_at,
    )