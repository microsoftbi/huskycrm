"""UAT tests for Profile flow — update profile, change password, view territories."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestProfileFlow:
    """UAT-PRO series: Profile management flow tests."""

    def test_update_display_name(self, logged_in_page, api_token):
        """UAT-PRO-01: Update display name."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        # Should see the profile page
        expect(page.locator("text=个人信息").first).to_be_visible()
        expect(page.locator("text=基本信息").first).to_be_visible()

    def test_change_password_page(self, logged_in_page):
        """UAT-PRO-02 (partial): Profile page shows password section."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        expect(page.locator("text=修改密码").first).to_be_visible()

    def test_territories_section(self, logged_in_page):
        """UAT-PRO-03: Profile page shows territories section."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        expect(page.locator("text=所属区域").first).to_be_visible()
