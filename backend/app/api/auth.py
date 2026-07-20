from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.auth import User
from app.models.profile import Profile
from app.models.territory import Territory, TerritoryMember
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, RefreshRequest, UserOut,
    ProfileUpdate, PasswordChange, UserTerritoryOut,
)
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, decode_token
)
from app.core.deps import get_current_user

async def _user_to_out(user: User, db: AsyncSession) -> UserOut:
    """Build UserOut with profile info."""
    data = {c.name: getattr(user, c.name) for c in user.__table__.columns}
    profile_name = None
    profile_type = None
    if user.profile_id:
        profile = await db.get(Profile, user.profile_id)
        if profile:
            profile_name = profile.name
            profile_type = profile.profile_type
    return UserOut(**data, profile_name=profile_name, profile_type=profile_type)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if username or email already exists
    result = await db.execute(
        select(User).where(
            (User.username == payload.username) | (User.email == payload.email)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name or payload.username,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return await _user_to_out(user, db)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.username == payload.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    token_data = decode_token(payload.refresh_token)
    if token_data is None or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user_id = token_data.get("sub")
    access_token = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.get("/me", response_model=UserOut)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _user_to_out(current_user, db)


@router.get("/users", response_model=dict)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar() or 0
    result = await db.execute(
        select(User).order_by(User.username).offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [await _user_to_out(u, db) for u in users],
    }


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only superusers can update other users
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update users")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return await _user_to_out(user, db)


@router.put("/profile", response_model=UserOut)
async def update_profile(
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Users cannot change their own profile_id
    update_data = payload.model_dump(exclude_unset=True, exclude={"profile_id"})
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return await _user_to_out(current_user, db)


@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")

    if len(payload.new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters")

    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}


@router.get("/my-territories", response_model=list[UserTerritoryOut])
async def get_my_territories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find all territory memberships for the current user
    result = await db.execute(
        select(TerritoryMember).where(TerritoryMember.user_id == current_user.id)
    )
    memberships = result.scalars().all()

    out = []
    for mem in memberships:
        territory = await db.get(Territory, mem.territory_id)
        if not territory:
            continue

        # Find the manager of this territory
        mgr_result = await db.execute(
            select(TerritoryMember).where(
                and_(
                    TerritoryMember.territory_id == mem.territory_id,
                    TerritoryMember.role == "manager",
                )
            )
        )
        mgr_member = mgr_result.scalar_one_or_none()
        manager_name = None
        manager_username = None
        if mgr_member:
            mgr_user = await db.get(User, mgr_member.user_id)
            if mgr_user:
                manager_name = mgr_user.display_name
                manager_username = mgr_user.username

        out.append(UserTerritoryOut(
            territory_id=territory.id,
            territory_name=territory.name,
            territory_code=territory.code,
            territory_type=territory.territory_type or "region",
            role=mem.role,
            manager_name=manager_name,
            manager_username=manager_username,
        ))

    return out
