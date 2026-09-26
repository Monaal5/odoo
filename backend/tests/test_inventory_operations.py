import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import engine, Base
from app.core.config import settings

from app.api.deps import get_current_user, require_manager

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Reset database tables and override auth dependencies before running tests."""
    mock_user = {
        "id": "1",
        "name": "Test Manager",
        "email": "manager@example.com",
        "role": "inventory_manager",
        "is_active": True,
    }
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[require_manager] = lambda: mock_user

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    app.dependency_overrides.clear()

def test_full_inventory_operations_flow():
    """
    Test the complete Deliverable sequence:
    Receive -> Deliver -> Transfer -> Adjustment all update stock and ledger correctly.
    """

    # 1. RECEIPT: Receive 100 units of Product 101 at Location 1 (Main Warehouse)
    receipt_payload = {
        "supplier_name": "Steel Corp Supplier",
        "items": [
            {"product_id": 101, "location_id": 1, "quantity": 100}
        ]
    }
    rec_res = client.post(f"{settings.API_V1_STR}/receipts", json=receipt_payload)
    assert rec_res.status_code == 201
    receipt_data = rec_res.json()
    receipt_id = receipt_data["id"]
    assert receipt_data["status"] == "Draft"

    # Validate Receipt -> Stock increases by 100
    val_rec = client.post(f"{settings.API_V1_STR}/receipts/{receipt_id}/validate")
    assert val_rec.status_code == 200
    assert val_rec.json()["status"] == "Done"

    # Check Dashboard KPI & Stock Level -> Location 1 should have 100
    kpi_res1 = client.get(f"{settings.API_V1_STR}/dashboard/kpis")
    assert kpi_res1.status_code == 200
    stock_map1 = { (item["product_id"], item["location_id"]): item["quantity"] for item in kpi_res1.json()["stock_levels"] }
    assert stock_map1[(101, 1)] == 100

    # 2. DELIVERY: Ship 30 units of Product 101 from Location 1
    delivery_payload = {
        "customer_name": "Acme Industries",
        "items": [
            {"product_id": 101, "location_id": 1, "quantity": 30}
        ]
    }
    del_res = client.post(f"{settings.API_V1_STR}/deliveries", json=delivery_payload)
    assert del_res.status_code == 201
    delivery_id = del_res.json()["id"]

    # Validate Delivery -> Stock decreases to 70
    val_del = client.post(f"{settings.API_V1_STR}/deliveries/{delivery_id}/validate")
    assert val_del.status_code == 200
    assert val_del.json()["status"] == "Done"

    kpi_res2 = client.get(f"{settings.API_V1_STR}/dashboard/kpis")
    stock_map2 = { (item["product_id"], item["location_id"]): item["quantity"] for item in kpi_res2.json()["stock_levels"] }
    assert stock_map2[(101, 1)] == 70

    # 3. INTERNAL TRANSFER: Move 20 units of Product 101 from Location 1 (Main) to Location 2 (Rack B)
    transfer_payload = {
        "product_id": 101,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 20
    }
    trf_res = client.post(f"{settings.API_V1_STR}/transfers", json=transfer_payload)
    assert trf_res.status_code == 201
    transfer_id = trf_res.json()["id"]

    # Validate Transfer -> Location 1 = 50, Location 2 = 20
    val_trf = client.post(f"{settings.API_V1_STR}/transfers/{transfer_id}/validate")
    assert val_trf.status_code == 200
    assert val_trf.json()["status"] == "Done"

    kpi_res3 = client.get(f"{settings.API_V1_STR}/dashboard/kpis")
    stock_map3 = { (item["product_id"], item["location_id"]): item["quantity"] for item in kpi_res3.json()["stock_levels"] }
    assert stock_map3[(101, 1)] == 50
    assert stock_map3[(101, 2)] == 20

    # 4. STOCK ADJUSTMENT: Counted physical stock at Location 1 is 46 (4 units damaged/lost)
    adj_payload = {
        "product_id": 101,
        "location_id": 1,
        "counted_qty": 46,
        "reason": "Damaged goods found during cycle count"
    }
    adj_res = client.post(f"{settings.API_V1_STR}/adjustments", json=adj_payload)
    assert adj_res.status_code == 201
    adj_data = adj_res.json()
    assert adj_data["system_qty"] == 50
    assert adj_data["counted_qty"] == 46
    assert adj_data["delta_qty"] == -4

    # Verify final stock level at Location 1 is 46
    kpi_res4 = client.get(f"{settings.API_V1_STR}/dashboard/kpis")
    stock_map4 = { (item["product_id"], item["location_id"]): item["quantity"] for item in kpi_res4.json()["stock_levels"] }
    assert stock_map4[(101, 1)] == 46

    # 5. STOCK LEDGER AUDIT HISTORY: Verify all events are present in history
    ledger_res = client.get(f"{settings.API_V1_STR}/ledger/history?product_id=101")
    assert ledger_res.status_code == 200
    history = ledger_res.json()
    # History contains: ADJUSTMENT (-4), TRANSFER_IN (+20), TRANSFER_OUT (-20), DELIVERY (-30), RECEIPT (+100)
    assert len(history) >= 5
    doc_types = [h["source_doc_type"] for h in history]
    assert "RECEIPT" in doc_types
    assert "DELIVERY" in doc_types
    assert "TRANSFER_OUT" in doc_types
    assert "TRANSFER_IN" in doc_types
    assert "ADJUSTMENT" in doc_types
