"""
Notification service — helper functions for creating notifications.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: str,
    title: str,
    message: str | None = None,
    notification_type: str = "system",
    reference_type: str | None = None,
    reference_id: str | None = None,
) -> Notification:
    """Create a notification for a user."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification