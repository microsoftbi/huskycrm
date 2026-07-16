"""UAT tests for Custom Objects engine flow."""

import requests
from playwright.sync_api import expect
from faker import Faker

API_URL = "http://localhost:8000/api"
BASE_URL = "http://localhost:5173"
fake = Faker()


class TestCustomObjectFlow:
    """UAT-CUS series: Custom object management flow tests."""

    def test_create_custom_object_with_fields(self, logged_in_page, api_token):
        """UAT-CUS-01: Create custom object with fields."""
        page = logged_in_page
        page.goto(f"{BASE_URL}/admin/objects")
        page.wait_for_load_state("networkidle")

        # Create via API since the admin page uses a complex builder UI
        obj_name = f"custom_{fake.word()}"
        resp = requests.post(f"{API_URL}/custom-objects", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "api_name": obj_name,
            "label": "测试对象",
            "fields": [
                {"api_name": "name", "label": "名称", "field_type": "text", "is_required": True},
                {"api_name": "quantity", "label": "数量", "field_type": "number"},
                {"api_name": "is_active", "label": "是否启用", "field_type": "boolean"},
            ],
        })
        assert resp.status_code == 201
        obj_data = resp.json()

        # Verify object appears in the API
        resp = requests.get(f"{API_URL}/custom-objects", headers={
            "Authorization": f"Bearer {api_token}",
        })
        objects = resp.json()
        names = [o["api_name"] for o in objects]
        assert obj_name in names

        # Verify fields
        assert len(obj_data["fields"]) == 3
        field_names = [f["api_name"] for f in obj_data["fields"]]
        assert "name" in field_names
        assert "quantity" in field_names
        assert "is_active" in field_names

    def test_dynamic_record_crud(self, logged_in_page, api_token):
        """UAT-CUS-02: Create, read, update, delete records on custom object."""
        # Create custom object with fields
        obj_name = f"custom_{fake.word()}"
        resp = requests.post(f"{API_URL}/custom-objects", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "api_name": obj_name,
            "label": "CRUD测试",
            "fields": [
                {"api_name": "title", "label": "标题", "field_type": "text", "is_required": True},
                {"api_name": "score", "label": "分数", "field_type": "number"},
            ],
        })
        obj_id = resp.json()["id"]

        # CREATE record
        title = fake.sentence(nb_words=3)
        score = fake.random_int(1, 100)
        create_resp = requests.post(f"{API_URL}/custom-objects/{obj_id}/records", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"fields": {"title": title, "score": score}})
        assert create_resp.status_code == 201
        record_id = create_resp.json()["id"]

        # READ record
        get_resp = requests.get(f"{API_URL}/custom-objects/{obj_id}/records/{record_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert get_resp.status_code == 200
        assert get_resp.json()["fields"]["title"] == title
        assert get_resp.json()["fields"]["score"] == score

        # UPDATE record
        new_score = fake.random_int(1, 100)
        update_resp = requests.put(f"{API_URL}/custom-objects/{obj_id}/records/{record_id}", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"fields": {"score": new_score}})
        assert update_resp.status_code == 200
        assert update_resp.json()["fields"]["score"] == new_score

        # LIST records
        list_resp = requests.get(f"{API_URL}/custom-objects/{obj_id}/records", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] >= 1

        # DELETE record
        del_resp = requests.delete(f"{API_URL}/custom-objects/{obj_id}/records/{record_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert del_resp.status_code == 204

        # Verify deleted
        get_resp = requests.get(f"{API_URL}/custom-objects/{obj_id}/records/{record_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert get_resp.status_code == 404

    def test_universal_api_by_name(self, logged_in_page, api_token):
        """UAT-CUS-03: Universal API by object name."""
        # Create object
        obj_name = f"custom_{fake.word()}"
        requests.post(f"{API_URL}/custom-objects", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "api_name": obj_name,
            "label": "通用API测试",
            "fields": [{"api_name": "desc", "label": "描述", "field_type": "text"}],
        })

        # Create record via universal API
        desc_text = fake.sentence()
        resp = requests.post(f"{API_URL}/custom-objects/by-name/{obj_name}/records", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"fields": {"desc": desc_text}})
        assert resp.status_code == 201
        assert resp.json()["fields"]["desc"] == desc_text

        # List via universal API
        resp = requests.get(f"{API_URL}/custom-objects/by-name/{obj_name}/records", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_add_field_to_existing_object(self, logged_in_page, api_token):
        """UAT-CUS-04: Add field to existing custom object."""
        # Create object with one field
        obj_name = f"custom_{fake.word()}"
        resp = requests.post(f"{API_URL}/custom-objects", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "api_name": obj_name,
            "label": "添加字段测试",
            "fields": [{"api_name": "f1", "label": "字段1", "field_type": "text"}],
        })
        obj_id = resp.json()["id"]

        # Add a new field
        resp = requests.post(f"{API_URL}/custom-objects/{obj_id}/fields", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"api_name": "f2", "label": "字段2", "field_type": "number"})
        assert resp.status_code == 201

        # Verify field count
        resp = requests.get(f"{API_URL}/custom-objects/{obj_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert len(resp.json()["fields"]) == 2

        # Create record with both fields
        resp = requests.post(f"{API_URL}/custom-objects/{obj_id}/records", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={"fields": {"f1": "hello", "f2": 42}})
        assert resp.status_code == 201
        assert resp.json()["fields"]["f2"] == 42

    def test_delete_custom_object(self, logged_in_page, api_token):
        """UAT-CUS-05: Delete custom object (and its dynamic table)."""
        obj_name = f"custom_{fake.word()}"
        resp = requests.post(f"{API_URL}/custom-objects", headers={
            "Authorization": f"Bearer {api_token}",
        }, json={
            "api_name": obj_name,
            "label": "删除测试",
            "fields": [{"api_name": "f1", "label": "字段1", "field_type": "text"}],
        })
        obj_id = resp.json()["id"]

        # Delete
        resp = requests.delete(f"{API_URL}/custom-objects/{obj_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 204

        # Verify deleted
        resp = requests.get(f"{API_URL}/custom-objects/{obj_id}", headers={
            "Authorization": f"Bearer {api_token}",
        })
        assert resp.status_code == 404