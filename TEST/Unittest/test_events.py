"""Tests for Event (Visit) and Task CRUD endpoints, including check-in/check-out."""


class TestListEvents:
    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/events", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_data(self, client, auth_headers):
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Client Meeting", "start_datetime": "2026-07-01T09:00:00",
        })
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Follow-up Call", "start_datetime": "2026-07-02T14:00:00",
        })
        resp = await client.get("/api/events", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_search_by_subject(self, client, auth_headers):
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Product Demo", "start_datetime": "2026-07-10T10:00:00",
        })
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Contract Review", "start_datetime": "2026-07-11T10:00:00",
        })
        resp = await client.get("/api/events?search=Product", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["subject"] == "Product Demo"

    async def test_filter_by_status(self, client, auth_headers):
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Planned Visit", "start_datetime": "2026-08-01T09:00:00",
        })
        resp = await client.get("/api/events?status_filter=planned", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1

    async def test_filter_by_type(self, client, auth_headers):
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Video Call", "type": "Video Conference",
            "start_datetime": "2026-08-01T09:00:00",
        })
        resp = await client.get("/api/events?type_filter=Video+Conference", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1


class TestCreateEvent:
    async def test_create_minimal(self, client, auth_headers):
        resp = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Quick Meeting", "start_datetime": "2026-07-15T10:00:00",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["subject"] == "Quick Meeting"
        assert data["status"] == "planned"

    async def test_create_full(self, client, auth_headers):
        resp = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Full Visit Plan",
            "type": "Visit",
            "start_datetime": "2026-07-20T09:00:00",
            "end_datetime": "2026-07-20T11:00:00",
            "purpose": "Discuss partnership",
            "preparation_notes": "Bring brochures",
            "location": "Client HQ",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "Visit"
        assert data["purpose"] == "Discuss partnership"
        assert data["location"] == "Client HQ"

    async def test_create_with_what_id(self, client, auth_headers):
        # Create an account first
        acct = await client.post("/api/accounts", headers=auth_headers, json={"name": "Event Test Corp"})
        acc_id = acct.json()["id"]
        resp = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Account Visit",
            "start_datetime": "2026-07-25T14:00:00",
            "what_id": acc_id,
            "what_type": "account",
        })
        assert resp.status_code == 201
        assert resp.json()["what_id"] == acc_id

    async def test_create_missing_subject(self, client, auth_headers):
        resp = await client.post("/api/events", headers=auth_headers, json={
            "start_datetime": "2026-07-15T10:00:00",
        })
        assert resp.status_code == 422

    async def test_create_missing_start_datetime(self, client, auth_headers):
        resp = await client.post("/api/events", headers=auth_headers, json={
            "subject": "No Date",
        })
        assert resp.status_code == 422


class TestGetEvent:
    async def test_get_by_id(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Get Test", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        resp = await client.get(f"/api/events/{eid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["subject"] == "Get Test"

    async def test_get_not_found(self, client, auth_headers):
        resp = await client.get("/api/events/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateEvent:
    async def test_update(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Old Subject", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        resp = await client.put(f"/api/events/{eid}", headers=auth_headers, json={
            "subject": "Updated Subject",
            "description": "Added notes",
        })
        assert resp.status_code == 200
        assert resp.json()["subject"] == "Updated Subject"
        assert resp.json()["description"] == "Added notes"

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.put("/api/events/nonexistent", headers=auth_headers, json={
            "subject": "Nope",
        })
        assert resp.status_code == 404


class TestDeleteEvent:
    async def test_delete(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Delete Me", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        resp = await client.delete(f"/api/events/{eid}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/events/{eid}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client, auth_headers):
        resp = await client.delete("/api/events/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestCheckInOut:
    async def test_check_in(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Check-in Test", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        resp = await client.post(f"/api/events/{eid}/check-in", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "in_progress"
        assert data["actual_start_time"] is not None

    async def test_check_in_with_location(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Location Check-in", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        resp = await client.post(f"/api/events/{eid}/check-in?location=Office", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["location"] == "Office"

    async def test_check_in_not_planned(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Already Started", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        await client.post(f"/api/events/{eid}/check-in", headers=auth_headers)
        # Second check-in should fail
        resp = await client.post(f"/api/events/{eid}/check-in", headers=auth_headers)
        assert resp.status_code == 400

    async def test_check_out(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Full Cycle", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        await client.post(f"/api/events/{eid}/check-in", headers=auth_headers)
        resp = await client.post(f"/api/events/{eid}/check-out", headers=auth_headers,
                                 params={"description": "Great meeting", "outcome": "success"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["actual_end_time"] is not None
        assert data["outcome"] == "success"
        assert data["description"] == "Great meeting"

    async def test_check_out_without_check_in(self, client, auth_headers):
        create = await client.post("/api/events", headers=auth_headers, json={
            "subject": "No Check-in", "start_datetime": "2026-07-15T10:00:00",
        })
        eid = create.json()["id"]
        resp = await client.post(f"/api/events/{eid}/check-out", headers=auth_headers)
        assert resp.status_code == 400

    async def test_check_in_not_found(self, client, auth_headers):
        resp = await client.post("/api/events/nonexistent/check-in", headers=auth_headers)
        assert resp.status_code == 404

    async def test_check_out_not_found(self, client, auth_headers):
        resp = await client.post("/api/events/nonexistent/check-out", headers=auth_headers)
        assert resp.status_code == 404


class TestTaskCRUD:
    async def _create_event(self, client, auth_headers):
        resp = await client.post("/api/events", headers=auth_headers, json={
            "subject": "Task Event", "start_datetime": "2026-07-20T10:00:00",
        })
        return resp.json()["id"]

    async def test_create_task(self, client, auth_headers):
        eid = await self._create_event(client, auth_headers)
        resp = await client.post(f"/api/events/{eid}/tasks", headers=auth_headers, json={
            "subject": "Prepare materials",
        })
        assert resp.status_code == 201
        assert resp.json()["subject"] == "Prepare materials"
        assert resp.json()["status"] == "not_started"

    async def test_list_tasks(self, client, auth_headers):
        eid = await self._create_event(client, auth_headers)
        await client.post(f"/api/events/{eid}/tasks", headers=auth_headers, json={
            "subject": "Task 1",
        })
        await client.post(f"/api/events/{eid}/tasks", headers=auth_headers, json={
            "subject": "Task 2",
        })
        resp = await client.get(f"/api/events/{eid}/tasks", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_update_task(self, client, auth_headers):
        eid = await self._create_event(client, auth_headers)
        create = await client.post(f"/api/events/{eid}/tasks", headers=auth_headers, json={
            "subject": "Incomplete Task",
        })
        tid = create.json()["id"]
        resp = await client.put(f"/api/events/{eid}/tasks/{tid}", headers=auth_headers, json={
            "status": "completed",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    async def test_delete_task(self, client, auth_headers):
        eid = await self._create_event(client, auth_headers)
        create = await client.post(f"/api/events/{eid}/tasks", headers=auth_headers, json={
            "subject": "Delete Task",
        })
        tid = create.json()["id"]
        resp = await client.delete(f"/api/events/{eid}/tasks/{tid}", headers=auth_headers)
        assert resp.status_code == 204
        resp = await client.get(f"/api/events/{eid}/tasks", headers=auth_headers)
        assert len(resp.json()) == 0

    async def test_task_update_not_found(self, client, auth_headers):
        eid = await self._create_event(client, auth_headers)
        resp = await client.put(f"/api/events/{eid}/tasks/nonexistent", headers=auth_headers,
                                json={"subject": "Nope"})
        assert resp.status_code == 404

    async def test_task_delete_not_found(self, client, auth_headers):
        eid = await self._create_event(client, auth_headers)
        resp = await client.delete(f"/api/events/{eid}/tasks/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


class TestEventHistory:
    async def test_account_event_history(self, client, auth_headers):
        # Create account
        acct = await client.post("/api/accounts", headers=auth_headers, json={"name": "History Corp"})
        acc_id = acct.json()["id"]
        # Create event linked to account
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Account Visit 1", "start_datetime": "2026-07-10T10:00:00",
            "what_id": acc_id, "what_type": "account",
        })
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Account Visit 2", "start_datetime": "2026-07-11T10:00:00",
            "what_id": acc_id, "what_type": "account",
        })
        resp = await client.get(f"/api/events/by-account/{acc_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_opportunity_event_history(self, client, auth_headers, seeded_stages):
        # Create account first (opportunity requires account_id)
        acct = await client.post("/api/accounts", headers=auth_headers, json={"name": "Opp Corp"})
        acc_id = acct.json()["id"]
        # Use the first stage's actual ID from seeded_stages
        stage_id = seeded_stages[0].id
        opp = await client.post("/api/opportunities", headers=auth_headers, json={
            "name": "Event Opp", "stage_id": stage_id, "account_id": acc_id,
        })
        opp_id = opp.json()["id"]
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Opp Meeting", "start_datetime": "2026-07-12T14:00:00",
            "what_id": opp_id, "what_type": "opportunity",
        })
        resp = await client.get(f"/api/events/by-opportunity/{opp_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_contact_event_history(self, client, auth_headers):
        acct = await client.post("/api/accounts", headers=auth_headers, json={"name": "Con Corp"})
        acc_id = acct.json()["id"]
        contact = await client.post("/api/contacts", headers=auth_headers, json={
            "first_name": "John", "last_name": "Doe", "account_id": acc_id,
        })
        con_id = contact.json()["id"]
        await client.post("/api/events", headers=auth_headers, json={
            "subject": "Contact Call", "start_datetime": "2026-07-13T10:00:00",
            "who_id": con_id,
        })
        resp = await client.get(f"/api/events/by-contact/{con_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
