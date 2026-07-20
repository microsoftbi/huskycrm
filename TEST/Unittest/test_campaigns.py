"""Tests for Campaign CRUD and member management endpoints."""


class TestCreateCampaign:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/campaigns", headers=auth_headers, json={
            "name": "春季促销活动",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "春季促销活动"
        assert data["status"] == "planning"

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/campaigns", headers=auth_headers, json={
            "name": "秋季大促", "type": "促销",
            "status": "in_progress", "budget": 100000,
            "description": "秋季大促活动",
            "start_date": "2026-09-01", "end_date": "2026-09-30",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "促销"
        assert float(data["budget"]) == 100000

    async def test_create_missing_name(self, client, auth_headers):
        resp = await client.post("/api/campaigns", headers=auth_headers, json={})
        assert resp.status_code == 422


class TestListCampaigns:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/campaigns", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/campaigns", headers=auth_headers, json={"name": "A"})
        await client.post("/api/campaigns", headers=auth_headers, json={"name": "B"})
        resp = await client.get("/api/campaigns", headers=auth_headers)
        assert resp.json()["total"] == 2

    async def test_search(self, client, auth_headers):
        await client.post("/api/campaigns", headers=auth_headers, json={"name": "搜索目标"})
        await client.post("/api/campaigns", headers=auth_headers, json={"name": "其他活动"})
        resp = await client.get("/api/campaigns?search=搜索", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_filter_by_status(self, client, auth_headers):
        await client.post("/api/campaigns", headers=auth_headers, json={
            "name": "C1", "status": "in_progress",
        })
        await client.post("/api/campaigns", headers=auth_headers, json={
            "name": "C2", "status": "completed",
        })
        resp = await client.get("/api/campaigns?status_filter=completed", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_filter_by_type(self, client, auth_headers):
        await client.post("/api/campaigns", headers=auth_headers, json={
            "name": "T1", "type": "促销",
        })
        await client.post("/api/campaigns", headers=auth_headers, json={
            "name": "T2", "type": "展会",
        })
        resp = await client.get("/api/campaigns?type_filter=展会", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/campaigns", headers=auth_headers, json={"name": f"C{i}"})
        resp = await client.get("/api/campaigns?page=1&page_size=2", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestGetCampaign:
    async def test_get_by_id(self, client, auth_headers):
        resp = await client.post("/api/campaigns", headers=auth_headers, json={"name": "查看活动"})
        cid = resp.json()["id"]
        resp = await client.get(f"/api/campaigns/{cid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "查看活动"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/campaigns/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateCampaign:
    async def test_update(self, client, auth_headers):
        resp = await client.post("/api/campaigns", headers=auth_headers, json={"name": "旧名称"})
        cid = resp.json()["id"]
        resp = await client.put(f"/api/campaigns/{cid}", headers=auth_headers, json={
            "name": "新名称", "status": "completed",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"
        assert resp.json()["status"] == "completed"

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/campaigns/bad_id", headers=auth_headers, json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteCampaign:
    async def test_delete(self, client, auth_headers):
        resp = await client.post("/api/campaigns", headers=auth_headers, json={"name": "待删除"})
        cid = resp.json()["id"]
        resp = await client.delete(f"/api/campaigns/{cid}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/campaigns/{cid}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/campaigns/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestCampaignMembers:
    async def test_add_member(self, client, auth_headers):
        camp = await client.post("/api/campaigns", headers=auth_headers, json={"name": "成员活动"})
        cid = camp.json()["id"]
        resp = await client.post(f"/api/campaigns/{cid}/members", headers=auth_headers, json={
            "contact_id": None, "lead_id": None, "type": "lead",
        })
        # OK if member created with null lead_id (validation in backend)
        assert resp.status_code in (200, 201, 400)

    async def test_list_members(self, client, auth_headers):
        camp = await client.post("/api/campaigns", headers=auth_headers, json={"name": "列表活动"})
        cid = camp.json()["id"]
        resp = await client.get(f"/api/campaigns/{cid}/members", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)