"""UAT tests for Territory management flow — create, hierarchy, and members."""
import pytest
from playwright.sync_api import Page, expect
import requests

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000/api"


class TestTerritoryFlow:
    """销售区域流程 UAT 测试"""

    def test_create_territory(self, logged_in_page: Page, api_token: str):
        """UAT-TERR-01: 新建区域"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/territories")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Click new territory button
        page.click("button:has-text('新建区域')")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Fill form using Element Plus form-item labels
        page.locator(".el-form-item").filter(has_text="名称").locator("input").fill("华东大区")
        page.locator(".el-form-item").filter(has_text="编码").locator("input").fill("HD-001")

        # Save
        page.click("button:has-text('保存')")
        page.wait_for_timeout(2000)

        # Should navigate to list and show success message
        expect(page.locator(".el-message--success")).to_be_visible()

    def test_territory_tree(self, logged_in_page: Page, api_token: str):
        """UAT-TERR-02: 区域树形结构"""
        # Create parent and child territories via API
        headers = {"Authorization": f"Bearer {api_token}"}
        parent = requests.post(f"{API_URL}/territories", headers=headers, json={"name": "中国市场"})
        pid = parent.json()["id"]
        requests.post(f"{API_URL}/territories", headers=headers, json={
            "name": "华东区域", "parent_id": pid,
        })
        requests.post(f"{API_URL}/territories", headers=headers, json={
            "name": "华北区域", "parent_id": pid,
        })

        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/territories")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Verify tree shows the parent node
        expect(page.locator("text=中国市场").first).to_be_visible()

    def test_territory_members(self, logged_in_page: Page, api_token: str):
        """UAT-TERR-03: 区域成员管理"""
        # Create a territory via API
        headers = {"Authorization": f"Bearer {api_token}"}
        terr = requests.post(f"{API_URL}/territories", headers=headers, json={"name": "测试区域"})
        assert terr.status_code == 201
        tid = terr.json()["id"]

        # Add a member via API (the UI doesn't have a detail page route)
        # First, get the current user's info to find a valid user_id
        resp = requests.get(f"{API_URL}/auth/me", headers=headers)
        user_id = resp.json()["id"]
        member_resp = requests.post(f"{API_URL}/territories/{tid}/members", headers=headers, json={
            "user_id": user_id, "role": "manager",
        })
        assert member_resp.status_code == 201, f"Add member failed: {member_resp.text}"

        # Verify by listing members
        list_resp = requests.get(f"{API_URL}/territories/{tid}/members", headers=headers)
        assert list_resp.status_code == 200
        members = list_resp.json()
        assert len(members) == 1
        assert members[0]["user_id"] == user_id
        assert members[0]["role"] == "manager"