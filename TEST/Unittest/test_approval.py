"""Tests for Approval Rules and Approval Requests CRUD and workflow."""


class TestCreateApprovalRule:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "金额审批", "object_type": "opportunity",
            "condition_expression": "[]", "approver_type": "manager",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "金额审批"
        assert data["is_active"] is True
        assert data["id"].startswith("apr_")

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "大额商机审批", "object_type": "opportunity",
            "condition_expression": '[{"field": "amount", "operator": "gt", "value": 100000}]',
            "approver_type": "specific_user", "approver_user_id": "user_001",
            "approval_order": 2, "is_active": False,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["approval_order"] == 2
        assert data["is_active"] is False

    async def test_create_missing_name(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "object_type": "opportunity",
        })
        assert resp.status_code == 422

    async def test_create_invalid_condition(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "无效条件", "object_type": "opportunity",
            "condition_expression": "not-json",
        })
        assert resp.status_code == 400


class TestListApprovalRules:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/approval-rules", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "规则A", "object_type": "opportunity", "condition_expression": "[]",
        })
        await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "规则B", "object_type": "opportunity", "condition_expression": "[]",
        })
        resp = await client.get("/api/approval-rules", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    async def test_filter_by_object_type(self, client, auth_headers):
        await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "机会审批", "object_type": "opportunity", "condition_expression": "[]",
        })
        await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "账户审批", "object_type": "account", "condition_expression": "[]",
        })
        resp = await client.get("/api/approval-rules?object_type=account", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/approval-rules", headers=auth_headers, json={
                "name": f"规则{i}", "object_type": "opportunity", "condition_expression": "[]",
            })
        resp = await client.get("/api/approval-rules?page=1&page_size=3", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3


class TestGetApprovalRule:
    async def test_get_by_id(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "获取测试", "object_type": "opportunity", "condition_expression": "[]",
        })
        rule_id = resp.json()["id"]
        resp = await client.get(f"/api/approval-rules/{rule_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "获取测试"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/approval-rules/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateApprovalRule:
    async def test_update(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "旧名称", "object_type": "opportunity", "condition_expression": "[]",
        })
        rule_id = resp.json()["id"]
        resp = await client.put(f"/api/approval-rules/{rule_id}", headers=auth_headers, json={
            "name": "新名称", "is_active": False,
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"
        assert resp.json()["is_active"] is False

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/approval-rules/bad_id", headers=auth_headers, json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteApprovalRule:
    async def test_delete(self, client, auth_headers):
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "删除测试", "object_type": "opportunity", "condition_expression": "[]",
        })
        rule_id = resp.json()["id"]
        resp = await client.delete(f"/api/approval-rules/{rule_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/approval-rules/{rule_id}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/approval-rules/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestApprovalWorkflow:
    async def test_full_approval_flow(self, client, auth_headers, user_token):
        """Create rule → trigger → approve → verify."""
        # Get current user ID
        me = await client.get("/api/auth/me", headers=auth_headers)
        my_id = me.json()["id"]

        # 1. Create a rule
        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "完整流程", "object_type": "opportunity",
            "condition_expression": "[]",  # empty = match all
            "approver_type": "specific_user",
            "approver_user_id": my_id,
        })
        assert resp.status_code == 201
        rule_id = resp.json()["id"]

        # 2. Trigger approval
        resp = await client.post("/api/approval-rules/trigger", headers=auth_headers, json={
            "object_type": "opportunity", "object_id": "opp_001",
            "record_data": {"amount": 500000},
        })
        assert resp.status_code == 200
        req_data = resp.json()
        assert req_data["status"] == "pending"
        request_id = req_data["id"]

        # 3. List requests
        resp = await client.get("/api/approval-rules/requests", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

        # 4. Approve the request
        resp = await client.post(f"/api/approval-rules/requests/{request_id}/approve",
                                 headers=auth_headers, json={"comment": "同意"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

        # 5. Check my queue
        resp = await client.get("/api/approval-rules/my-queue", headers=auth_headers)
        assert resp.status_code == 200

    async def test_reject_flow(self, client, auth_headers, user_token):
        """Create rule → trigger → reject → verify."""
        me = await client.get("/api/auth/me", headers=auth_headers)
        my_id = me.json()["id"]

        resp = await client.post("/api/approval-rules", headers=auth_headers, json={
            "name": "拒绝流程", "object_type": "opportunity",
            "condition_expression": "[]",
            "approver_type": "specific_user",
            "approver_user_id": my_id,
        })
        rule_id = resp.json()["id"]

        resp = await client.post("/api/approval-rules/trigger", headers=auth_headers, json={
            "object_type": "opportunity", "object_id": "opp_002",
            "record_data": {"amount": 1000},
        })
        request_id = resp.json()["id"]

        resp = await client.post(f"/api/approval-rules/requests/{request_id}/reject",
                                 headers=auth_headers, json={"comment": "拒绝"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    async def test_no_matching_rule(self, client, auth_headers):
        """Trigger without any matching rule should return 200 with no request."""
        resp = await client.post("/api/approval-rules/trigger", headers=auth_headers, json={
            "object_type": "nonexistent_type", "object_id": "obj_001",
            "record_data": {},
        })
        # No matching rule → returns 200 with detail message
        assert resp.status_code == 200