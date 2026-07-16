"""Tests for Account CRUD endpoints."""


class TestListAccounts:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/accounts", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/accounts", headers=auth_headers, json={
            "name": "Acme Corp", "industry": "Technology",
        })
        await client.post("/api/accounts", headers=auth_headers, json={
            "name": "Beta Inc", "industry": "Finance",
        })
        resp = await client.get("/api/accounts", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_search(self, client, auth_headers):
        await client.post("/api/accounts", headers=auth_headers, json={"name": "Alpha Ltd"})
        await client.post("/api/accounts", headers=auth_headers, json={"name": "Beta Co"})
        resp = await client.get("/api/accounts?search=Alpha", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Alpha Ltd"

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/accounts", headers=auth_headers, json={"name": f"Acc{i}"})
        resp = await client.get("/api/accounts?page=1&page_size=2", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestCreateAccount:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/accounts", headers=auth_headers, json={"name": "New Corp"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "New Corp"
        assert data["id"] is not None

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/accounts", headers=auth_headers, json={
            "name": "Full Corp",
            "industry": "Healthcare",
            "phone": "123-456-7890",
            "website": "https://fullcorp.com",
            "email": "info@fullcorp.com",
            "billing_street": "123 Main St",
            "billing_city": "Beijing",
            "billing_state": "BJ",
            "billing_zip": "100000",
            "billing_country": "China",
            "description": "A full test account",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["industry"] == "Healthcare"
        assert data["billing_city"] == "Beijing"

    async def test_create_missing_name(self, client, auth_headers):
        resp = await client.post("/api/accounts", headers=auth_headers, json={"industry": "No Name"})
        assert resp.status_code == 422


class TestGetAccount:
    async def test_get_by_id(self, client, auth_headers):
        create = await client.post("/api/accounts", headers=auth_headers, json={"name": "Get Test"})
        acc_id = create.json()["id"]
        resp = await client.get(f"/api/accounts/{acc_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Test"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/accounts/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateAccount:
    async def test_update(self, client, auth_headers):
        create = await client.post("/api/accounts", headers=auth_headers, json={"name": "Old Name"})
        acc_id = create.json()["id"]
        resp = await client.put(f"/api/accounts/{acc_id}", headers=auth_headers, json={
            "name": "New Name", "industry": "Updated",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["industry"] == "Updated"

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/accounts/99999", headers=auth_headers, json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteAccount:
    async def test_delete(self, client, auth_headers):
        create = await client.post("/api/accounts", headers=auth_headers, json={"name": "Delete Me"})
        acc_id = create.json()["id"]
        resp = await client.delete(f"/api/accounts/{acc_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/accounts/{acc_id}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/accounts/99999", headers=auth_headers)
        assert resp.status_code == 404
