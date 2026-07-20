from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.crm import Account
from app.models.territory import TerritoryAccount, Territory
from app.models.auth import User
from app.schemas.crm import AccountCreate, AccountUpdate, AccountOut
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=dict)
async def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(Account).where(Account.is_deleted == False)
    count_query = select(func.count(Account.id)).where(Account.is_deleted == False)

    if search:
        search_filter = Account.name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Account.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [AccountOut.model_validate(a).model_dump() for a in items],
    }


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    account = Account(**payload.model_dump(exclude_unset=True))
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.is_deleted == False))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: str,
    payload: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.is_deleted == False))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, field, value)

    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.is_deleted == False))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    account.is_deleted = True
    account.deleted_at = datetime.now()
    await db.commit()


# ── Territories ──────────────────────────────────────────────────────

@router.get("/{account_id}/territories", response_model=list[dict])
async def list_account_territories(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """List all territories associated with an account."""
    account_result = await db.execute(select(Account).where(Account.id == account_id, Account.is_deleted == False))
    if not account_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    result = await db.execute(
        select(TerritoryAccount, Territory.name, Territory.code)
        .join(Territory, TerritoryAccount.territory_id == Territory.id)
        .where(TerritoryAccount.account_id == account_id)
    )
    rows = result.all()

    return [
        {
            "id": row[0].id,
            "territory_id": row[0].territory_id,
            "account_id": row[0].account_id,
            "territory_name": row[1],
            "territory_code": row[2],
            "assigned_at": row[0].assigned_at,
        }
        for row in rows
    ]