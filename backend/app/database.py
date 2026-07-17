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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
