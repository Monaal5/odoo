"""
Tests for Forecasting & Analytics APIs.

Run with:
    python -m pytest tests/test_forecast_analytics.py -v
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


def get_auth_headers() -> dict:
    """Register/login an inventory manager and return Bearer auth headers."""
    uid = uuid.uuid4().hex[:6]
    creds = {
        "email": f"forecast_tester_{uid}@example.com",
        "password": "TestPassword123!",
        "name": f"Forecast Tester {uid}",
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


class TestForecastAPI:

    @pytest.fixture(autouse=True)
    def setup_headers(self):
        self.headers = get_auth_headers()

    def test_get_product_forecast(self):
        """Test GET /forecast/{product_id} matching required JSON response shape."""
        # 1. Create a sample product
        prod_resp = client.post(
            f"{PREFIX}/products",
            json={
                "name": "Steel Rod",
                "sku": f"SKU-STEEL-{uuid.uuid4().hex[:4]}",
                "unit_of_measure": "units",
                "reorder_min": 10,
                "reorder_max": 150,
            },
            headers=self.headers,
        )
        assert prod_resp.status_code == 201
        prod_id = prod_resp.json()["id"]

        # 2. Get forecast
        resp = client.get(f"{PREFIX}/forecast/{prod_id}", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "product" in data
        assert data["product"] == "Steel Rod"
        assert "days_to_stockout" in data
        assert "recommended_order" in data
        assert isinstance(data["days_to_stockout"], int)
        assert isinstance(data["recommended_order"], (int, float))

    def test_list_forecasts(self):
        resp = client.get(f"{PREFIX}/forecast", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_forecast_requires_auth(self):
        resp = client.get(f"{PREFIX}/forecast")
        assert resp.status_code in (401, 403)


class TestAnalyticsAPI:

    @pytest.fixture(autouse=True)
    def setup_headers(self):
        self.headers = get_auth_headers()

    def test_get_anomalies(self):
        """Test GET /analytics/anomalies matching required JSON response shape."""
        resp = client.get(f"{PREFIX}/analytics/anomalies", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "anomalies" in data
        assert "total_anomalies" in data
        assert isinstance(data["anomalies"], list)

        if data["anomalies"]:
            sample = data["anomalies"][0]
            assert "severity" in sample
            assert "message" in sample

    def test_get_analytics_summary(self):
        resp = client.get(f"{PREFIX}/analytics/summary", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_consumption_30d" in data
        assert "total_shrinkage_30d" in data
        assert "anomalies_count" in data
