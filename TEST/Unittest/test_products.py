"""Tests for Product CRUD endpoints."""


class TestCreateProduct:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={
            "name": "测试产品",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "测试产品"

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={
            "name": "企业版", "product_code": "ENT-001",
            "category": "软件", "price": 9999.00,
            "cost": 5000.00, "description": "企业版软件许可",
            "is_active": True,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["product_code"] == "ENT-001"
        assert data["category"] == "软件"
        assert data["is_active"] is True
        assert float(data["price"]) == 9999.00

    async def test_create_missing_name(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={})
        assert resp.status_code == 422

    async def test_create_default_price(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={
            "name": "默认价格产品",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "默认价格产品"


class TestListProducts:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/products", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/products", headers=auth_headers, json={"name": "P1"})
        await client.post("/api/products", headers=auth_headers, json={"name": "P2"})
        resp = await client.get("/api/products", headers=auth_headers)
        assert resp.json()["total"] == 2

    async def test_search(self, client, auth_headers):
        await client.post("/api/products", headers=auth_headers, json={"name": "高级版"})
        await client.post("/api/products", headers=auth_headers, json={"name": "基础版"})
        resp = await client.get("/api/products?search=高级", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/products", headers=auth_headers, json={
                "name": f"产品{i}",
            })
        resp = await client.get("/api/products?page=1&page_size=2", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestGetProduct:
    async def test_get_by_id(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={"name": "查询产品"})
        pid = resp.json()["id"]
        resp = await client.get(f"/api/products/{pid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "查询产品"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/products/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateProduct:
    async def test_update(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={
            "name": "旧产品",
        })
        pid = resp.json()["id"]
        resp = await client.put(f"/api/products/{pid}", headers=auth_headers, json={
            "name": "新产品", "price": 150,
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "新产品"
        assert float(resp.json()["price"]) == 150

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/products/bad_id", headers=auth_headers, json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteProduct:
    async def test_delete(self, client, auth_headers):
        resp = await client.post("/api/products", headers=auth_headers, json={"name": "待删除"})
        pid = resp.json()["id"]
        resp = await client.delete(f"/api/products/{pid}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/products/{pid}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/products/bad_id", headers=auth_headers)
        assert resp.status_code == 404