"""UAT tests for Campaign management flow — create, list, and member management."""
import pytest
from playwright.sync_api import Page, expect
import requests
import time

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000/api"


class TestCampaignFlow:
    """活动管理流程 UAT 测试"""

    def test_create_campaign(self, logged_in_page: Page, api_token: str):
        """UAT-CAMP-01: 新建活动"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/campaigns/new")
        page.wait_for_load_state("networkidle")

        # Fill form using Element Plus form-item labels
        page.locator(".el-form-item").filter(has_text="活动名称").locator("input").fill("春季促销活动")

        # Set budget (el-input-number)
        page.locator(".el-form-item").filter(has_text="预算").locator("input").fill("100000")

        # Save
        page.click("button:has-text('保存')")
        page.wait_for_timeout(2000)

        # Should show success message
        expect(page.locator(".el-message--success")).to_be_visible()

    def test_campaign_list_and_search(self, logged_in_page: Page, api_token: str):
        """UAT-CAMP-02: 活动列表与搜索"""
        # Create a unique campaign via API for search testing
        uid = str(int(time.time() * 1000))[-6:]
        unique_name = f"夏季促销_{uid}"
        headers = {"Authorization": f"Bearer {api_token}"}
        resp = requests.post(f"{API_URL}/campaigns", headers=headers, json={"name": unique_name})
        assert resp.status_code == 201, f"Create campaign failed: {resp.text}"

        page = logged_in_page
        page.goto(f"{BASE_URL}/campaigns")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Search for the unique campaign
        search_input = page.locator("input[placeholder*='搜索活动']")
        search_input.fill(unique_name)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)

        # Should show only the matching campaign
        expect(page.locator(".el-table__row")).to_have_count(1)