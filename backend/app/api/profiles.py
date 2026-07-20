from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.auth import User
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileOut, ProfileBrief, ProfileUserBrief
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("", response_model=list[ProfileOut])
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Profile).order_by(Profile.name))
    profiles = result.scalars().all()

    out = []
    for p in profiles:
        user_count = await db.scalar(
            select(func.count(User.id)).where(User.profile_id == p.id)
        )
        out.append(ProfileOut(
            id=p.id, name=p.name, profile_type=p.profile_type,
            description=p.description, is_system=p.is_system,
            user_count=user_count or 0,
            created_at=p.created_at, updated_at=p.updated_at,
        ))
    return out


@router.get("/brief", response_model=list[ProfileBrief])
async def list_profiles_brief(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """轻量级列表 — 无需特殊权限（用于下拉选择）"""
    result = await db.execute(select(Profile).order_by(Profile.name))
    return result.scalars().all()


@router.post("", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    # Only superusers can create profiles
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create profiles")

    # Check for duplicate name
    existing = await db.execute(select(Profile).where(Profile.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile name already exists")

    profile = Profile(**payload.model_dump(exclude_unset=True))
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return ProfileOut(
        id=profile.id, name=profile.name, profile_type=profile.profile_type,
        description=profile.description, is_system=profile.is_system,
        user_count=0, created_at=profile.created_at, updated_at=profile.updated_at,
    )


@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    user_count = await db.scalar(
        select(func.count(User.id)).where(User.profile_id == profile_id)
    )
    users_result = await db.execute(
        select(User).where(User.profile_id == profile_id).order_by(User.username)
    )
    users = [
        ProfileUserBrief(
            id=u.id, username=u.username, display_name=u.display_name,
            email=u.email, is_active=u.is_active,
        )
        for u in users_result.scalars().all()
    ]
    return ProfileOut(
        id=profile.id, name=profile.name, profile_type=profile.profile_type,
        description=profile.description, is_system=profile.is_system,
        user_count=user_count or 0, users=users,
        created_at=profile.created_at, updated_at=profile.updated_at,
    )


@router.put("/{profile_id}", response_model=ProfileOut)
async def update_profile(
    profile_id: str,
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update profiles")

    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    # Prevent changing profile_type of system profiles
    if profile.is_system and payload.profile_type is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change profile type of system profiles")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    user_count = await db.scalar(
        select(func.count(User.id)).where(User.profile_id == profile_id)
    )
    return ProfileOut(
        id=profile.id, name=profile.name, profile_type=profile.profile_type,
        description=profile.description, is_system=profile.is_system,
        user_count=user_count or 0,
        created_at=profile.created_at, updated_at=profile.updated_at,
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("delete")),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete profiles")

    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if profile.is_system:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete system profiles")

    # Check if any users are assigned to this profile
    user_count = await db.scalar(
        select(func.count(User.id)).where(User.profile_id == profile_id)
    )
    if user_count and user_count > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete profile with {user_count} assigned users")

    await db.delete(profile)
    await db.commit()