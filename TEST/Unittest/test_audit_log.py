import pytest
from app.models.audit_log import AuditLog
from app.models.crm import Account
from app.models.auth import User
from app.services.audit_service import current_user_id, attach_listeners

# Attach audit listeners for models used in these tests
attach_listeners(Account)
attach_listeners(User)


@pytest.mark.asyncio
async def test_audit_log_created_on_account_create(db_session):
    """Verify an audit log entry is created when a new account is inserted."""
    token = current_user_id.set("test_user")
    try:
        account = Account(name="Test Account", industry="Tech")
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
    finally:
        current_user_id.reset(token)

    from sqlalchemy import select
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.object_type == "Account",
            AuditLog.object_id == account.id,
        )
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    create_log = [l for l in logs if l.action == "create"]
    assert len(create_log) == 1
    assert create_log[0].user_id == "test_user"


@pytest.mark.asyncio
async def test_audit_log_recorded_on_update(db_session):
    token = current_user_id.set("test_user")
    try:
        account = Account(name="Original", industry="Tech")
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        account.name = "Updated"
        await db_session.commit()
    finally:
        current_user_id.reset(token)

    from sqlalchemy import select
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.object_type == "Account",
            AuditLog.object_id == account.id,
            AuditLog.action == "update",
        )
    )
    logs = result.scalars().all()
    name_updates = [l for l in logs if l.field_name == "name"]
    assert len(name_updates) >= 1
    assert "Original" in name_updates[0].old_value
    assert "Updated" in name_updates[0].new_value


@pytest.mark.asyncio
async def test_audit_log_excludes_password(db_session):
    """Verify password_hash field is excluded from audit logging."""
    from app.models.auth import User
    from app.core.security import hash_password

    token = current_user_id.set("test_user")
    try:
        user = User(
            username="audit_test_user",
            email="audit_test@example.com",
            password_hash=hash_password("secret123"),
            display_name="Audit Test",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        user.display_name = "Updated Name"
        await db_session.commit()
    finally:
        current_user_id.reset(token)

    from sqlalchemy import select
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.object_type == "User",
            AuditLog.object_id == user.id,
        )
    )
    logs = result.scalars().all()
    password_logs = [l for l in logs if l.field_name == "password_hash"]
    assert len(password_logs) == 0


@pytest.mark.asyncio
async def test_audit_log_system_user_fallback(db_session):
    """When no user context is set, log should use 'system'."""
    account = Account(name="System Test")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    from sqlalchemy import select
    result = await db_session.execute(
        select(AuditLog).where(
            AuditLog.object_type == "Account",
            AuditLog.object_id == account.id,
            AuditLog.action == "create",
        )
    )
    log = result.scalar_one_or_none()
    assert log is not None
    assert log.user_id == "system"