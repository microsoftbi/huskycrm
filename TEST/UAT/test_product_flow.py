"""UAT tests for Product CRUD flow."""
import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestProductFlow:
    """UAT-PROD series: Product management flow tests."""

    def test_product_list_shows_empty_state(self, logged_in_page):
        """UAT-PROD-01: Verify product list loads."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/products")
        page.wait_for_load_state("networkidle")

        # Should see the page title
        expect(page.get_by_role("heading", name="产品")).to_be_visible()

    def test_create_product_full(self, logged_in_page):
        """UAT-PROD-02: Create product with all fields."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/products/new")
        page.wait_for_load_state("networkidle")

        name = fake.catch_phrase()
        code = f"PROD-{fake.random_int(1000, 9999)}"
        category = fake.random_element(["电子产品", "软件服务", "办公用品", "咨询服务"])
        price = fake.random_int(100, 99999)
        cost = fake.random_int(50, price - 1)
        description = fake.text(max_nb_chars=100)

        # Fill the form
        page.fill("[placeholder='请输入产品名称']", name)
        page.fill("[placeholder='请输入产品编码']", code)
        page.fill("[placeholder='请输入分类']", category)
        page.fill("[placeholder='产品描述']", description)

        # Set price — Element Plus input-number is a special component
        price_input = page.locator(".el-form-item").filter(has_text="售价").locator("input")
        price_input.click()
        price_input.fill(str(price))

        cost_input = page.locator(".el-form-item").filter(has_text="成本").locator("input")
        cost_input.click()
        cost_input.fill(str(cost))

        # Click save
        page.click("button:has-text('保存')")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Verify the detail page shows our data
        expect(page.locator(f"text={name}").first).to_be_visible()

    def test_edit_product(self, logged_in_page, api_token):
        """UAT-PROD-03: Edit an existing product."""
        name = fake.catch_phrase()
        resp = requests.post(f"{API_URL}/products", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": name, "price": 100, "category": "电子产品"})
        assert resp.status_code == 201
        product_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/products/{product_id}/edit")
        page.wait_for_load_state("networkidle")

        new_name = fake.catch_phrase()
        new_category = "软件服务"

        page.fill("[placeholder='请输入产品名称']", "")
        page.fill("[placeholder='请输入产品名称']", new_name)
        page.fill("[placeholder='请输入分类']", "")
        page.fill("[placeholder='请输入分类']", new_category)
        page.fill("[placeholder='产品描述']", "Updated description")

        page.click("button:has-text('保存')")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Verify changes
        expect(page.locator(f"text={new_name}").first).to_be_visible()

    def test_search_product(self, logged_in_page, api_token):
        """UAT-PROD-04: Search products."""
        unique_name = f"产品{fake.random_int(10000, 99999)}"
        requests.post(f"{API_URL}/products", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": unique_name, "price": 100})

        page = logged_in_page
        page.goto(f"{BASE_URL}/products")
        page.wait_for_load_state("networkidle")

        # Type search query
        page.fill("[placeholder='搜索产品名称...']", unique_name)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1000)

        # Verify the result appears in the table
        expect(page.locator(f"text={unique_name}").first).to_be_visible()

    def test_view_product_detail(self, logged_in_page, api_token):
        """UAT-PROD-05: View product detail page."""
        name = fake.catch_phrase()
        code = f"PROD-{fake.random_int(1000, 9999)}"
        category = "办公用品"
        resp = requests.post(f"{API_URL}/products", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": name, "product_code": code, "price": 5000, "category": category})
        assert resp.status_code == 201
        product_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/products/{product_id}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Verify product info is displayed
        expect(page.locator(f"text={name}").first).to_be_visible()
        expect(page.locator(f"text={code}").first).to_be_visible()