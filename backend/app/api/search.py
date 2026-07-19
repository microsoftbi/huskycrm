from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.auth import User
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.search_service import search_all

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search(
    q: str = Query("", min_length=1, max_length=255),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Unified search across all objects."""
    return await search_all(db, q, limit)