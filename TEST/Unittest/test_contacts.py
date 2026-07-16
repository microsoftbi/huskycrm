"""Tests for Contact CRUD endpoints."""


class TestCreateContact:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "John", "last_name": "Doe",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    async def test_create_full(self, client, auth_headers):
        acc = await client.post("/api/accounts", headers=auth_headers, json={"name": "Test Corp"})
        acc_id = acc.json()["id"]
        resp = await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "Jane", "last_name": "Smith",
            "email": "jane@test.com", "phone": "555-0100",
            "mobile_phone": "555-0200", "title": "CTO",
            "department": "Engineering", "account_id": acc_id,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "jane@test.com"
        assert data["account_id"] == acc_id

    async def test_create_missing_name(self, client, auth_headers):
        resp = await client.post("/api/contacts", headers=auth_headers, json={"first_name": "OnlyFirst"})
        assert resp.status_code == 422


class TestListContacts:
    async def test_list_with_account_filter(self, client, auth_headers):
        acc1 = (await client.post("/api/accounts", headers=auth_headers, json={"name": "A1"})).json()
        acc2 = (await client.post("/api/accounts", headers=auth_headers, json={"name": "A2"})).json()
        await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "F1", "last_name": "L1", "account_id": acc1["id"],
        })
        await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "F2", "last_name": "L2", "account_id": acc2["id"],
        })
        resp = await client.get(f"/api/contacts?account_id={acc1['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["first_name"] == "F1"

    async def test_search_contacts(self, client, auth_headers):
        await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "Alice", "last_name": "Wang",
        })
        await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "Bob", "last_name": "Li",
        })
        resp = await client.get("/api/contacts?search=Alice", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


class TestUpdateContact:
    async def test_update(self, client, auth_headers):
        resp = await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "Old", "last_name": "Name",
        })
        c = resp.json()
        resp = await client.put(f"/api/contacts/{c['id']}", headers=auth_headers, json={
            "first_name": "New", "title": "Manager",
        })
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "New"
        assert resp.json()["title"] == "Manager"


class TestDeleteContact:
    async def test_delete(self, client, auth_headers):
        resp = await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "Del", "last_name": "Ete",
        })
        c = resp.json()
        resp = await client.delete(f"/api/contacts/{c['id']}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/contacts/{c['id']}", headers=auth_headers)
        assert resp.status_code == 404
