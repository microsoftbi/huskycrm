"""Tests for Opportunity and Pipeline endpoints."""


class TestStages:
    async def test_stages_seeded(self, client, auth_headers, seeded_stages):
        resp = await client.get("/api/opportunities/stages", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 7
        assert data[0]["name"] == "初步接触"
        assert data[5]["is_closed_won"] is True
        assert data[6]["is_closed_lost"] is True


class TestCreateOpportunity:
    async def test_create_success(self, client, auth_headers, seeded_stages):
        resp = await client.post("/api/accounts", headers=auth_headers, json={"name": "Test Account"})
        acc_id = resp.json()["id"]
        resp = await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Big Deal",
            "account_id": acc_id,
            "stage_id": 1,
            "amount": 500000,
            "probability": 30,
            "close_date": "2026-12-31",
            "description": "A significant opportunity",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Big Deal"
        assert data["amount"] == 500000.0
        assert data["stage_id"] == 1

    async def test_create_invalid_stage(self, client, auth_headers):
        resp = await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Bad Stage", "stage_id": 999,
        })
        assert resp.status_code == 400


class TestListOpportunities:
    async def test_list_and_search(self, client, auth_headers, seeded_stages):
        await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Alpha Deal", "stage_id": 1, "amount": 10000,
        })
        await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Beta Deal", "stage_id": 2, "amount": 20000,
        })
        resp = await client.get("/api/opportunities", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

        resp = await client.get("/api/opportunities?search=Alpha", headers=auth_headers)
        assert resp.json()["total"] == 1

        resp = await client.get("/api/opportunities?stage_id=2", headers=auth_headers)
        assert resp.json()["total"] == 1


class TestUpdateOpportunity:
    async def test_move_stage(self, client, auth_headers, seeded_stages):
        resp = await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Moving Deal", "stage_id": 1, "amount": 100000,
        })
        opp_id = resp.json()["id"]
        resp = await client.put(f"/api/opportunities/{opp_id}", headers=auth_headers, json={
            "stage_id": 3, "probability": 50,
        })
        assert resp.status_code == 200
        assert resp.json()["stage_id"] == 3
        assert resp.json()["probability"] == 50

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/opportunities/999", headers=auth_headers, json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteOpportunity:
    async def test_delete(self, client, auth_headers, seeded_stages):
        resp = await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Delete Me", "stage_id": 1,
        })
        opp_id = resp.json()["id"]
        resp = await client.delete(f"/api/opportunities/{opp_id}", headers=auth_headers)
        assert resp.status_code == 204


class TestPipeline:
    async def test_pipeline_structure(self, client, auth_headers, seeded_stages):
        await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Deal 1", "stage_id": 1, "amount": 50000,
        })
        await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Deal 2", "stage_id": 1, "amount": 30000,
        })
        resp = await client.get("/api/opportunities/pipeline", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "stages" in data
        assert len(data["stages"]) == 7
        stage1 = data["stages"][0]
        assert stage1["count"] == 2
        assert stage1["total_amount"] == 80000.0
