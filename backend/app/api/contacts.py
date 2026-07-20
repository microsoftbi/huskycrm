from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.crm import Contact, Account, ContactAccount
from app.models.auth import User
from app.schemas.crm import (
    ContactCreate, ContactUpdate, ContactOut,
    ContactAccountOut, ContactAccountCreate,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def _populate_accounts(contact: Contact) -> dict:
    """Convert Contact to dict with account_name and accounts list."""
    data = ContactOut.model_validate(contact).model_dump()
    if contact.account:
        data["account_name"] = contact.account.name
    data["accounts"] = [
        ContactAccountOut(
            id=assoc.id,
            contact_id=assoc.contact_id,
            account_id=assoc.account_id,
            account_name=assoc.account.name if assoc.account else None,
            assigned_at=assoc.assigned_at,
        )
        for assoc in (contact.account_associations or [])
    ]
    return data


@router.get("", response_model=dict)
async def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=255),
    account_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    query = select(Contact).options(
        selectinload(Contact.account),
        selectinload(Contact.account_associations).selectinload(ContactAccount.account),
    ).where(Contact.is_deleted == False)
    count_query = select(func.count(Contact.id)).where(Contact.is_deleted == False)

    if search:
        search_filter = (
            Contact.first_name.ilike(f"%{search}%")
            | Contact.last_name.ilike(f"%{search}%")
            | Contact.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if account_id is not None:
        query = query.where(Contact.account_id == account_id)
        count_query = count_query.where(Contact.account_id == account_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Contact.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_populate_accounts(c) for c in items],
    }


@router.post("", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    contact = Contact(**payload.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactOut)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(
        select(Contact)
        .options(
            selectinload(Contact.account),
            selectinload(Contact.account_associations).selectinload(ContactAccount.account),
        )
        .where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return _populate_accounts(contact)


@router.put("/{contact_id}", response_model=ContactOut)
async def update_contact(
    contact_id: str,
    payload: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    result = await db.execute(
        select(Contact)
        .options(
            selectinload(Contact.account),
            selectinload(Contact.account_associations).selectinload(ContactAccount.account),
        )
        .where(Contact.id == contact_id, Contact.is_deleted == False)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    await db.refresh(contact, ["account", "account_associations"])
    for assoc in contact.account_associations:
        await db.refresh(assoc, ["account"])
    return _populate_accounts(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    contact.is_deleted = True
    contact.deleted_at = datetime.now()
    await db.commit()


# ── Contact-Account Associations ─────────────────────────────────────

@router.get("/{contact_id}/accounts", response_model=list[ContactAccountOut])
async def list_contact_accounts(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """List all accounts associated with a contact."""
    contact_result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False))
    contact = contact_result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    result = await db.execute(
        select(ContactAccount)
        .options(selectinload(ContactAccount.account))
        .where(ContactAccount.contact_id == contact_id)
    )
    associations = result.scalars().all()

    return [
        ContactAccountOut(
            id=assoc.id,
            contact_id=assoc.contact_id,
            account_id=assoc.account_id,
            account_name=assoc.account.name if assoc.account else None,
            assigned_at=assoc.assigned_at,
        )
        for assoc in associations
    ]


@router.post("/{contact_id}/accounts", response_model=ContactAccountOut, status_code=status.HTTP_201_CREATED)
async def add_contact_account(
    contact_id: str,
    payload: ContactAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    """Associate an account with a contact."""
    contact_result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.is_deleted == False))
    contact = contact_result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    account_result = await db.execute(select(Account).where(Account.id == payload.account_id))
    account = account_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    existing = await db.execute(
        select(ContactAccount).where(
            ContactAccount.contact_id == contact_id,
            ContactAccount.account_id == payload.account_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already associated with this contact")

    association = ContactAccount(contact_id=contact_id, account_id=payload.account_id)
    db.add(association)
    await db.commit()
    await db.refresh(association)
    await db.refresh(association, ["account"])

    return ContactAccountOut(
        id=association.id,
        contact_id=association.contact_id,
        account_id=association.account_id,
        account_name=association.account.name if association.account else None,
        assigned_at=association.assigned_at,
    )


@router.delete("/{contact_id}/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact_account(
    contact_id: str,
    account_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    """Remove an account association from a contact."""
    result = await db.execute(
        select(ContactAccount).where(
            ContactAccount.contact_id == contact_id,
            ContactAccount.account_id == account_id,
        )
    )
    association = result.scalar_one_or_none()
    if not association:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")

    await db.delete(association)
    await db.commit()