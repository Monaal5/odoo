import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_audit_trail_logging_and_retrieval():
    """Verify POST + GET /audit matches the specification examples."""
    entries = [
        {"user_id": "Monaal", "action": "CREATE", "entity": "Product", "entity_id": "PRD-101"},
        {"user_id": "Rahul", "action": "VALIDATE", "entity": "Receipt", "entity_id": "REC-202"},
        {"user_id": "Admin", "action": "ADJUST", "entity": "Stock", "entity_id": "STL001"},
    ]

    for entry in entries:
        response = client.post("/api/v1/audit", json=entry)
        assert response.status_code == 201, f"POST /audit failed: {response.json()}"
        data = response.json()
        assert data["user_id"] == entry["user_id"]
        assert data["action"] == entry["action"]
        assert data["entity"] == entry["entity"]

    # Retrieve all audit logs
    response = client.get("/api/v1/audit")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 3

    # Filter by user
    user_resp = client.get("/api/v1/audit?user_id=Monaal")
    assert user_resp.status_code == 200
    user_logs = user_resp.json()
    assert any(l["user_id"] == "Monaal" for l in user_logs)


def test_mobile_get_tasks():
    """GET /mobile/tasks returns a list (possibly empty)."""
    response = client.get("/mobile/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)


def test_mobile_post_count_and_get_stock():
    """POST /mobile/count then GET /mobile/stock/{sku} returns consistent data."""
    count_payload = {"sku": "STL001", "qty": 42, "location": "Rack-B2"}

    # Submit stock count
    count_resp = client.post("/mobile/count", json=count_payload)
    assert count_resp.status_code == 200, f"POST /mobile/count failed: {count_resp.json()}"
    res_data = count_resp.json()
    assert res_data["sku"] == "STL001"
    assert res_data["qty"] == 42
    assert res_data["location"] == "Rack-B2"
    assert res_data["status"] == "success"

    # Fetch current stock — qty must match the count we just submitted
    stock_resp = client.get("/mobile/stock/STL001")
    assert stock_resp.status_code == 200, f"GET /mobile/stock failed: {stock_resp.json()}"
    stock_data = stock_resp.json()
    assert stock_data["sku"] == "STL001"
    assert stock_data["qty"] == 42.0


def test_stock_reports_csv_and_pdf():
    """Report endpoints should return downloadable files."""
    csv_resp = client.get("/api/v1/reports/stock/csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]

    pdf_resp = client.get("/api/v1/reports/stock/pdf")
    assert pdf_resp.status_code == 200
    assert "application/pdf" in pdf_resp.headers["content-type"]
