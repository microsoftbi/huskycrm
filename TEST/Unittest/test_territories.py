"""Tests for Territory CRUD, tree, members, accounts, products, and pipeline."""


class TestCreateTerritory:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/territories", headers=auth_headers, json={
            "name": "华东区域",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "华东区域"
        assert data["territory_type"] == "region"

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/territories", headers=auth_headers, json={
            "name": "华北区域", "code": "NC-001",
            "territory_type": "district", "description": "华北销售区域",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == "NC-001"
        assert data["territory_type"] == "district"

    async def test_create_with_parent(self, client, auth_headers):
        parent = await client.post("/api/territories", headers=auth_headers, json={"name": "中国"})
        pid = parent.json()["id"]
        resp = await client.post("/api/territories", headers=auth_headers, json={
            "name": "北京", "parent_id": pid,
        })
        assert resp.status_code == 201
        assert resp.json()["parent_id"] == pid

    async def test_create_missing_name(self, client, auth_headers):
        resp = await client.post("/api/territories", headers=auth_headers, json={})
        assert resp.status_code == 422

    async def test_create_duplicate_code(self, client, auth_headers):
        await client.post("/api/territories", headers=auth_headers, json={
            "name": "T1", "code": "DUP",
        })
        resp = await client.post("/api/territories", headers=auth_headers, json={
            "name": "T2", "code": "DUP",
        })
        assert resp.status_code == 400


class TestListTerritories:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/territories", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/territories", headers=auth_headers, json={"name": "区域A"})
        await client.post("/api/territories", headers=auth_headers, json={"name": "区域B"})
        resp = await client.get("/api/territories", headers=auth_headers)
        assert resp.json()["total"] == 2

    async def test_search(self, client, auth_headers):
        await client.post("/api/territories", headers=auth_headers, json={"name": "目标区域"})
        await client.post("/api/territories", headers=auth_headers, json={"name": "其他区域"})
        resp = await client.get("/api/territories?search=目标", headers=auth_headers)
        assert resp.json()["total"] == 1

    async def test_pagination(self, client, auth_headers):
        for i in range(5):
            await client.post("/api/territories", headers=auth_headers, json={"name": f"区域{i}"})
        resp = await client.get("/api/territories?page=1&page_size=2", headers=auth_headers)
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2


class TestTerritoryTree:
    async def test_tree_structure(self, client, auth_headers):
        global_ = await client.post("/api/territories", headers=auth_headers, json={"name": "全球"})
        gid = global_.json()["id"]
        asia = await client.post("/api/territories", headers=auth_headers, json={
            "name": "亚太", "parent_id": gid,
        })
        aid = asia.json()["id"]
        await client.post("/api/territories", headers=auth_headers, json={
            "name": "中国", "parent_id": aid,
        })
        resp = await client.get("/api/territories/tree", headers=auth_headers)
        assert resp.status_code == 200
        tree = resp.json()
        # Tree should contain the root node(s)
        assert len(tree) > 0
        # Root should have a child (亚太)
        assert len(tree[0].get("children", [])) > 0


class TestGetTerritory:
    async def test_get_by_id(self, client, auth_headers):
        resp = await client.post("/api/territories", headers=auth_headers, json={"name": "查询区域"})
        tid = resp.json()["id"]
        resp = await client.get(f"/api/territories/{tid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "查询区域"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/territories/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateTerritory:
    async def test_update(self, client, auth_headers):
        resp = await client.post("/api/territories", headers=auth_headers, json={"name": "旧名称"})
        tid = resp.json()["id"]
        resp = await client.put(f"/api/territories/{tid}", headers=auth_headers, json={
            "name": "新名称",
        })
        assert resp.status_code == 200
        # Verify via GET instead of parsing the update response body
        resp = await client.get(f"/api/territories/{tid}", headers=auth_headers)
        assert resp.json()["name"] == "新名称"

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/territories/bad_id", headers=auth_headers, json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteTerritory:
    async def test_delete(self, client, auth_headers):
        resp = await client.post("/api/territories", headers=auth_headers, json={"name": "待删除"})
        tid = resp.json()["id"]
        resp = await client.delete(f"/api/territories/{tid}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/territories/{tid}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/territories/bad_id", headers=auth_headers)
        assert resp.status_code == 404


class TestTerritoryMembers:
    async def test_add_and_list_members(self, client, auth_headers, user_token):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "成员区域"})
        tid = terr.json()["id"]
        # Get current user ID from /api/auth/me
        me = await client.get("/api/auth/me", headers=auth_headers)
        uid = me.json()["id"]
        resp = await client.post(f"/api/territories/{tid}/members", headers=auth_headers, json={
            "user_id": uid, "role": "member",
        })
        assert resp.status_code == 201
        resp = await client.get(f"/api/territories/{tid}/members", headers=auth_headers)
        assert resp.status_code == 200
        members = resp.json()
        assert len(members) > 0
        assert members[0]["user_id"] == uid

    async def test_add_member_invalid_user(self, client, auth_headers):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "区域"})
        tid = terr.json()["id"]
        resp = await client.post(f"/api/territories/{tid}/members", headers=auth_headers, json={
            "user_id": "nonexistent", "role": "member",
        })
        assert resp.status_code == 400

    async def test_remove_member(self, client, auth_headers):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "移除区域"})
        tid = terr.json()["id"]
        me = await client.get("/api/auth/me", headers=auth_headers)
        uid = me.json()["id"]
        await client.post(f"/api/territories/{tid}/members", headers=auth_headers, json={
            "user_id": uid, "role": "member",
        })
        resp = await client.get(f"/api/territories/{tid}/members", headers=auth_headers)
        member_id = resp.json()[0]["id"]
        resp = await client.delete(f"/api/territories/{tid}/members/{member_id}", headers=auth_headers)
        assert resp.status_code == 204


class TestTerritoryAccounts:
    async def test_add_and_list_accounts(self, client, auth_headers):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "账户区域"})
        tid = terr.json()["id"]
        acc = await client.post("/api/accounts", headers=auth_headers, json={"name": "区域关联账户"})
        aid = acc.json()["id"]
        resp = await client.post(f"/api/territories/{tid}/accounts", headers=auth_headers, json={
            "account_id": aid,
        })
        assert resp.status_code == 201
        resp = await client.get(f"/api/territories/{tid}/accounts", headers=auth_headers)
        assert resp.status_code == 200
        accounts = resp.json()
        assert len(accounts) > 0
        assert accounts[0]["account_id"] == aid

    async def test_remove_account(self, client, auth_headers):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "移除账户区域"})
        tid = terr.json()["id"]
        acc = await client.post("/api/accounts", headers=auth_headers, json={"name": "待移除账户"})
        aid = acc.json()["id"]
        await client.post(f"/api/territories/{tid}/accounts", headers=auth_headers, json={"account_id": aid})
        resp = await client.delete(f"/api/territories/{tid}/accounts/{aid}", headers=auth_headers)
        assert resp.status_code == 204


class TestTerritoryProducts:
    async def test_add_and_list_products(self, client, auth_headers):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "产品区域"})
        tid = terr.json()["id"]
        prod = await client.post("/api/products", headers=auth_headers, json={
            "name": "区域产品", "standard_price": 100,
        })
        pid = prod.json()["id"]
        resp = await client.post(f"/api/territories/{tid}/products", headers=auth_headers, json={
            "product_id": pid, "price": 90.00,
        })
        assert resp.status_code == 201
        resp = await client.get(f"/api/territories/{tid}/products", headers=auth_headers)
        assert resp.status_code == 200
        products = resp.json()
        assert len(products) > 0
        assert products[0]["product_id"] == pid
        assert products[0].get("price") == 90.00

    async def test_remove_product(self, client, auth_headers):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "移除产品区域"})
        tid = terr.json()["id"]
        prod = await client.post("/api/products", headers=auth_headers, json={
            "name": "待移除产品", "standard_price": 50,
        })
        pid = prod.json()["id"]
        await client.post(f"/api/territories/{tid}/products", headers=auth_headers, json={"product_id": pid})
        resp = await client.delete(f"/api/territories/{tid}/products/{pid}", headers=auth_headers)
        assert resp.status_code == 204


class TestTerritoryPipeline:
    async def test_pipeline(self, client, auth_headers, seeded_stages):
        terr = await client.post("/api/territories", headers=auth_headers, json={"name": "管道区域"})
        tid = terr.json()["id"]
        acc = await client.post("/api/accounts", headers=auth_headers, json={"name": "管道账户"})
        aid = acc.json()["id"]
        # Link account to territory
        await client.post(f"/api/territories/{tid}/accounts", headers=auth_headers, json={"account_id": aid})
        # Create an opportunity under this account
        stages = seeded_stages
        await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "区域商机", "account_id": aid,
            "stage_id": stages[0].id, "amount": 50000,
        })
        resp = await client.get(f"/api/territories/{tid}/pipeline", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "stages" in data