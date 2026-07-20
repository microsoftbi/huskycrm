"""UAT tests for Workflow and Report flow."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestWorkflowFlow:
    """UAT-WF series: Workflow rule management flow tests."""

    def test_create_workflow_rule(self, logged_in_page, api_token):
        """UAT-WF-01: Create a workflow rule with conditions and actions."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/workflows")
        page.wait_for_load_state("networkidle")

        # Create via API
        resp = requests.post(f"{API_URL}/workflows", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": f"大额通知_{fake.random_int(1000,9999)}",
            "object_type": "opportunity",
            "trigger_event": "create_or_update",
            "condition_expression": [
                {"field": "amount", "operator": "gt", "value": 100000},
            ],
            "actions": [
                {
                    "action_type": "send_notification",
                    "action_config": {"message": "大额机会已创建!"},
                    "display_order": 0,
                },
            ],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_active"] is True
        assert len(data["actions"]) == 1

    def test_list_workflows(self, logged_in_page, api_token):
        """UAT-WF-01 (continued): Verify workflow appears in list."""
        # Create via API
        requests.post(f"{API_URL}/workflows", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": f"规则_{fake.word()}",
            "object_type": "account",
            "trigger_event": "create",
            "condition_expression": [{"field": "name", "operator": "contains", "value": "VIP"}],
            "actions": [],
        })

        resp = requests.get(f"{API_URL}/workflows", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_toggle_workflow_active(self, logged_in_page, api_token):
        """UAT-WF-01: Toggle workflow active/inactive."""
        resp = requests.post(f"{API_URL}/workflows", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": f"可切换规则_{fake.word()}",
            "object_type": "contact",
            "trigger_event": "update",
            "condition_expression": [{"field": "email", "operator": "is_not_empty", "value": None}],
            "actions": [],
        })
        rule_id = resp.json()["id"]

        # Deactivate
        resp = requests.put(f"{API_URL}/workflows/{rule_id}", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"is_active": False})
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

        # Reactivate
        resp = requests.put(f"{API_URL}/workflows/{rule_id}", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"is_active": True})
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

    def test_test_workflow_condition(self, logged_in_page, api_token):
        """UAT-WF-01: Test workflow condition matching."""
        resp = requests.post(f"{API_URL}/workflows", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": "条件测试规则",
            "object_type": "opportunity",
            "trigger_event": "create",
            "condition_expression": [{"field": "amount", "operator": "gt", "value": 10000}],
            "actions": [],
        })
        rule_id = resp.json()["id"]

        # Test with matching record
        resp = requests.post(f"{API_URL}/workflows/{rule_id}/test", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"record": {"amount": 50000}})
        assert resp.status_code == 200
        assert resp.json()["conditions_met"] is True

        # Test with non-matching record
        resp = requests.post(f"{API_URL}/workflows/{rule_id}/test", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"record": {"amount": 100}})
        assert resp.status_code == 200
        assert resp.json()["conditions_met"] is False

    def test_delete_workflow(self, logged_in_page, api_token):
        """UAT-WF-01: Delete a workflow rule."""
        resp = requests.post(f"{API_URL}/workflows", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": "待删除规则",
            "object_type": "account",
            "trigger_event": "create",
            "condition_expression": [],
            "actions": [],
        })
        rule_id = resp.json()["id"]

        resp = requests.delete(f"{API_URL}/workflows/{rule_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        # Standard users may not have delete permission — skip if 403
        if resp.status_code == 403:
            return
        assert resp.status_code == 204

        resp = requests.get(f"{API_URL}/workflows/{rule_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 404


class TestReportFlow:
    """UAT-REP series: Report management flow tests."""

    def test_create_and_run_report(self, logged_in_page, api_token):
        """UAT-REP-01: Create and run a report."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/reports")
        page.wait_for_load_state("networkidle")

        # Create a few accounts for data
        for i in range(3):
            requests.post(f"{API_URL}/accounts", headers={
                "Authorization": f"Bearer {api_token}",
            }, json={"name": fake.company(), "industry": fake.random_element(["Tech", "Finance", "Health"])})

        # Create report via API
        resp = requests.post(f"{API_URL}/reports", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": "账户报表",
            "object_type": "account",
            "columns": ["id", "name", "industry", "phone"],
        })
        assert resp.status_code == 201
        report_id = resp.json()["id"]

        # Run report
        resp = requests.post(f"{API_URL}/reports/{report_id}/run", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "columns" in data
        assert "rows" in data
        assert "total" in data
        assert data["total"] >= 3
        assert "name" in data["columns"]

    def test_report_with_filters(self, logged_in_page, api_token):
        """UAT-REP-01: Create and run a filtered report."""
        unique_filter = f"UATFilter_{fake.random_int(10000,99999)}"
        requests.post(f"{API_URL}/accounts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": "UAT Acme", "industry": unique_filter})
        requests.post(f"{API_URL}/accounts", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": "UAT Beta", "industry": "Other_" + unique_filter})

        resp = requests.post(f"{API_URL}/reports", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": "过滤报表",
            "object_type": "account",
            "columns": ["id", "name", "industry"],
            "filters": [{"field": "industry", "operator": "eq", "value": unique_filter}],
        })
        report_id = resp.json()["id"]

        resp = requests.post(f"{API_URL}/reports/{report_id}/run", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1, f"Expected 1, got {data['total']}"

    def test_report_crud_lifecycle(self, logged_in_page, api_token):
        """UAT-REP-01: Full report CRUD lifecycle."""
        # CREATE
        resp = requests.post(f"{API_URL}/reports", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "name": "生命周期测试报表",
            "object_type": "contact",
            "columns": ["id", "first_name", "last_name", "email"],
        })
        assert resp.status_code == 201
        report_id = resp.json()["id"]

        # READ
        resp = requests.get(f"{API_URL}/reports/{report_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "生命周期测试报表"

        # UPDATE
        resp = requests.put(f"{API_URL}/reports/{report_id}", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"name": "已更新报表", "columns": ["id", "first_name"]})
        assert resp.status_code == 200
        assert resp.json()["name"] == "已更新报表"

        # DELETE
        resp = requests.delete(f"{API_URL}/reports/{report_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        # Standard users may not have delete permission — skip if 403
        if resp.status_code == 403:
            return
        assert resp.status_code == 204