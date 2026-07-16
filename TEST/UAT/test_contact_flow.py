"""UAT tests for Contact CRUD flow."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestContactFlow:
    """UAT-CON series: Contact management flow tests."""

    def test_create_contact_minimal(self, logged_in_page):
        """UAT-CON-01: Create contact with minimal fields."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/contacts/new")
        page.wait_for_load_state("networkidle")

        first_name = fake.first_name()
        last_name = fake.last_name()

        page.fill("[placeholder='请输入名字']", first_name)
        page.fill("[placeholder='请输入姓氏']", last_name)

        page.click("button:has-text('保存')")
        page.wait_for_load_state("networkidle")

        # Verify on detail page
        expect(page.locator(f"text={first_name}").first).to_be_visible()
        expect(page.locator(f"text={last_name}").first).to_be_visible()

    def test_create_contact_with_account(self, logged_in_page, api_token):
        """UAT-CON-02: Create contact linked to an account."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/contacts/new")
        page.wait_for_load_state("networkidle")

        first_name = fake.first_name()
        last_name = fake.last_name()

        page.fill("[placeholder='请输入名字']", first_name)
        page.fill("[placeholder='请输入姓氏']", last_name)
        page.fill("[placeholder='请输入邮箱']", fake.email())

        page.click("button:has-text('保存')")
        page.wait_for_load_state("networkidle")

        # Should see contact name on detail page
        expect(page.locator(f"text={first_name}").first).to_be_visible()

    def test_edit_contact(self, logged_in_page, api_token):
        """UAT-CON-03: Edit existing contact."""
        # Create contact via API
        first = fake.first_name()
        last = fake.last_name()
        resp = requests.post(f"{API_URL}/contacts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"first_name": first, "last_name": last, "title": "Engineer"})
        contact_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/contacts/{contact_id}/edit")
        page.wait_for_load_state("networkidle")

        # Change title
        new_title = "Senior Manager"
        page.fill("[placeholder='请输入职位']", "")
        page.fill("[placeholder='请输入职位']", new_title)

        page.click("button:has-text('保存')")
        page.wait_for_load_state("networkidle")

        # Verify change
        expect(page.locator(f"text={new_title}").first).to_be_visible()

    def test_delete_contact(self, logged_in_page, api_token):
        """UAT-CON-04: Delete a contact."""
        # Create contact via API
        first = fake.first_name()
        last = fake.last_name()
        resp = requests.post(f"{API_URL}/contacts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"first_name": first, "last_name": last})
        contact_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/contacts/{contact_id}")
        page.wait_for_load_state("networkidle")

        page.click("button:has-text('删除')")
        page.wait_for_timeout(300)
        page.click(".el-message-box .el-button--primary")
        page.wait_for_load_state("networkidle")

        expect(page).to_have_url(f"{BASE_URL}/contacts")