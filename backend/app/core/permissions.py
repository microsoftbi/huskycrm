"""权限检查工具 — 基于 profile_type 的简化权限模型"""

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.auth import User
from app.core.deps import get_current_user

# 权限等级映射
# admin: 全部操作
# standard: read / create / edit (无 delete)
# readonly: 仅 read
PROFILE_PERMISSIONS = {
    "admin": {"read", "create", "edit", "delete"},
    "standard": {"read", "create", "edit"},
    "readonly": {"read"},
}


def require_permission(action: str):
    """返回 FastAPI 依赖，检查当前用户是否有权执行指定操作。

    Args:
        action: 'read' | 'create' | 'edit' | 'delete'

    用法:
        @router.get(...)
        async def list_accounts(
            ...,
            _: User = Depends(require_permission("read")),
            current_user: User = Depends(get_current_user),
        ):
    """
    async def checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        # 超级用户跳过所有检查
        if current_user.is_superuser:
            return current_user

        # 没有 profile — 按最严格处理（只读）
        if not current_user.profile_id:
            if action == "read":
                return current_user
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No profile assigned",
            )

        # 加载 profile 类型
        from app.models.profile import Profile
        result = await db.execute(
            select(Profile).where(Profile.id == current_user.profile_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profile not found",
            )

        allowed = PROFILE_PERMISSIONS.get(profile.profile_type, set())
        if action not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action}",
            )

        return current_user

    return checker