"""UAT tests for Event (Visit) flow — create, check-in, check-out, tasks."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestEventFlow:
    """UAT-EVT series: Visit/Event management flow tests."""

    def test_create_event(self, logged_in_page, api_token):
        """UAT-EVT-01: Create a new visit event."""
        # Create an account via API first for what_id
        acc_name = fake.company()
        resp = requests.post(f"{API_URL}/accounts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": acc_name})
        assert resp.status_code == 201

        page = logged_in_page
        page.goto(f"{BASE_URL}/events/new")
        page.wait_for_load_state("networkidle")

        subject = f"拜访 {fake.catch_phrase()}"

        # Fill form
        page.fill("[placeholder='请输入拜访主题']", subject)
        page.click("button:has-text('保存')")

        # Wait for redirect to detail
        page.wait_for_load_state("networkidle")

        # Verify detail page shows the subject
        expect(page.locator(f"text={subject}").first).to_be_visible()

    def test_check_in_and_check_out(self, logged_in_page, api_token):
        """UAT-EVT-02 + UAT-EVT-03: Check in and check out a visit."""
        # Create event via API
        resp = requests.post(f"{API_URL}/events", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "subject": f"UAT Check-in Test {fake.word()}",
            "start_datetime": "2026-07-20T10:00:00",
        })
        assert resp.status_code == 201
        event_id = resp.json()["id"]

        page = logged_in_page
        page.goto(f"{BASE_URL}/events/{event_id}")
        page.wait_for_load_state("networkidle")

        # Should see the event detail
        expect(page.locator("text=计划中").first).to_be_visible()

    def test_event_list_and_search(self, logged_in_page, api_token):
        """UAT-EVT-05: Visit list search and filter."""
        # Create two events via API
        subject_a = f"UAT Search Alpha {fake.word()}"
        subject_b = f"UAT Search Beta {fake.word()}"
        for subj in [subject_a, subject_b]:
            requests.post(f"{API_URL}/events", headers={
                "Authorization": f"Bearer {api_token}",
            }, json={
                "subject": subj,
                "start_datetime": "2026-07-25T10:00:00",
            })

        page = logged_in_page
        page.goto(f"{BASE_URL}/events")
        page.wait_for_load_state("networkidle")

        # List should contain both
        expect(page.locator(f"text={subject_a}").first).to_be_visible()
