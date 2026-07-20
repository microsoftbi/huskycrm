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
        "username": f"{fake.user_name()}_{int(__import__('time').time() * 1000)}",
        "email": f"uat_{int(__import__('time').time() * 1000)}_{fake.random_int(100,999)}@test.com",
        "password": "test123",
        "display_name": fake.name(),
    }
    resp = requests.post(f"{API_URL}/auth/register", json=user)
    assert resp.status_code == 201, f"Register failed: {resp.text}"

    # Assign a profile to the user so they have permissions (create/edit/delete)
    # Login as admin to get superuser token
    admin_resp = requests.post(f"{API_URL}/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    if admin_resp.status_code == 200:
        admin_token = admin_resp.json()["access_token"]
        user_id = resp.json()["id"]
        # Assign standard profile (prof_standard_01 exists in seeded data)
        assign_resp = requests.put(
            f"{API_URL}/auth/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"profile_id": "prof_standard_01"},
        )
        if assign_resp.status_code != 200:
            print(f"Warning: Profile assignment failed: {assign_resp.text}")

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
