from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables. Alembic migrations will be used in production."""
    from app.models.auth import User  # noqa: F401
    from app.models.crm import Account, Contact, Stage, Opportunity, Product, OpportunityProduct  # noqa: F401
    from app.models.custom_object import CustomObjectDef, CustomFieldDef  # noqa: F401
    from app.models.workflow import WorkflowRule, WorkflowAction, WorkflowExecutionLog  # noqa: F401
    from app.models.report import Report, Dashboard, DashboardComponent  # noqa: F401
    from app.models.territory import Territory, TerritoryMember, TerritoryAccount, TerritoryProduct  # noqa: F401
    from app.models.event import Event, Task  # noqa: F401
    from app.models.profile import Profile  # noqa: F401
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.notification import Notification  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_default_profiles()

    # Attach audit listeners to all models
    from app.services.audit_service import setup_audit_listeners, attach_listeners
    setup_audit_listeners()
    for model_cls in [
        User, Account, Contact, Opportunity, Product, Event, Task,
        Territory, TerritoryMember, TerritoryAccount, TerritoryProduct,
        CustomObjectDef, CustomFieldDef,
        WorkflowRule, WorkflowAction,
        Report, Dashboard, DashboardComponent,
        Notification,
    ]:
        attach_listeners(model_cls)


# The three system profiles, mirroring the Salesforce profile concept.
# profile_type drives require_permission(): admin (all), standard (CRUD),
# readonly (read only).
DEFAULT_PROFILES = [
    {
        "name": "System Administrator",
        "profile_type": "admin",
        "description": "全量系统权限 + 数据权限（View All / Modify All）",
        "is_system": True,
    },
    {
        "name": "Standard User",
        "profile_type": "standard",
        "description": "基础销售 CRUD 权限（无删除）",
        "is_system": True,
    },
    {
        "name": "Read Only",
        "profile_type": "readonly",
        "description": "仅查询，无编辑/删除权限",
        "is_system": True,
    },
]


async def seed_default_profiles():
    """Ensure the three system profiles exist (idempotent)."""
    from sqlalchemy import select
    from app.models.profile import Profile

    async with async_session() as session:
        result = await session.execute(select(Profile).where(Profile.is_system.is_(True)))
        existing = {p.name for p in result.scalars().all()}
        changed = False
        for spec in DEFAULT_PROFILES:
            if spec["name"] in existing:
                continue
            session.add(Profile(**spec))
            changed = True
        if changed:
            await session.commit()
