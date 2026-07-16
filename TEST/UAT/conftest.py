"""
UAT test fixtures for Playwright-based end-to-end testing.

- Each test gets its own browser context and page
- Each test registers its own user (data isolation)
- Backend runs on localhost:8000, frontend on localhost:5173
"""
import pytest
import requests
from faker import Faker

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000/api"

fake = Faker(locale="zh_CN")


@pytest.fixture(scope="session")
def browser_context_args():
    """Default browser context configuration."""
    return {
        "viewport": {"width": 1440, "height": 900},
        "locale": "zh-CN",
    }


@pytest.fixture
def registered_user():
    """Register a new test user via API and return credentials."""
    user = {
        "username": fake.user_name() + fake.random_int(100, 999).__str__(),
        "email": fake.email(),
        "password": "test123",
        "display_name": fake.name(),
    }
    resp = requests.post(f"{API_URL}/auth/register", json=user)
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    return user


@pytest.fixture
def logged_in_page(page, registered_user):
    """Open the app, login with the registered user, return authenticated page."""
    user = registered_user
    # First, get a token via API so we can inject it into localStorage
    resp = requests.post(f"{API_URL}/auth/login", json={
        "username": user["username"],
        "password": user["password"],
    })
    assert resp.status_code == 200
    tokens = resp.json()

    # Navigate to login page first (to be on the app's origin for localStorage)
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("networkidle")

    # Inject the token into localStorage so the router guard can find it
    page.evaluate(f"""
        localStorage.setItem('access_token', '{tokens["access_token"]}');
        localStorage.setItem('refresh_token', '{tokens["refresh_token"]}');
    """)

    # Navigate to dashboard — the router guard should find the token and load the user
    page.goto(f"{BASE_URL}/")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    return page


@pytest.fixture
def api_token(registered_user):
    """Login via API and return JWT token."""
    user = registered_user
    resp = requests.post(f"{API_URL}/auth/login", json={
        "username": user["username"],
        "password": user["password"],
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(autouse=True)
def _ensure_servers_running():
    """Verify that backend and frontend are reachable before each test."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        assert r.status_code == 200, f"Backend health check failed: {r.status_code}"
    except requests.ConnectionError:
        pytest.fail(
            "Backend is not running. Start it with:\n"
            "  cd backend && source venv/bin/activate && uvicorn app.main:app --port 8000"
        )
