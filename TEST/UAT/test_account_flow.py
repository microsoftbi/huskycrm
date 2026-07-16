"""UAT tests for Account CRUD flow."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestAccountFlow:
    """UAT-ACC series: Account management flow tests."""

    def test_account_list_shows_empty_state(self, logged_in_page):
        """UAT-ACC-01 (partial): Verify account list loads."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/accounts")
        page.wait_for_load_state("networkidle")

        # Should see the page title
        expect(page.get_by_role("heading", name="账户")).to_be_visible()

    def test_create_account_full(self, logged_in_page):
        """UAT-ACC-02: Create account with all fields."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/accounts/new")
        page.wait_for_load_state("networkidle")

        name = fake.company()
        industry = fake.random_element(["Technology", "Finance", "Healthcare", "Education"])
        phone = fake.phone_number()
        email = fake.company_email()
        website = fake.url()

        # Fill the form
        page.fill("[placeholder='请输入账户名称']", name)
        page.fill("[placeholder='请输入行业']", industry)
        page.fill("[placeholder='请输入电话']", phone)
        page.fill("[placeholder='请输入邮箱']", email)
        page.fill("[placeholder='https://']", website)

        # Click save
        page.click("button:has-text('保存')")

        # Wait for redirect to detail page
        page.wait_for_load_state("networkidle")

        # Verify the detail page shows our data
        expect(page.locator(f"text={name}").first).to_be_visible()
        expect(page.locator(f"text={industry}").first).to_be_visible()

    def test_edit_account(self, logged_in_page, api_token):
        """UAT-ACC-03: Edit an existing account."""
        # Create account via API first
        name = fake.company()
        resp = requests.post(f"{API_URL}/accounts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": name, "industry": "Technology"})
        account_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/accounts/{account_id}/edit")
        page.wait_for_load_state("networkidle")

        # Modify fields
        new_name = fake.company()
        new_industry = "Finance"
        page.fill("[placeholder='请输入账户名称']", "")
        page.fill("[placeholder='请输入账户名称']", new_name)
        page.fill("[placeholder='请输入行业']", "")
        page.fill("[placeholder='请输入行业']", new_industry)

        page.click("button:has-text('保存')")
        page.wait_for_load_state("networkidle")

        # Verify changes
        expect(page.locator(f"text={new_name}").first).to_be_visible()

    def test_delete_account(self, logged_in_page, api_token):
        """UAT-ACC-04: Delete an account."""
        # Create account via API
        name = fake.company()
        resp = requests.post(f"{API_URL}/accounts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": name})
        account_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/accounts/{account_id}")
        page.wait_for_load_state("networkidle")

        # Click delete button
        page.click("button:has-text('删除')")

        # Confirm in dialog
        page.wait_for_timeout(300)
        page.click(".el-message-box .el-button--primary")
        page.wait_for_load_state("networkidle")

        # Should redirect to list
        expect(page).to_have_url(f"{BASE_URL}/accounts")

    def test_search_account(self, logged_in_page, api_token):
        """UAT-ACC-05: Search accounts."""
        # Create a uniquely named account via API
        unique_name = f"ZzTest{fake.random_int(10000,99999)}"
        requests.post(f"{API_URL}/accounts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": unique_name})

        page = logged_in_page
        page.goto(f"{BASE_URL}/accounts")
        page.wait_for_load_state("networkidle")

        # Type search query
        page.fill("[placeholder='搜索账户名称...']", unique_name)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1000)

        # Verify the result appears in the table
        expect(page.locator(f"text={unique_name}").first).to_be_visible()

    def test_empty_submit_shows_error(self, logged_in_page):
        """UAT-ACC-06: Submit empty form shows validation error."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/accounts/new")
        page.wait_for_load_state("networkidle")

        # Click save without filling name
        page.click("button:has-text('保存')")
        page.wait_for_timeout(500)

        # Should see validation error (Element Plus form error)
        expect(page.locator(".el-form-item__error")).to_be_visible()