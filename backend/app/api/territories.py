from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.territory import Territory, TerritoryMember, TerritoryAccount, TerritoryProduct
from app.models.auth import User
from app.models.crm import Account, Opportunity, Product, Stage
from app.schemas.territory import (
    TerritoryCreate, TerritoryUpdate, TerritoryOut, TerritoryTreeNode,
    TerritoryMemberOut, TerritoryMemberCreate,
    TerritoryAccountOut, TerritoryAccountCreate,
    TerritoryProductOut, TerritoryProductCreate, TerritoryProductUpdate,
)
from app.schemas.crm import StageOut, PipelineOut, PipelineStageData, OpportunityOut
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/territories", tags=["territories"])


# ── Helpers ──────────────────────────────────────────────────────────

async def _build_tree(territories: list[Territory], parent_id: str | None = None) -> list[TerritoryTreeNode]:
    """Build tree from flat list of territories."""
    nodes = []
    for t in territories:
        if t.parent_id == parent_id:
            children = await _build_tree(territories, t.id)
            nodes.append(TerritoryTreeNode(
                id=t.id, name=t.name, code=t.code,
                territory_type=t.territory_type or "region",
                parent_id=t.parent_id, children=children,
            ))
    return nodes


def _make_territory_out(t: Territory, children: list = None,
                        member_count: int = 0, account_count: int = 0, product_count: int = 0):
    """Build TerritoryOut without triggering async lazy loading on children."""
    data = {c.name: getattr(t, c.name) for c in t.__table__.columns}
    return TerritoryOut(
        **data,
        children=children or [],
        member_count=member_count,
        account_count=account_count,
        product_count=product_count,
    )


# ── CRUD ─────────────────────────────────────────────────────────────

@router.get("", response_model=dict)
async def list_territories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    count_query = select(func.count(Territory.id))
    query = select(Territory).options(selectinload(Territory.children)).order_by(Territory.name)

    if search:
        search_filter = Territory.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    territories = result.scalars().all()

    # Count members and accounts per territory
    out = []
    for t in territories:
        member_count = await db.scalar(
            select(func.count(TerritoryMember.id)).where(TerritoryMember.territory_id == t.id)
        )
        account_count = await db.scalar(
            select(func.count(TerritoryAccount.id)).where(TerritoryAccount.territory_id == t.id)
        )
        product_count = await db.scalar(
            select(func.count(TerritoryProduct.id)).where(TerritoryProduct.territory_id == t.id)
        )
        children = [_make_territory_out(c) for c in (t.children or [])]
        out.append(_make_territory_out(t, children=children,
                                       member_count=member_count or 0,
                                       account_count=account_count or 0,
                                       product_count=product_count or 0))
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": out,
    }


@router.get("/tree", response_model=list[TerritoryTreeNode])
async def get_territory_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Territory).order_by(Territory.name))
    territories = result.scalars().all()
    return await _build_tree(territories)


@router.post("", response_model=TerritoryOut, status_code=status.HTTP_201_CREATED)
async def create_territory(
    payload: TerritoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Validate parent exists if provided
    if payload.parent_id:
        parent = await db.get(Territory, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent territory not found")

    territory = Territory(**payload.model_dump(exclude_unset=True))
    db.add(territory)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A territory with this code already exists",
        )
    await db.refresh(territory)
    return TerritoryOut(
        **{c.name: getattr(territory, c.name) for c in territory.__table__.columns},
        children=[], member_count=0, account_count=0, product_count=0,
    )


@router.get("/{territory_id}", response_model=TerritoryOut)
async def get_territory(
    territory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Territory)
        .options(selectinload(Territory.children))
        .where(Territory.id == territory_id)
    )
    territory = result.scalar_one_or_none()
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    member_count = await db.scalar(
        select(func.count(TerritoryMember.id)).where(TerritoryMember.territory_id == territory_id)
    )
    account_count = await db.scalar(
        select(func.count(TerritoryAccount.id)).where(TerritoryAccount.territory_id == territory_id)
    )
    product_count = await db.scalar(
        select(func.count(TerritoryProduct.id)).where(TerritoryProduct.territory_id == territory_id)
    )

    return _make_territory_out(
        territory,
        children=[_make_territory_out(c) for c in territory.children],
        member_count=member_count or 0,
        account_count=account_count or 0,
        product_count=product_count or 0,
    )


@router.put("/{territory_id}", response_model=TerritoryOut)
async def update_territory(
    territory_id: str,
    payload: TerritoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(
        select(Territory).options(selectinload(Territory.children)).where(Territory.id == territory_id)
    )
    territory = result.scalar_one_or_none()
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"] is not None:
        if update_data["parent_id"] == territory_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot set self as parent")
        parent = await db.get(Territory, update_data["parent_id"])
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent territory not found")

    for field, value in update_data.items():
        setattr(territory, field, value)

    # Build a plain dict BEFORE commit to avoid ORM lazy loading issues
    data = {c.name: getattr(territory, c.name) for c in Territory.__table__.columns}

    # Load related data before commit
    member_count = await db.scalar(
        select(func.count(TerritoryMember.id)).where(TerritoryMember.territory_id == territory_id)
    )
    account_count = await db.scalar(
        select(func.count(TerritoryAccount.id)).where(TerritoryAccount.territory_id == territory_id)
    )
    product_count = await db.scalar(
        select(func.count(TerritoryProduct.id)).where(TerritoryProduct.territory_id == territory_id)
    )

    await db.commit()

    return TerritoryOut(
        **data,
        children=[],
        member_count=member_count or 0,
        account_count=account_count or 0,
        product_count=product_count or 0,
    )


@router.delete("/{territory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_territory(
    territory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Territory).where(Territory.id == territory_id))
    territory = result.scalar_one_or_none()
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")
    await db.delete(territory)
    await db.commit()


# ── Members ──────────────────────────────────────────────────────────

@router.get("/{territory_id}/members", response_model=list[TerritoryMemberOut])
async def list_members(
    territory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    # Verify territory exists
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    result = await db.execute(
        select(TerritoryMember).where(TerritoryMember.territory_id == territory_id)
    )
    members = result.scalars().all()

    out = []
    for m in members:
        user = await db.get(User, m.user_id)
        out.append(TerritoryMemberOut(
            id=m.id, territory_id=m.territory_id, user_id=m.user_id,
            role=m.role, assigned_at=m.assigned_at,
            username=user.username if user else None,
            display_name=user.display_name if user else None,
        ))
    return out


@router.post("/{territory_id}/members", response_model=TerritoryMemberOut, status_code=status.HTTP_201_CREATED)
async def add_member(
    territory_id: str,
    payload: TerritoryMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    user = await db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    # Check for duplicate
    existing = await db.execute(
        select(TerritoryMember).where(
            TerritoryMember.territory_id == territory_id,
            TerritoryMember.user_id == payload.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member already exists")

    member = TerritoryMember(territory_id=territory_id, user_id=payload.user_id, role=payload.role)
    db.add(member)
    await db.commit()
    await db.refresh(member)

    # Send system notification
    await create_notification(
        db,
        user_id=payload.user_id,
        title="区域分配",
        message=f"您已被分配到区域「{territory.name}」",
        reference_type="territory",
        reference_id=territory_id,
    )

    return TerritoryMemberOut(
        id=member.id, territory_id=member.territory_id, user_id=member.user_id,
        role=member.role, assigned_at=member.assigned_at,
        username=user.username, display_name=user.display_name,
    )


@router.delete("/{territory_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    territory_id: str,
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(TerritoryMember).where(
            TerritoryMember.id == member_id,
            TerritoryMember.territory_id == territory_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    await db.delete(member)
    await db.commit()


# ── Accounts ─────────────────────────────────────────────────────────

@router.get("/{territory_id}/accounts", response_model=list[TerritoryAccountOut])
async def list_territory_accounts(
    territory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    result = await db.execute(
        select(TerritoryAccount).where(TerritoryAccount.territory_id == territory_id)
    )
    items = result.scalars().all()

    out = []
    for item in items:
        account = await db.get(Account, item.account_id)
        out.append(TerritoryAccountOut(
            id=item.id, territory_id=item.territory_id, account_id=item.account_id,
            assigned_at=item.assigned_at,
            account_name=account.name if account else None,
        ))
    return out


@router.post("/{territory_id}/accounts", response_model=TerritoryAccountOut, status_code=status.HTTP_201_CREATED)
async def add_territory_account(
    territory_id: str,
    payload: TerritoryAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    account = await db.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not found")

    existing = await db.execute(
        select(TerritoryAccount).where(
            TerritoryAccount.territory_id == territory_id,
            TerritoryAccount.account_id == payload.account_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already assigned to this territory")

    ta = TerritoryAccount(territory_id=territory_id, account_id=payload.account_id)
    db.add(ta)
    await db.commit()
    await db.refresh(ta)
    return TerritoryAccountOut(
        id=ta.id, territory_id=ta.territory_id, account_id=ta.account_id,
        assigned_at=ta.assigned_at, account_name=account.name,
    )


@router.delete("/{territory_id}/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_territory_account(
    territory_id: str,
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(TerritoryAccount).where(
            TerritoryAccount.territory_id == territory_id,
            TerritoryAccount.account_id == account_id,
        )
    )
    ta = result.scalar_one_or_none()
    if not ta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account assignment not found")
    await db.delete(ta)
    await db.commit()


# ── Products ─────────────────────────────────────────────────────────

@router.get("/{territory_id}/products", response_model=list[TerritoryProductOut])
async def list_territory_products(
    territory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    result = await db.execute(
        select(TerritoryProduct).where(TerritoryProduct.territory_id == territory_id)
    )
    items = result.scalars().all()

    out = []
    for item in items:
        product = await db.get(Product, item.product_id)
        out.append(TerritoryProductOut(
            id=item.id, territory_id=item.territory_id, product_id=item.product_id,
            price=float(item.price) if item.price else None,
            is_active=item.is_active,
            product_name=product.name if product else None,
            product_code=product.product_code if product else None,
            default_price=float(product.price) if product and product.price else None,
        ))
    return out


@router.post("/{territory_id}/products", response_model=TerritoryProductOut, status_code=status.HTTP_201_CREATED)
async def add_territory_product(
    territory_id: str,
    payload: TerritoryProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    product = await db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found")

    existing = await db.execute(
        select(TerritoryProduct).where(
            TerritoryProduct.territory_id == territory_id,
            TerritoryProduct.product_id == payload.product_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already assigned to this territory")

    tp = TerritoryProduct(
        territory_id=territory_id, product_id=payload.product_id,
        price=payload.price,
    )
    db.add(tp)
    await db.commit()
    await db.refresh(tp)
    return TerritoryProductOut(
        id=tp.id, territory_id=tp.territory_id, product_id=tp.product_id,
        price=float(tp.price) if tp.price else None,
        is_active=tp.is_active,
        product_name=product.name, product_code=product.product_code,
        default_price=float(product.price) if product.price else None,
    )


@router.put("/{territory_id}/products/{product_id}", response_model=TerritoryProductOut)
async def update_territory_product(
    territory_id: str,
    product_id: str,
    payload: TerritoryProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(
        select(TerritoryProduct).where(
            TerritoryProduct.territory_id == territory_id,
            TerritoryProduct.product_id == product_id,
        )
    )
    tp = result.scalar_one_or_none()
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product assignment not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tp, field, value)

    await db.commit()
    await db.refresh(tp)

    product = await db.get(Product, tp.product_id)
    return TerritoryProductOut(
        id=tp.id, territory_id=tp.territory_id, product_id=tp.product_id,
        price=float(tp.price) if tp.price else None,
        is_active=tp.is_active,
        product_name=product.name if product else None,
        product_code=product.product_code if product else None,
        default_price=float(product.price) if product and product.price else None,
    )


@router.delete("/{territory_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_territory_product(
    territory_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(
        select(TerritoryProduct).where(
            TerritoryProduct.territory_id == territory_id,
            TerritoryProduct.product_id == product_id,
        )
    )
    tp = result.scalar_one_or_none()
    if not tp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product assignment not found")
    await db.delete(tp)
    await db.commit()


# ── Pipeline (opportunities in this territory) ───────────────────────

@router.get("/{territory_id}/pipeline", response_model=PipelineOut)
async def get_territory_pipeline(
    territory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    territory = await db.get(Territory, territory_id)
    if not territory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")

    # Get account IDs for this territory
    acct_result = await db.execute(
        select(TerritoryAccount.account_id).where(TerritoryAccount.territory_id == territory_id)
    )
    account_ids = [r for r in acct_result.scalars().all()]

    if not account_ids:
        # Get stages for empty pipeline
        stages_result = await db.execute(select(Stage).order_by(Stage.sort_order))
        stages = stages_result.scalars().all()
        return PipelineOut(stages=[
            PipelineStageData(
                stage=StageOut.model_validate(s), opportunities=[], total_amount=0, count=0
            ) for s in stages
        ])

    stages_result = await db.execute(select(Stage).order_by(Stage.sort_order))
    stages = stages_result.scalars().all()

    pipeline_stages = []
    for stage in stages:
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Opportunity)
            .options(selectinload(Opportunity.line_items))
            .where(Opportunity.stage_id == stage.id, Opportunity.account_id.in_(account_ids))
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
