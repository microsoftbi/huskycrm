"""UAT tests for login/register/logout flow."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"

fake = Faker()


class TestLoginFlow:
    """UAT-LOGIN series: Login flow tests."""

    def test_login_success(self, page, registered_user):
        """UAT-LOGIN-01: Normal login flow."""
        user = registered_user
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        page.fill("[placeholder='请输入用户名']", user["username"])
        page.fill("[placeholder='请输入密码']", user["password"])
        page.click("button:has-text('登录')")

        # Verify redirected to dashboard
        page.wait_for_url(f"{BASE_URL}/")
        expect(page.get_by_role("heading", name="仪表盘")).to_be_visible()
        expect(page.locator("text=SPSF CRM").first).to_be_visible()

    def test_wrong_password(self, page, registered_user):
        """UAT-LOGIN-02: Wrong password shows error."""
        user = registered_user
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        page.fill("[placeholder='请输入用户名']", user["username"])
        page.fill("[placeholder='请输入密码']", "wrongpassword")
        page.click("button:has-text('登录')")

        # Verify we stay on login page (no redirect)
        page.wait_for_timeout(1000)
        expect(page).to_have_url(f"{BASE_URL}/login")

    def test_register_and_auto_login(self, page):
        """UAT-LOGIN-03: Register via UI and auto-login."""
        username = fake.user_name()
        email = fake.email()
        password = "test123"

        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        # Switch to register tab
        page.click(".el-tabs__item:has-text('注册')")
        page.wait_for_timeout(500)

        # Use last() to get the visible form fields (the login tab fields are hidden)
        page.locator("[placeholder='请输入用户名']").last.fill(username)
        page.locator("[placeholder='请输入邮箱']").fill(email)
        page.locator("[placeholder='请输入密码']").last.fill(password)
        page.click("button:has-text('注册')")

        # Should auto-login and redirect to dashboard
        page.wait_for_url(f"{BASE_URL}/")
        expect(page.get_by_role("heading", name="仪表盘")).to_be_visible()

    def test_logout(self, logged_in_page):
        """UAT-LOGIN-04: Logout redirects to login page."""
        page = logged_in_page

        # Click user avatar dropdown
        page.click(".sf-user-info")
        page.wait_for_timeout(300)

        # Click logout
        page.click(".el-dropdown-menu__item:has-text('退出登录')")
        page.wait_for_timeout(500)

        # Verify redirected to login
        expect(page).to_have_url(f"{BASE_URL}/login")
        expect(page.locator("button:has-text('登录')")).to_be_visible()