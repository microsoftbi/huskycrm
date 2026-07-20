from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db, async_session
from app.models.crm import Opportunity, Stage, OpportunityProduct
from app.models.auth import User
from app.schemas.crm import (
    OpportunityCreate, OpportunityUpdate, OpportunityOut,
    StageOut, PipelineOut, PipelineStageData,
    OpportunityProductCreate, OpportunityProductOut,
)
from app.models.crm import Product as ProductModel
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.validation_service import validate_record


async def ensure_stages_seeded():
    """Auto-seed stages if the table is empty (self-healing)."""
    async with async_session() as session:
        result = await session.execute(select(Stage).limit(1))
        if result.scalar_one_or_none():
            return
        stages = [
            Stage(name="初步接触", probability=10, sort_order=1),
            Stage(name="需求分析", probability=30, sort_order=2),
            Stage(name="方案制定", probability=50, sort_order=3),
            Stage(name="商务谈判", probability=70, sort_order=4),
            Stage(name="合同签订", probability=90, sort_order=5),
            Stage(name="赢单", probability=100, sort_order=6, is_closed_won=True),
            Stage(name="输单", probability=0, sort_order=7, is_closed_lost=True),
        ]
        session.add_all(stages)
        await session.commit()

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


# ── Stages ─────────────────────────────────────────────────────────

@router.get("/stages", response_model=list[StageOut])
async def list_stages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    await ensure_stages_seeded()
    result = await db.execute(select(Stage).order_by(Stage.sort_order))
    return result.scalars().all()


# ── Pipeline (Kanban data) ─────────────────────────────────────────

@router.get("/pipeline", response_model=PipelineOut)
async def get_pipeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    stages_result = await db.execute(select(Stage).order_by(Stage.sort_order))
    stages = stages_result.scalars().all()

    pipeline_stages = []
    for stage in stages:
        result = await db.execute(
            select(Opportunity)
            .options(selectinload(Opportunity.line_items))
            .where(Opportunity.stage_id == stage.id, Opportunity.is_deleted == False)
        )
        opps = result.scalars().all()
        total_amount = sum((o.amount or 0) for o in opps)
        pipeline_stages.append(PipelineStageData(
            stage=StageOut.model_validate(stage),
            opportunities=[OpportunityOut.model_validate(o) for o in opps],
            total_amount=total_amount,
            count=len(opps),
        ))

    return PipelineOut(stages=pipeline_stages)


# ── CRUD ───────────────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    stage_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(Opportunity).options(selectinload(Opportunity.line_items)).where(Opportunity.is_deleted == False)
    count_query = select(func.count(Opportunity.id)).where(Opportunity.is_deleted == False)

    if search:
        search_filter = Opportunity.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if stage_id is not None:
        query = query.where(Opportunity.stage_id == stage_id)
        count_query = count_query.where(Opportunity.stage_id == stage_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Opportunity.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [OpportunityOut.model_validate(o).model_dump() for o in items],
    }


@router.post("", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    payload: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Validate against active validation rules
    errors = await validate_record(db, "opportunity", payload.model_dump(exclude_unset=True))
    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})

    # Validate stage exists
    stage = await db.execute(select(Stage).where(Stage.id == payload.stage_id))
    if not stage.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stage not found")

    opp = Opportunity(**payload.model_dump(exclude_unset=True))
    db.add(opp)
    await db.commit()
    # Re-fetch with line_items to avoid lazy loading issue in async mode
    result = await db.execute(
        select(Opportunity)
        .options(selectinload(Opportunity.line_items))
        .where(Opportunity.id == opp.id)
    )
    return result.scalar_one()


@router.get("/{opportunity_id}", response_model=OpportunityOut)
async def get_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Opportunity)
        .options(selectinload(Opportunity.line_items))
        .where(Opportunity.id == opportunity_id, Opportunity.is_deleted == False)
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opp


@router.put("/{opportunity_id}", response_model=OpportunityOut)
async def update_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id, Opportunity.is_deleted == False))
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    update_data = payload.model_dump(exclude_unset=True)
    # Validate against active validation rules
    if update_data:
        errors = await validate_record(db, "opportunity", update_data)
        if errors:
            raise HTTPException(status_code=422, detail={"validation_errors": errors})
    if "stage_id" in update_data:
        stage = await db.execute(select(Stage).where(Stage.id == update_data["stage_id"]))
        if not stage.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stage not found")

    for field, value in update_data.items():
        setattr(opp, field, value)

    await db.commit()
    # Re-fetch with line_items
    result = await db.execute(
        select(Opportunity)
        .options(selectinload(Opportunity.line_items))
        .where(Opportunity.id == opportunity_id)
    )
    return result.scalar_one()


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id, Opportunity.is_deleted == False))
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    opp.is_deleted = True
    opp.deleted_at = datetime.now()
    await db.commit()


# ── Line Items (Opportunity Products) ──────────────────────────────

@router.get("/{opportunity_id}/line-items", response_model=list[OpportunityProductOut])
async def list_line_items(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(OpportunityProduct).where(OpportunityProduct.opportunity_id == opportunity_id)
    )
    return result.scalars().all()


@router.post("/{opportunity_id}/line-items", response_model=OpportunityProductOut, status_code=status.HTTP_201_CREATED)
async def add_line_item(
    opportunity_id: str,
    payload: OpportunityProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Verify opportunity exists
    opp_result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
    if not opp_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    # Verify product exists
    prod_result = await db.execute(select(ProductModel).where(ProductModel.id == payload.product_id))
    prod = prod_result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found")

    total_price = payload.quantity * payload.unit_price
    item = OpportunityProduct(
        opportunity_id=opportunity_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_price=total_price,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{opportunity_id}/line-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_line_item(
    opportunity_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(OpportunityProduct).where(
            OpportunityProduct.id == item_id,
            OpportunityProduct.opportunity_id == opportunity_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line item not found")
    await db.delete(item)
    await db.commit()
