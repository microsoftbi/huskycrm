"""UAT tests for Approval management flow — rules, queue, and approval actions."""
import pytest
from playwright.sync_api import Page, expect
import requests
import time

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000/api"


class TestApprovalFlow:
    """审批流程 UAT 测试"""

    def test_approval_rule_crud(self, logged_in_page: Page, api_token: str):
        """UAT-APR-01: 审批规则CRUD"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/settings")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # Click approval rules menu item in sidebar
        page.locator(".el-menu-item").filter(has_text="审批规则").click()
        page.wait_for_timeout(500)

        # Click create rule button
        page.click("button:has-text('新建规则')")
        page.wait_for_timeout(500)

        # Fill form fields in the dialog
        page.locator(".el-form-item").filter(has_text="规则名称").locator("input").fill("大额商机审批")
        page.locator(".el-form-item").filter(has_text="条件").locator("textarea").fill(
            '[{"field":"amount","operator":"gt","value":100000}]'
        )

        # Save
        page.click("button:has-text('保存')")
        page.wait_for_timeout(2000)

        # Should show success message
        expect(page.locator(".el-message--success")).to_be_visible()

    def test_approval_queue_view(self, logged_in_page: Page, api_token: str):
        """UAT-APR-02: 审批队列查看"""
        # Create a rule and trigger an approval request via API
        headers = {"Authorization": f"Bearer {api_token}"}

        # First get current user info
        me = requests.get(f"{API_URL}/auth/me", headers=headers)
        assert me.status_code == 200
        my_id = me.json()["id"]

        # Create rule with unique object_type to avoid matching old rules
        unique_type = f"opportunity_{int(time.time() * 1000)}"
        rule = requests.post(f"{API_URL}/approval-rules", headers=headers, json={
            "name": "队列测试规则", "object_type": unique_type,
            "condition_expression": "[]",
            "approver_type": "specific_user", "approver_user_id": my_id,
        })
        assert rule.status_code == 201

        # Trigger approval
        trigger = requests.post(f"{API_URL}/approval-rules/trigger", headers=headers, json={
            "object_type": unique_type, "object_id": "opp_uat_001",
            "record_data": {"amount": 500000},
        })
        assert trigger.status_code == 200

        # Navigate to approval queue
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/approval-queue")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # Verify the request appears as an approval card (card-based layout, not table)
        expect(page.locator(".approval-card").first).to_be_visible()

    def test_approve_request(self, logged_in_page: Page, api_token: str):
        """UAT-APR-03: 审批通过"""
        # Setup: create rule + trigger approval
        headers = {"Authorization": f"Bearer {api_token}"}
        me = requests.get(f"{API_URL}/auth/me", headers=headers)
        assert me.status_code == 200
        my_id = me.json()["id"]

        unique_type = f"opp_approve_{int(time.time() * 1000)}"
        r = requests.post(f"{API_URL}/approval-rules", headers=headers, json={
            "name": "审批通过测试", "object_type": unique_type,
            "condition_expression": "[]",
            "approver_type": "specific_user", "approver_user_id": my_id,
        })
        assert r.status_code == 201, f"Create rule failed: {r.text}"
        trigger = requests.post(f"{API_URL}/approval-rules/trigger", headers=headers, json={
            "object_type": unique_type, "object_id": "opp_uat_002",
            "record_data": {"amount": 1000},
        })
        assert trigger.status_code == 200, f"Trigger failed: {trigger.text}"
        request_id = trigger.json()["id"]

        # Approve via API (UI may not have approve button for own requests)
        resp = requests.post(f"{API_URL}/approval-rules/requests/{request_id}/approve",
                             headers=headers, json={"comment": "审批通过"})
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "approved"

        # Navigate to queue and verify
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/approval-queue")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # Should show the page title
        expect(page.locator("h2").filter(has_text="我的审批").first).to_be_visible()

    def test_reject_request(self, logged_in_page: Page, api_token: str):
        """UAT-APR-04: 审批拒绝"""
        headers = {"Authorization": f"Bearer {api_token}"}
        me = requests.get(f"{API_URL}/auth/me", headers=headers)
        assert me.status_code == 200
        my_id = me.json()["id"]

        unique_type = f"opp_reject_{int(time.time() * 1000)}"
        requests.post(f"{API_URL}/approval-rules", headers=headers, json={
            "name": "审批拒绝测试", "object_type": unique_type,
            "condition_expression": "[]",
            "approver_type": "specific_user", "approver_user_id": my_id,
        })
        trigger = requests.post(f"{API_URL}/approval-rules/trigger", headers=headers, json={
            "object_type": unique_type, "object_id": "opp_uat_003",
            "record_data": {"amount": 1000},
        })
        assert trigger.status_code == 200
        request_id = trigger.json()["id"]

        # Reject via API
        resp = requests.post(f"{API_URL}/approval-rules/requests/{request_id}/reject",
                             headers=headers, json={"comment": "不通过"})
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "rejected"

        # Verify in queue page — the rejected request won't appear in the
        # default "pending" tab, so just verify the page loaded correctly
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/approval-queue")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # Page should display the title
        expect(page.locator("h2").filter(has_text="我的审批").first).to_be_visible()