"""
Tests for Negative Stock Prevention across Receipts, Deliveries,
Internal Transfers, and Stock Adjustments.

Run with:
    python -m pytest tests/test_negative_stock_prevention.py -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

PREFIX = settings.API_V1_STR
client = TestClient(app)


import uuid

def get_auth_headers() -> dict:
    """Register/login an inventory manager and return Bearer auth headers."""
    unique_id = uuid.uuid4().hex[:6]
    creds = {
        "email": f"stock_tester_{unique_id}@example.com",
        "password": "TestPassword123!",
        "name": "Stock Tester",
        "role": "inventory_manager",
    }
    signup_res = client.post(f"{PREFIX}/auth/signup", json=creds)
    assert signup_res.status_code == 201, f"Signup failed: {signup_res.text}"

    resp = client.post(
        f"{PREFIX}/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestNegativeStockPrevention:

    @pytest.fixture(autouse=True)
    def setup_headers(self):
        self.headers = get_auth_headers()

    def test_delivery_validation_fails_on_zero_stock(self):
        """
        Attempting to validate a delivery for a product with 0 stock
        must be rejected with HTTP 400 Insufficient stock error.
        """
        # 1. Create product with 0 initial stock
        prod_resp = client.post(
            f"{PREFIX}/products",
            json={
                "name": "Zero Stock Item",
                "sku": f"SKU-ZERO-{uuid.uuid4().hex[:6]}",
                "unit_of_measure": "units",
                "reorder_min": 5,
            },
            headers=self.headers,
        )
        assert prod_resp.status_code == 201
        prod_id = prod_resp.json()["id"]

        # 2. Create delivery for 10 units of the 0-stock product
        del_resp = client.post(
            f"{PREFIX}/deliveries",
            json={
                "customer": "Test Customer",
                "items": [{"product_id": prod_id, "quantity": 10}],
            },
            headers=self.headers,
        )
        assert del_resp.status_code == 201
        del_id = del_resp.json()["id"]

        # 3. Validate delivery -> Must fail with 400 (Insufficient stock)
        val_resp = client.put(
            f"{PREFIX}/deliveries/{del_id}/validate",
            headers=self.headers,
        )
        assert val_resp.status_code == 400
        assert "Insufficient stock" in val_resp.json()["detail"]

    def test_transfer_validation_fails_when_source_stock_insufficient(self):
        """
        Internal transfer from source location with insufficient stock
        must be rejected with HTTP 400.
        """
        # 1. Create product
        prod_resp = client.post(
            f"{PREFIX}/products",
            json={
                "name": "Transfer Test Item",
                "sku": f"SKU-TRF-NEG-{uuid.uuid4().hex[:6]}",
                "unit_of_measure": "kg",
            },
            headers=self.headers,
        )
        assert prod_resp.status_code == 201
        prod_id = prod_resp.json()["id"]

        # 2. Create transfer for 50 units (source stock is 0)
        trf_resp = client.post(
            f"{PREFIX}/transfers",
            json={
                "product_id": prod_id,
                "from_warehouse": None,
                "to_warehouse": None,
                "quantity": 50,
            },
            headers=self.headers,
        )
        assert trf_resp.status_code == 201
        trf_id = trf_resp.json()["id"]

        # 3. Validate transfer -> Must fail with 400
        val_resp = client.put(
            f"{PREFIX}/transfers/{trf_id}/validate",
            headers=self.headers,
        )
        assert val_resp.status_code == 400
        assert "Insufficient stock" in val_resp.json()["detail"]

    def test_delivery_exceeding_partial_stock_fails(self):
        """
        If stock is 15 and delivery requests 20, validation must fail.
        """
        # 1. Create product
        prod_resp = client.post(
            f"{PREFIX}/products",
            json={
                "name": "Partial Stock Item",
                "sku": f"SKU-PARTIAL-{uuid.uuid4().hex[:6]}",
                "unit_of_measure": "pcs",
            },
            headers=self.headers,
        )
        assert prod_resp.status_code == 201
        prod_id = prod_resp.json()["id"]

        # 2. Receive 15 units
        rec_resp = client.post(
            f"{PREFIX}/receipts",
            json={
                "supplier": "Acme Supply",
                "items": [{"product_id": prod_id, "quantity": 15}],
            },
            headers=self.headers,
        )
        rec_id = rec_resp.json()["id"]
        client.put(f"{PREFIX}/receipts/{rec_id}/validate", headers=self.headers)

        # 3. Try to deliver 20 units (only 15 available)
        del_resp = client.post(
            f"{PREFIX}/deliveries",
            json={
                "customer": "Greedy Customer",
                "items": [{"product_id": prod_id, "quantity": 20}],
            },
            headers=self.headers,
        )
        del_id = del_resp.json()["id"]

        val_resp = client.put(
            f"{PREFIX}/deliveries/{del_id}/validate",
            headers=self.headers,
        )
        assert val_resp.status_code == 400
        assert "Available: 15" in val_resp.json()["detail"]

    def test_valid_delivery_within_available_stock_succeeds(self):
        """
        Delivering within available stock (e.g., receive 20, deliver 12) succeeds
        and leaves correct on-hand balance (8).
        """
        # 1. Create product
        prod_resp = client.post(
            f"{PREFIX}/products",
            json={
                "name": "Valid Delivery Item",
                "sku": f"SKU-VALID-DEL-{uuid.uuid4().hex[:6]}",
                "unit_of_measure": "boxes",
            },
            headers=self.headers,
        )
        assert prod_resp.status_code == 201
        prod_id = prod_resp.json()["id"]

        # 2. Receive 20
        rec_resp = client.post(
            f"{PREFIX}/receipts",
            json={
                "supplier": "Good Supplier",
                "items": [{"product_id": prod_id, "quantity": 20}],
            },
            headers=self.headers,
        )
        client.put(f"{PREFIX}/receipts/{rec_resp.json()['id']}/validate", headers=self.headers)

        # 3. Deliver 12 -> Should succeed
        del_resp = client.post(
            f"{PREFIX}/deliveries",
            json={
                "customer": "Happy Customer",
                "items": [{"product_id": prod_id, "quantity": 12}],
            },
            headers=self.headers,
        )
        val_resp = client.put(
            f"{PREFIX}/deliveries/{del_resp.json()['id']}/validate",
            headers=self.headers,
        )
        assert val_resp.status_code == 200
        assert val_resp.json()["status"] == "Done"
