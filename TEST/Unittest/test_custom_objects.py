"""Tests for the Custom Objects engine - the core Salesforce-like feature."""


class TestCreateCustomObject:
    async def test_create_with_fields(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_invoice",
            "label": "发票",
            "plural_label": "发票列表",
            "fields": [
                {"api_name": "invoice_number", "label": "发票编号", "field_type": "text", "is_required": True},
                {"api_name": "amount", "label": "金额", "field_type": "number"},
                {"api_name": "status", "label": "状态", "field_type": "picklist",
                 "picklist_values": ["待付款", "已付款"]},
            ],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["api_name"] == "custom_invoice"
        assert data["table_name"] == "obj_1"
        assert len(data["fields"]) == 3
        status_field = [f for f in data["fields"] if f["api_name"] == "status"][0]
        assert status_field["picklist_values"] == ["待付款", "已付款"]

    async def test_create_duplicate_api_name(self, client, auth_headers):
        await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_dup", "label": "Dup", "fields": [],
        })
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_dup", "label": "Dup2", "fields": [],
        })
        assert resp.status_code == 400

    async def test_create_without_fields(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_empty", "label": "Empty",
        })
        assert resp.status_code == 201
        assert resp.json()["fields"] == []


class TestListAndGetObjects:
    async def test_list_objects(self, client, auth_headers):
        await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_a", "label": "Object A", "fields": [],
        })
        await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_b", "label": "Object B", "fields": [],
        })
        resp = await client.get("/api/custom-objects", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_object_by_id(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_x", "label": "Object X",
            "fields": [{"api_name": "name", "label": "名称", "field_type": "text"}],
        })
        obj_id = resp.json()["id"]
        resp = await client.get(f"/api/custom-objects/{obj_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["label"] == "Object X"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/custom-objects/999", headers=auth_headers)
        assert resp.status_code == 404


class TestAddField:
    async def test_add_field(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_addfield", "label": "Add Field Test",
            "fields": [{"api_name": "f1", "label": "字段1", "field_type": "text"}],
        })
        obj_id = resp.json()["id"]
        resp = await client.post(f"/api/custom-objects/{obj_id}/fields", headers=auth_headers, json={
            "api_name": "f2", "label": "字段2", "field_type": "number",
        })
        assert resp.status_code == 201
        assert resp.json()["api_name"] == "f2"

        resp = await client.get(f"/api/custom-objects/{obj_id}", headers=auth_headers)
        assert len(resp.json()["fields"]) == 2

    async def test_add_duplicate_field(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_dupfield", "label": "Dup Field",
            "fields": [{"api_name": "f1", "label": "字段1", "field_type": "text"}],
        })
        obj_id = resp.json()["id"]
        resp = await client.post(f"/api/custom-objects/{obj_id}/fields", headers=auth_headers, json={
            "api_name": "f1", "label": "重复字段", "field_type": "text",
        })
        assert resp.status_code == 400


class TestRecordCRUD:
    async def _create_invoice_object(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_invoice",
            "label": "发票",
            "fields": [
                {"api_name": "invoice_number", "label": "发票编号", "field_type": "text", "is_required": True},
                {"api_name": "amount", "label": "金额", "field_type": "number"},
                {"api_name": "status", "label": "状态", "field_type": "picklist",
                 "picklist_values": ["待付款", "已付款"]},
            ],
        })
        return resp.json()

    async def test_create_record(self, client, auth_headers):
        obj = await self._create_invoice_object(client, auth_headers)
        resp = await client.post(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers, json={
            "fields": {"invoice_number": "INV-001", "amount": 15000.50, "status": "待付款"},
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["fields"]["invoice_number"] == "INV-001"
        assert data["fields"]["amount"] == 15000.50
        assert data["fields"]["status"] == "待付款"

    async def test_create_record_missing_required(self, client, auth_headers):
        obj = await self._create_invoice_object(client, auth_headers)
        resp = await client.post(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers, json={
            "fields": {"amount": 1000},
        })
        assert resp.status_code == 400

    async def test_list_records(self, client, auth_headers):
        obj = await self._create_invoice_object(client, auth_headers)
        await client.post(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers, json={
            "fields": {"invoice_number": "INV-001", "amount": 1000},
        })
        await client.post(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers, json={
            "fields": {"invoice_number": "INV-002", "amount": 2000},
        })
        resp = await client.get(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_update_record(self, client, auth_headers):
        obj = await self._create_invoice_object(client, auth_headers)
        resp = await client.post(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers, json={
            "fields": {"invoice_number": "INV-001", "amount": 1000, "status": "待付款"},
        })
        rec_id = resp.json()["id"]
        resp = await client.put(f"/api/custom-objects/{obj['id']}/records/{rec_id}", headers=auth_headers, json={
            "fields": {"amount": 2000, "status": "已付款"},
        })
        assert resp.status_code == 200
        assert resp.json()["fields"]["amount"] == 2000
        assert resp.json()["fields"]["status"] == "已付款"

    async def test_delete_record(self, client, auth_headers):
        obj = await self._create_invoice_object(client, auth_headers)
        resp = await client.post(f"/api/custom-objects/{obj['id']}/records", headers=auth_headers, json={
            "fields": {"invoice_number": "INV-001"},
        })
        rec_id = resp.json()["id"]
        resp = await client.delete(f"/api/custom-objects/{obj['id']}/records/{rec_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/custom-objects/{obj['id']}/records/{rec_id}", headers=auth_headers)
        assert resp.status_code == 404


class TestUniversalAPI:
    async def test_create_record_by_name(self, client, auth_headers):
        await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_universal", "label": "Universal Test",
            "fields": [{"api_name": "name", "label": "名称", "field_type": "text"}],
        })
        resp = await client.post("/api/custom-objects/by-name/custom_universal/records", headers=auth_headers, json={
            "fields": {"name": "Test Record"},
        })
        assert resp.status_code == 201
        assert resp.json()["fields"]["name"] == "Test Record"

    async def test_list_records_by_name(self, client, auth_headers):
        await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_list", "label": "List Test",
            "fields": [{"api_name": "title", "label": "标题", "field_type": "text"}],
        })
        await client.post("/api/custom-objects/by-name/custom_list/records", headers=auth_headers, json={
            "fields": {"title": "Record 1"},
        })
        resp = await client.get("/api/custom-objects/by-name/custom_list/records", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


class TestDeleteCustomObject:
    async def test_delete_object(self, client, auth_headers):
        resp = await client.post("/api/custom-objects", headers=auth_headers, json={
            "api_name": "custom_delete", "label": "Delete Test",
            "fields": [{"api_name": "f1", "label": "字段1", "field_type": "text"}],
        })
        obj_id = resp.json()["id"]
        resp = await client.delete(f"/api/custom-objects/{obj_id}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/custom-objects/{obj_id}", headers=auth_headers)
        assert resp.status_code == 404
