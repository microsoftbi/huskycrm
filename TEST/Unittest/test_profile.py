"""Tests for Profile (update + password) and My-Territories endpoints."""


class TestUpdateProfile:
    async def test_update_display_name(self, client, auth_headers):
        resp = await client.put("/api/auth/profile", headers=auth_headers, json={
            "display_name": "New Display Name",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] == "New Display Name"

    async def test_update_email(self, client, auth_headers):
        resp = await client.put("/api/auth/profile", headers=auth_headers, json={
            "email": "updated@example.com",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "updated@example.com"

    async def test_update_both(self, client, auth_headers):
        resp = await client.put("/api/auth/profile", headers=auth_headers, json={
            "display_name": "Both Updated",
            "email": "both@example.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] == "Both Updated"
        assert data["email"] == "both@example.com"

    async def test_update_empty_body(self, client, auth_headers):
        resp = await client.put("/api/auth/profile", headers=auth_headers, json={})
        assert resp.status_code == 400

    async def test_update_unauthorized(self, client):
        resp = await client.put("/api/auth/profile", json={
            "display_name": "Hacker",
        })
        assert resp.status_code == 403


class TestChangePassword:
    async def test_change_password_success(self, client, auth_headers, user_token):
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "current_password": "testpass123",
            "new_password": "newpass456",
            "confirm_password": "newpass456",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Password updated successfully"

        # Verify can login with new password
        resp = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "newpass456",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_change_password_wrong_current(self, client, auth_headers):
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "current_password": "wrongpass",
            "new_password": "newpass456",
            "confirm_password": "newpass456",
        })
        assert resp.status_code == 400
        assert "incorrect" in resp.json()["detail"].lower()

    async def test_change_password_mismatch(self, client, auth_headers):
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "current_password": "testpass123",
            "new_password": "newpass456",
            "confirm_password": "different789",
        })
        assert resp.status_code == 400
        assert "do not match" in resp.json()["detail"].lower()

    async def test_change_password_too_short(self, client, auth_headers):
        resp = await client.put("/api/auth/password", headers=auth_headers, json={
            "current_password": "testpass123",
            "new_password": "ab",
            "confirm_password": "ab",
        })
        assert resp.status_code == 400
        assert "at least 6" in resp.json()["detail"].lower()

    async def test_change_password_unauthorized(self, client):
        resp = await client.put("/api/auth/password", json={
            "current_password": "x",
            "new_password": "y",
            "confirm_password": "y",
        })
        assert resp.status_code == 403


class TestMyTerritories:
    async def test_my_territories_empty(self, client, auth_headers):
        """User has no territory memberships initially."""
        resp = await client.get("/api/auth/my-territories", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_my_territories_structure(self, client, auth_headers):
        """Verify response structure even when empty."""
        resp = await client.get("/api/auth/my-territories", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Each item should have the expected fields if any exist
        if len(data) > 0:
            item = data[0]
            assert "territory_id" in item
            assert "territory_name" in item
            assert "role" in item
            assert "manager_name" in item

    async def test_my_territories_unauthorized(self, client):
        resp = await client.get("/api/auth/my-territories")
        assert resp.status_code == 403
