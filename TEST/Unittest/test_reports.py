"""Tests for Reports and Dashboards."""


class TestReportCRUD:
    async def test_create_report(self, client, auth_headers):
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "账户报表",
            "object_type": "account",
            "columns": ["id", "name", "industry", "phone"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "账户报表"
        assert data["object_type"] == "account"

    async def test_list_reports(self, client, auth_headers):
        await client.post("/api/reports", headers=auth_headers, json={
            "name": "Report 1", "object_type": "account",
        })
        await client.post("/api/reports", headers=auth_headers, json={
            "name": "Report 2", "object_type": "contact",
        })
        resp = await client.get("/api/reports", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    async def test_get_report(self, client, auth_headers):
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "Get Report", "object_type": "account",
        })
        rep_id = resp.json()["id"]
        resp = await client.get(f"/api/reports/{rep_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Report"

    async def test_update_report(self, client, auth_headers):
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "Original", "object_type": "account",
        })
        rep_id = resp.json()["id"]
        resp = await client.put(f"/api/reports/{rep_id}", headers=auth_headers, json={
            "name": "Updated", "columns": ["id", "name"],
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    async def test_delete_report(self, client, auth_headers):
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "Delete Me", "object_type": "account",
        })
        rep_id = resp.json()["id"]
        resp = await client.delete(f"/api/reports/{rep_id}", headers=auth_headers)
        assert resp.status_code == 204


class TestRunReport:
    async def test_run_account_report(self, client, auth_headers):
        await client.post("/api/accounts", headers=auth_headers, json={"name": "Acme", "industry": "Tech"})
        await client.post("/api/accounts", headers=auth_headers, json={"name": "Beta", "industry": "Finance"})

        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "All Accounts", "object_type": "account",
            "columns": ["id", "name", "industry"],
        })
        rep_id = resp.json()["id"]

        resp = await client.post(f"/api/reports/{rep_id}/run", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert "id" in data["columns"]
        assert "name" in data["columns"]
        assert len(data["rows"]) == 2

    async def test_run_report_with_filter(self, client, auth_headers):
        await client.post("/api/accounts", headers=auth_headers, json={"name": "Acme", "industry": "Tech"})
        await client.post("/api/accounts", headers=auth_headers, json={"name": "Beta", "industry": "Finance"})

        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "Filtered", "object_type": "account",
            "columns": ["id", "name"],
            "filters": [{"field": "industry", "operator": "eq", "value": "Tech"}],
        })
        rep_id = resp.json()["id"]

        resp = await client.post(f"/api/reports/{rep_id}/run", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["rows"][0][1] == "Acme"


class TestDashboardCRUD:
    async def test_create_dashboard(self, client, auth_headers):
        resp = await client.post("/api/dashboards", headers=auth_headers, json={"name": "销售概览"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "销售概览"

    async def test_list_dashboards(self, client, auth_headers):
        await client.post("/api/dashboards", headers=auth_headers, json={"name": "Dash 1"})
        await client.post("/api/dashboards", headers=auth_headers, json={"name": "Dash 2"})
        resp = await client.get("/api/dashboards", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_dashboard_with_components(self, client, auth_headers):
        resp = await client.post("/api/dashboards", headers=auth_headers, json={"name": "Main"})
        dash_id = resp.json()["id"]
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "Rep", "object_type": "account",
        })
        rep_id = resp.json()["id"]
        await client.post(f"/api/dashboards/{dash_id}/components", headers=auth_headers, json={
            "report_id": rep_id, "title": "账户统计", "chart_type": "bar",
            "position_x": 0, "position_y": 0, "width": 4, "height": 3,
        })
        resp = await client.get(f"/api/dashboards/{dash_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["components"]) == 1
        assert data["components"][0]["title"] == "账户统计"

    async def test_delete_dashboard(self, client, auth_headers):
        resp = await client.post("/api/dashboards", headers=auth_headers, json={"name": "Delete Me"})
        dash_id = resp.json()["id"]
        resp = await client.delete(f"/api/dashboards/{dash_id}", headers=auth_headers)
        assert resp.status_code == 204


class TestDashboardComponent:
    async def test_add_component(self, client, auth_headers):
        resp = await client.post("/api/dashboards", headers=auth_headers, json={"name": "D"})
        dash_id = resp.json()["id"]
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "R", "object_type": "account",
        })
        rep_id = resp.json()["id"]
        resp = await client.post(f"/api/dashboards/{dash_id}/components", headers=auth_headers, json={
            "report_id": rep_id, "title": "Tile", "chart_type": "pie",
        })
        assert resp.status_code == 200
        assert resp.json()["chart_type"] == "pie"

    async def test_delete_component(self, client, auth_headers):
        resp = await client.post("/api/dashboards", headers=auth_headers, json={"name": "D2"})
        dash_id = resp.json()["id"]
        resp = await client.post("/api/reports", headers=auth_headers, json={
            "name": "R2", "object_type": "account",
        })
        rep_id = resp.json()["id"]
        resp = await client.post(f"/api/dashboards/{dash_id}/components", headers=auth_headers, json={
            "report_id": rep_id, "title": "Tile",
        })
        comp_id = resp.json()["id"]
        resp = await client.delete(
            f"/api/dashboards/{dash_id}/components/{comp_id}", headers=auth_headers
        )
        assert resp.status_code == 204
