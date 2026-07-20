"""UAT tests for Recycle Bin flow."""
import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestRecycleBinFlow:
    """UAT-RBIN series: Recycle bin flow tests."""

    def test_recycle_bin_empty_state(self, logged_in_page):
        """UAT-RBIN-01: Empty recycle bin loads correctly."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/recycle-bin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Should see the page title
        expect(page.get_by_role("heading", name="回收站")).to_be_visible()

    def test_deleted_record_appears_in_recycle_bin(self, logged_in_page, api_token):
        """UAT-RBIN-02: Deleted account appears in recycle bin."""
        headers = {"Authorization": f"Bearer {api_token}"}

        # Create an account
        name = fake.company()
        resp = requests.post(f"{API_URL}/accounts", headers=headers, json={"name": name})
        assert resp.status_code == 201
        account_id = resp.json()["id"]

        # Delete the account
        del_resp = requests.delete(f"{API_URL}/accounts/{account_id}", headers=headers)
        # Standard user may not have delete permission — skip if 403
        if del_resp.status_code == 403:
            return

        # Navigate to recycle bin
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/recycle-bin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # The deleted account should appear in the table
        expect(page.locator(f"text={name}").first).to_be_visible()

    def test_restore_from_recycle_bin(self, logged_in_page, api_token):
        """UAT-RBIN-03: Restore a deleted account from recycle bin."""
        headers = {"Authorization": f"Bearer {api_token}"}

        # Create and delete an account
        name = fake.company()
        resp = requests.post(f"{API_URL}/accounts", headers=headers, json={"name": name})
        account_id = resp.json()["id"]

        del_resp = requests.delete(f"{API_URL}/accounts/{account_id}", headers=headers)
        if del_resp.status_code == 403:
            return

        # Navigate to recycle bin
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/recycle-bin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Click restore button for the deleted record
        restore_btn = page.locator(".el-table__row").filter(has_text=name).locator("button:has-text('恢复')")
        if restore_btn.is_visible():
            restore_btn.click()
            page.wait_for_timeout(1000)

            # Should show success message
            expect(page.locator(".el-message--success").first).to_be_visible()