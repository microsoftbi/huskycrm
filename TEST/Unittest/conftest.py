"""
Test configuration and fixtures for SPSF CRM API tests.

Uses a separate in-memory SQLite database so tests don't touch the
development database. All tests run against the FastAPI test client.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, select

from app.database import engine, async_session, Base
from app.main import app
from app.config import settings
from app.models.crm import Stage

# Force in-memory SQLite for tests
settings.database_url = "sqlite+aiosqlite://"

# Default pipeline stages (normally seeded by the lifespan handler)
STAGES = [
    {"name": "初步接触", "probability": 10, "sort_order": 1},
    {"name": "需求分析", "probability": 30, "sort_order": 2},
    {"name": "方案制定", "probability": 50, "sort_order": 3},
    {"name": "商务谈判", "probability": 70, "sort_order": 4},
    {"name": "合同签订", "probability": 90, "sort_order": 5},
    {"name": "赢单", "probability": 100, "sort_order": 6, "is_closed_won": True},
    {"name": "输单", "probability": 0, "sort_order": 7, "is_closed_lost": True},
]


# ── Event loop ─────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Database ───────────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # Drop standard tables
        await conn.run_sync(Base.metadata.drop_all)
        # Also drop any dynamically created custom object tables (obj_*)
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'obj_%'")
        )
        rows = result.fetchall()
        for row in rows:
            await conn.execute(text(f"DROP TABLE IF EXISTS {row[0]}"))


async def _seed_stages():
    """Insert default pipeline stages directly into the DB."""
    async with async_session() as session:
        for s in STAGES:
            stage = Stage(
                name=s["name"],
                probability=s["probability"],
                sort_order=s["sort_order"],
                is_closed_won=s.get("is_closed_won", False),
                is_closed_lost=s.get("is_closed_lost", False),
            )
            session.add(stage)
        await session.commit()


@pytest_asyncio.fixture
async def seeded_stages():
    """Seed pipeline stages and return the list of stages with IDs."""
    async with async_session() as session:
        for s in STAGES:
            stage = Stage(
                name=s["name"],
                probability=s["probability"],
                sort_order=s["sort_order"],
                is_closed_won=s.get("is_closed_won", False),
                is_closed_lost=s.get("is_closed_lost", False),
            )
            session.add(stage)
        await session.commit()
    # Fetch back to get generated IDs
    async with async_session() as session:
        result = await session.execute(select(Stage).order_by(Stage.sort_order))
        return result.scalars().all()


# ── Test client ────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client():
    """Provide an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Auth helpers ──────────────────────────────────────────────────

@pytest_asyncio.fixture
async def user_token(client: AsyncClient) -> dict:
    """Register a test user and return access + refresh tokens."""
    resp = await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "display_name": "Test User",
    })
    assert resp.status_code == 201
    resp = await client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "token_type": data["token_type"],
    }


@pytest_asyncio.fixture
async def auth_headers(user_token: dict) -> dict:
    """Provide Authorization headers with a valid JWT."""
    return {"Authorization": f"Bearer {user_token['access_token']}"}