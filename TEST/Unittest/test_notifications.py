import pytest
from app.models.notification import Notification
from app.services.audit_service import attach_listeners

# Attach listeners for notification model used in tests
attach_listeners(Notification)


@pytest.mark.asyncio
async def test_create_notification(db_session):
    from app.services.notification_service import create_notification
    notif = await create_notification(
        db_session,
        user_id="test_user",
        title="Test Notification",
        message="This is a test",
        notification_type="system",
    )
    assert notif.id is not None
    assert notif.title == "Test Notification"
    assert notif.is_read is False


@pytest.mark.asyncio
async def test_unread_count(db_session):
    from app.services.notification_service import create_notification
    await create_notification(db_session, user_id="user_a", title="N1")
    await create_notification(db_session, user_id="user_a", title="N2")
    await create_notification(db_session, user_id="user_b", title="N3")

    # Mark one as read
    from sqlalchemy import select
    result = await db_session.execute(
        select(Notification).where(Notification.user_id == "user_a")
    )
    notifs = result.scalars().all()
    notifs[0].is_read = True
    await db_session.commit()

    # Check unread count for user_a
    from sqlalchemy import select, func
    result = await db_session.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == "user_a",
            Notification.is_read == False,
        )
    )
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_mark_all_read(db_session):
    from app.services.notification_service import create_notification
    for i in range(3):
        await create_notification(db_session, user_id="user_c", title=f"Notification {i}")

    from sqlalchemy import update as sa_update, select, func
    await db_session.execute(
        sa_update(Notification)
        .where(Notification.user_id == "user_c", Notification.is_read == False)
        .values(is_read=True)
    )
    await db_session.commit()

    result = await db_session.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == "user_c",
            Notification.is_read == False,
        )
    )
    assert result.scalar() == 0