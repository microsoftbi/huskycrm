"""Tests for authentication endpoints."""

import pytest


class TestRegister:
    async def test_register_success(self, client):
        resp = await client.post("/api/auth/register", json={
            "username": "newuser", "email": "new@example.com",
            "password": "pass123", "display_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["display_name"] == "New User"
        assert data["is_active"] is True
        assert "password" not in data

    async def test_register_duplicate_username(self, client):
        await client.post("/api/auth/register", json={
            "username": "dup", "email": "a@a.com", "password": "pass123",
        })
        resp = await client.post("/api/auth/register", json={
            "username": "dup", "email": "b@b.com", "password": "pass123",
        })
        assert resp.status_code == 400

    async def test_register_duplicate_email(self, client):
        await client.post("/api/auth/register", json={
            "username": "u1", "email": "same@x.com", "password": "pass123",
        })
        resp = await client.post("/api/auth/register", json={
            "username": "u2", "email": "same@x.com", "password": "pass123",
        })
        assert resp.status_code == 400


class TestLogin:
    async def test_login_success(self, client):
        await client.post("/api/auth/register", json={
            "username": "u1", "email": "u1@x.com", "password": "secret",
        })
        resp = await client.post("/api/auth/login", json={
            "username": "u1", "password": "secret",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client):
        await client.post("/api/auth/register", json={
            "username": "u2", "email": "u2@x.com", "password": "correct",
        })
        resp = await client.post("/api/auth/login", json={
            "username": "u2", "password": "wrong",
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client):
        resp = await client.post("/api/auth/login", json={
            "username": "noone", "password": "x",
        })
        assert resp.status_code == 401


class TestRefresh:
    async def test_refresh_success(self, client, user_token):
        resp = await client.post("/api/auth/refresh", json={
            "refresh_token": user_token["refresh_token"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, client):
        resp = await client.post("/api/auth/refresh", json={
            "refresh_token": "invalid-token",
        })
        assert resp.status_code == 401


class TestMe:
    async def test_get_me(self, client, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_get_me_unauthorized(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 403
