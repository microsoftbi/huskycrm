"""Tests for Workflow rules and execution engine."""

from app.services.workflow_service import evaluate_conditions


class TestConditionEvaluator:
    """Unit tests for the condition evaluation logic."""

    def test_eq_operator(self):
        record = {"status": "active"}
        assert evaluate_conditions(record, [{"field": "status", "operator": "eq", "value": "active"}]) is True
        assert evaluate_conditions(record, [{"field": "status", "operator": "eq", "value": "inactive"}]) is False

    def test_gt_operator(self):
        record = {"amount": 50000}
        assert evaluate_conditions(record, [{"field": "amount", "operator": "gt", "value": 10000}]) is True
        assert evaluate_conditions(record, [{"field": "amount", "operator": "gt", "value": 100000}]) is False

    def test_contains_operator(self):
        record = {"name": "Acme Corporation"}
        assert evaluate_conditions(record, [{"field": "name", "operator": "contains", "value": "Acme"}]) is True
        assert evaluate_conditions(record, [{"field": "name", "operator": "contains", "value": "Beta"}]) is False

    def test_multiple_conditions_anded(self):
        record = {"amount": 50000, "status": "open"}
        conditions = [
            {"field": "amount", "operator": "gt", "value": 10000},
            {"field": "status", "operator": "eq", "value": "open"},
        ]
        assert evaluate_conditions(record, conditions) is True
        conditions.append({"field": "status", "operator": "eq", "value": "closed"})
        assert evaluate_conditions(record, conditions) is False

    def test_empty_conditions_always_true(self):
        record = {"amount": 0}
        assert evaluate_conditions(record, []) is True
        assert evaluate_conditions(record, None) is True

    def test_is_empty_operator(self):
        record = {"notes": ""}
        assert evaluate_conditions(record, [{"field": "notes", "operator": "is_empty", "value": None}]) is True
        record = {"notes": "has content"}
        assert evaluate_conditions(record, [{"field": "notes", "operator": "is_empty", "value": None}]) is False

    def test_missing_field_treated_as_none(self):
        record = {}
        assert evaluate_conditions(record, [{"field": "amount", "operator": "gt", "value": 100}]) is False
        assert evaluate_conditions(record, [{"field": "amount", "operator": "is_empty", "value": None}]) is True


class TestWorkflowCRUD:
    async def test_create_workflow(self, client, auth_headers):
        resp = await client.post("/api/workflows", headers=auth_headers, json={
            "name": "大额机会通知",
            "object_type": "opportunity",
            "trigger_event": "create_or_update",
            "condition_expression": [{"field": "amount", "operator": "gt", "value": 100000}],
            "actions": [
                {"action_type": "send_notification", "action_config": {"message": "大额机会!"}, "display_order": 0},
            ],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "大额机会通知"
        assert data["is_active"] is True
        assert len(data["actions"]) == 1

    async def test_list_workflows(self, client, auth_headers):
        await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Rule 1", "object_type": "account", "trigger_event": "create", "actions": [],
        })
        await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Rule 2", "object_type": "contact", "trigger_event": "update", "actions": [],
        })
        resp = await client.get("/api/workflows", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_workflow(self, client, auth_headers):
        resp = await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Get Test", "object_type": "account", "trigger_event": "create",
            "actions": [{"action_type": "send_notification", "action_config": {"message": "hi"}, "display_order": 0}],
        })
        wf_id = resp.json()["id"]
        resp = await client.get(f"/api/workflows/{wf_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Test"

    async def test_update_workflow(self, client, auth_headers):
        resp = await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Original", "object_type": "account", "trigger_event": "create", "actions": [],
        })
        wf_id = resp.json()["id"]
        resp = await client.put(f"/api/workflows/{wf_id}", headers=auth_headers, json={
            "name": "Updated", "is_active": False,
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"
        assert resp.json()["is_active"] is False

    async def test_delete_workflow(self, client, auth_headers):
        resp = await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Delete Me", "object_type": "account", "trigger_event": "create", "actions": [],
        })
        wf_id = resp.json()["id"]
        resp = await client.delete(f"/api/workflows/{wf_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/workflows/{wf_id}", headers=auth_headers)
        assert resp.status_code == 404


class TestWorkflowTest:
    async def test_workflow_condition_match(self, client, auth_headers):
        resp = await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Test Rule", "object_type": "opportunity", "trigger_event": "create",
            "condition_expression": [{"field": "amount", "operator": "gt", "value": 10000}],
            "actions": [],
        })
        wf_id = resp.json()["id"]
        resp = await client.post(f"/api/workflows/{wf_id}/test", headers=auth_headers, json={
            "record": {"amount": 50000},
        })
        assert resp.status_code == 200
        assert resp.json()["conditions_met"] is True

    async def test_workflow_condition_no_match(self, client, auth_headers):
        resp = await client.post("/api/workflows", headers=auth_headers, json={
            "name": "Test Rule 2", "object_type": "opportunity", "trigger_event": "create",
            "condition_expression": [{"field": "amount", "operator": "gt", "value": 100000}],
            "actions": [],
        })
        wf_id = resp.json()["id"]
        resp = await client.post(f"/api/workflows/{wf_id}/test", headers=auth_headers, json={
            "record": {"amount": 5000},
        })
        assert resp.status_code == 200
        assert resp.json()["conditions_met"] is False
