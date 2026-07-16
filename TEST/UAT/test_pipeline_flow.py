"""UAT tests for Opportunity and Pipeline Kanban flow."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


def _seed_stages_if_needed():
    """Ensure stages exist (seeded by backend on startup)."""
    pass


class TestPipelineFlow:
    """UAT-OPP series: Opportunity and Pipeline flow tests."""

    def test_pipeline_board_displays(self, logged_in_page, api_token):
        """UAT-OPP-02: Pipeline board shows stages and opportunities."""
        # Create a few opportunities via API
        stages_resp = requests.get(f"{API_URL}/opportunities/stages", headers={
            "Authorization": f"Bearer {api_token}",
        })
        stages = stages_resp.json()
        if stages:
            stage_id = stages[0]["id"]
            requests.post(f"{API_URL}/opportunities", headers={
                "Authorization": f"Bearer {api_token}",
            }, json={"name": fake.catch_phrase(), "stage_id": stage_id, "amount": 50000})

        page = logged_in_page
        page.goto(f"{BASE_URL}/opportunities/pipeline")
        page.wait_for_load_state("networkidle")

        # Should see column headers for stages
        expect(page.locator("text=初步接触").first).to_be_visible()
        expect(page.locator("text=需求分析").first).to_be_visible()
        expect(page.locator("text=赢单").first).to_be_visible()
        expect(page.locator("text=输单").first).to_be_visible()

    def test_pipeline_summary_stats(self, logged_in_page):
        """UAT-OPP-04: Pipeline shows summary statistics."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/opportunities/pipeline")
        page.wait_for_load_state("networkidle")

        # Should see summary cards
        expect(page.locator("text=管道总额").first).to_be_visible()
        expect(page.locator("text=机会总数").first).to_be_visible()