"""Tests for Lead CRUD, conversion, and Web-to-Lead endpoints."""


class TestCreateLead:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "张", "last_name": "三", "company": "测试公司",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["first_name"] == "张"
        assert data["company"] == "测试公司"
        assert data["status"] == "New"

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "李", "last_name": "四",
            "company": "全字段公司", "email": "lisi@test.com",
            "phone": "13800138002", "source": "Web",
            "description": "测试线索",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "lisi@test.com"
        assert data["source"] == "Web"
        assert data["description"] == "测试线索"

    async def test_create_missing_required(self, client, auth_headers):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "缺字段",
        })
        assert resp.status_code == 422


class TestListLeads:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/leads", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "A", "last_name": "A", "company": "Co1",
        })
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "B", "last_name": "B", "company": "Co2",
        })
        resp = await client.get("/api/leads", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    async def test_search(self, client, auth_headers):
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "搜索", "last_name": "测试", "company": "FindMe",
        })
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "其他", "last_name": "人", "company": "HideMe",
        })
        resp = await client.get("/api/leads?search=FindMe", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_filter_by_status(self, client, auth_headers):
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "S1", "last_name": "T", "company": "C", "status": "Contacted",
        })
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "S2", "last_name": "T", "company": "C", "status": "Qualified",
        })
        resp = await client.get("/api/leads?status_filter=Contacted", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_filter_by_source(self, client, auth_headers):
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "S", "last_name": "R", "company": "C", "source": "Web",
        })
        await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "S", "last_name": "R2", "company": "C", "source": "Phone",
        })
        resp = await client.get("/api/leads?source_filter=Web", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/leads", headers=auth_headers, json={
                "first_name": f"P{i}", "last_name": "P", "company": "Co",
            })
        resp = await client.get("/api/leads?page=1&page_size=3", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3


class TestGetLead:
    async def test_get_by_id(self, client, auth_headers):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "Get", "last_name": "Me", "company": "C",
        })
        lead_id = resp.json()["id"]
        resp = await client.get(f"/api/leads/{lead_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Get"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/leads/nonexistent_id", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateLead:
    async def test_update(self, client, auth_headers):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "Old", "last_name": "Name", "company": "C",
        })
        lead_id = resp.json()["id"]
        resp = await client.put(f"/api/leads/{lead_id}", headers=auth_headers, json={
            "first_name": "New", "status": "Contacted",
        })
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "New"
        assert resp.json()["status"] == "Contacted"

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/leads/bad_id", headers=auth_headers, json={"first_name": "X"})
        assert resp.status_code == 404


class TestDeleteLead:
    async def test_delete(self, client, auth_headers):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "Del", "last_name": "Me", "company": "C",
        })
        lead_id = resp.json()["id"]
        resp = await client.delete(f"/api/leads/{lead_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/leads/{lead_id}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/leads/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestConvertLead:
    async def test_convert_with_new_account(self, client, auth_headers, seeded_stages):
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "转", "last_name": "化", "company": "转化公司",
            "email": "zhuanhua@test.com",
        })
        lead_id = resp.json()["id"]
        resp = await client.post(f"/api/leads/{lead_id}/convert", headers=auth_headers, json={
            "create_account": True,
            "account_name": "转化公司",
            "create_opportunity": True,
            "opportunity_name": "转化商机",
            "opportunity_amount": 50000,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["account_id"] is not None
        assert data["contact_id"] is not None
        assert data["opportunity_id"] is not None
        assert data["message"] == "Lead converted successfully"

    async def test_convert_with_existing_account(self, client, auth_headers, seeded_stages):
        acc = await client.post("/api/accounts", headers=auth_headers, json={"name": "已有账户"})
        acc_id = acc.json()["id"]
        resp = await client.post("/api/leads", headers=auth_headers, json={
            "first_name": "转", "last_name": "化2", "company": "Co",
        })
        lead_id = resp.json()["id"]
        resp = await client.post(f"/api/leads/{lead_id}/convert", headers=auth_headers, json={
            "create_account": False,
            "account_id": acc_id,
            "create_opportunity": False,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["account_id"] == acc_id
        assert data["opportunity_id"] is None
        assert data["message"] == "Lead converted successfully"


class TestWebToLead:
    async def test_web_to_lead_public(self, client):
        """Web-to-Lead endpoint requires no auth."""
        resp = await client.post("/api/leads/web-to-lead", json={
            "first_name": "Web", "last_name": "Lead",
            "company": "网站公司", "email": "web@lead.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["lead_id"] is not None
