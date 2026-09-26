"""
Tests for User Management, Profile, and Reports APIs.

Run with:
    python -m pytest tests/test_user_reports.py -v
"""
import uuid
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

PREFIX = settings.API_V1_STR
client = TestClient(app)


def get_manager_auth_headers() -> dict:
    """Register/login an inventory manager user and return Bearer auth header."""
    uid = uuid.uuid4().hex[:6]
    creds = {
        "email": f"manager_{uid}@example.com",
        "password": "Password123!",
        "name": f"Manager {uid}",
        "role": "inventory_manager",
    }
    client.post(f"{PREFIX}/auth/signup", json=creds)
    resp = client.post(
        f"{PREFIX}/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_staff_auth_headers() -> dict:
    """Register/login a warehouse staff user and return Bearer auth header."""
    uid = uuid.uuid4().hex[:6]
    creds = {
        "email": f"staff_{uid}@example.com",
        "password": "Password123!",
        "name": f"Staff {uid}",
        "role": "warehouse_staff",
    }
    client.post(f"{PREFIX}/auth/signup", json=creds)
    resp = client.post(
        f"{PREFIX}/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestProfileAPI:

    def test_get_profile(self):
        headers = get_manager_auth_headers()
        resp = client.get(f"{PREFIX}/profile", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "email" in data
        assert data["role"] == "inventory_manager"

    def test_update_profile_name(self):
        headers = get_manager_auth_headers()
        new_name = f"Updated Name {uuid.uuid4().hex[:4]}"
        resp = client.put(
            f"{PREFIX}/profile",
            json={"name": new_name},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == new_name

    def test_update_profile_unauthorized(self):
        resp = client.get(f"{PREFIX}/profile")
        assert resp.status_code in (401, 403)


# ─────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestUserManagementAPI:

    def test_manager_can_list_users(self):
        headers = get_manager_auth_headers()
        resp = client.get(f"{PREFIX}/users", headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_staff_cannot_list_users(self):
        headers = get_staff_auth_headers()
        resp = client.get(f"{PREFIX}/users", headers=headers)
        assert resp.status_code == 403  # Forbidden for non-managers

    def test_manager_can_change_role(self):
        manager_headers = get_manager_auth_headers()

        # Create a target staff user
        staff_uid = uuid.uuid4().hex[:6]
        staff_creds = {
            "email": f"target_staff_{staff_uid}@example.com",
            "password": "Password123!",
            "name": f"Target Staff {staff_uid}",
            "role": "warehouse_staff",
        }
        client.post(f"{PREFIX}/auth/signup", json=staff_creds)
        login_res = client.post(
            f"{PREFIX}/auth/login",
            json={"email": staff_creds["email"], "password": staff_creds["password"]},
        )
        target_user_id = login_res.json()["user_id"]

        # Manager updates staff user to manager
        resp = client.put(
            f"{PREFIX}/users/{target_user_id}/role",
            json={"role": "inventory_manager"},
            headers=manager_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "inventory_manager"


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestReportsAPI:

    def test_export_stock_csv(self):
        headers = get_manager_auth_headers()
        resp = client.get(f"{PREFIX}/reports/stock/csv", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        content = resp.text
        assert "SKU" in content
        assert "Product" in content
        assert "Warehouse" in content
        assert "Qty" in content

    def test_export_stock_pdf(self):
        headers = get_manager_auth_headers()
        resp = client.get(f"{PREFIX}/reports/stock/pdf", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF")
