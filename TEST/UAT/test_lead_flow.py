"""UAT tests for Lead management flow — create, list, convert, and search."""
import pytest
from playwright.sync_api import Page, expect
import requests
import time

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000/api"


class TestLeadFlow:
    """线索管理流程 UAT 测试"""

    def test_create_lead(self, logged_in_page: Page, api_token: str):
        """UAT-LEAD-01: 新建线索"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/leads/new")
        page.wait_for_load_state("networkidle")

        # Fill form using Element Plus form-item labels
        page.locator(".el-form-item").filter(has_text="名").locator("input").fill("张")
        page.locator(".el-form-item").filter(has_text="姓").locator("input").fill("三")
        page.locator(".el-form-item").filter(has_text="公司").locator("input").fill("测试科技有限公司")
        page.locator(".el-form-item").filter(has_text="邮箱").locator("input").fill("zhangsan@test.com")
        page.locator(".el-form-item").filter(has_text="电话").locator("input").fill("13800138000")

        # Save
        page.click("button:has-text('保存')")
        page.wait_for_timeout(2000)

        # Should navigate to list page and show success message
        expect(page.locator(".el-message--success")).to_be_visible()

    def test_lead_list_and_search(self, logged_in_page: Page, api_token: str):
        """UAT-LEAD-02: 查看线索列表并搜索"""
        # Create a unique lead via API for search testing
        uid = str(int(time.time() * 1000))[-6:]
        unique_company = f"搜索公司_{uid}"
        headers = {"Authorization": f"Bearer {api_token}"}
        resp = requests.post(f"{API_URL}/leads", headers=headers, json={
            "first_name": "李", "last_name": "四", "company": unique_company,
        })
        assert resp.status_code == 201, f"Create lead failed: {resp.text}"

        page = logged_in_page
        page.goto(f"{BASE_URL}/leads")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Verify table has at least 1 row (data exists)
        expect(page.locator(".el-table__row").first).to_be_visible()

        # Search for the unique lead
        search_input = page.locator("input[placeholder*='搜索名称']")
        search_input.fill(unique_company)
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        # After search, should show only the matching lead
        expect(page.locator(".el-table__row")).to_have_count(1)

    def test_convert_lead(self, logged_in_page: Page, api_token: str):
        """UAT-LEAD-03: 线索转化"""
        # Create a lead via API
        headers = {"Authorization": f"Bearer {api_token}"}
        resp = requests.post(f"{API_URL}/leads", headers=headers, json={
            "first_name": "转", "last_name": "化", "company": "转化科技",
            "email": "zhuan@test.com",
        })
        assert resp.status_code == 201, f"Create lead failed: {resp.text}"
        lead_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/leads/{lead_id}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Click convert button
        page.click("button:has-text('转化')")
        page.wait_for_timeout(500)

        # Fill opportunity name and confirm
        page.fill("input[placeholder*='默认']", "转化商机")
        page.click("button:has-text('确认转化')")
        page.wait_for_timeout(1500)

        # Should show success message
        expect(page.locator(".el-message--success")).to_be_visible()

    def test_lead_filter_by_status(self, logged_in_page: Page, api_token: str):
        """UAT-LEAD-04: 按状态筛选线索"""
        # Create a unique lead with a specific status for filter testing
        uid = str(int(time.time() * 1000))[-6:]
        unique_company = f"筛选公司_{uid}"
        headers = {"Authorization": f"Bearer {api_token}"}
        resp = requests.post(f"{API_URL}/leads", headers=headers, json={
            "first_name": "筛选", "last_name": "测试", "company": unique_company,
            "status": "Contacted",
        })
        assert resp.status_code == 201, f"Create lead failed: {resp.text}"

        page = logged_in_page
        page.goto(f"{BASE_URL}/leads")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Click the status filter select and pick "已联系"
        page.locator(".el-select").first.click()
        page.wait_for_timeout(500)
        page.click("text=已联系")
        page.wait_for_timeout(1000)

        # Should show at least 1 Contacted lead
        expect(page.locator(".el-table__row").first).to_be_visible()