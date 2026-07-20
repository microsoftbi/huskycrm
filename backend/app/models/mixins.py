"""
Soft-delete mixin for models that support recycle bin functionality.
"""
from sqlalchemy import Column, Boolean, DateTime, func, text


class SoftDeleteMixin:
    """Add is_deleted and deleted_at columns for soft-delete support."""

    is_deleted = Column(Boolean, default=False, server_default=text("0"), index=True)
    deleted_at = Column(DateTime, nullable=True, default=None)