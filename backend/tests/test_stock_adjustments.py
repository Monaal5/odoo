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

def test_stock_adjustment_delta_computation_and_ledger_entry():
    """
    Test Developer 2 Stock Adjustment Spec:
    1. Initial Stock Level = 100 (via Receipt validation)
    2. Post Physical Count = 97 with reason "Damaged items"
    3. Verify system calculates Delta = -3
    4. Verify StockLevel becomes 97
    5. Verify Stock Ledger records Entry with delta = -3 and doc_type = ADJUSTMENT
    """
    # 1. Initialize Stock: Receive 100 units of Product 1 at Location/Warehouse 2
    receipt_payload = {
        "supplier_name": "Initial Supply Co",
        "items": [
            {"product_id": 1, "location_id": 2, "quantity": 100}
        ]
    }
    rec_res = client.post(f"{settings.API_V1_STR}/receipts", json=receipt_payload)
    assert rec_res.status_code == 201
    receipt_id = rec_res.json()["id"]

    val_res = client.post(f"{settings.API_V1_STR}/receipts/{receipt_id}/validate")
    assert val_res.status_code == 200

    # Verify initial stock level is 100
    kpi_before = client.get(f"{settings.API_V1_STR}/dashboard/kpis")
    stock_before = { (item["product_id"], item["location_id"]): item["quantity"] for item in kpi_before.json()["stock_levels"] }
    assert stock_before[(1, 2)] == 100

    # 2. Perform Stock Adjustment: Counted stock is 97 (using warehouse_id and counted_quantity fields)
    adj_payload = {
        "product_id": 1,
        "warehouse_id": 2,
        "counted_quantity": 97,
        "reason": "Damaged items"
    }
    adj_res = client.post(f"{settings.API_V1_STR}/adjustments", json=adj_payload)
    assert adj_res.status_code == 201
    adj_data = adj_res.json()

    # 3. Assert Delta Calculation
    assert adj_data["system_qty"] == 100
    assert adj_data["counted_qty"] == 97
    assert adj_data["delta_qty"] == -3
    assert adj_data["reason"] == "Damaged items"

    # 4. Assert StockLevel updated to 97
    kpi_after = client.get(f"{settings.API_V1_STR}/dashboard/kpis")
    stock_after = { (item["product_id"], item["location_id"]): item["quantity"] for item in kpi_after.json()["stock_levels"] }
    assert stock_after[(1, 2)] == 97

    # 5. Assert Stock Ledger history entry with delta -3
    ledger_res = client.get(f"{settings.API_V1_STR}/ledger?product_id=1")
    assert ledger_res.status_code == 200
    ledger_entries = ledger_res.json()
    
    # Latest ledger entry must be the ADJUSTMENT with delta_qty = -3
    latest_adj_entry = next(e for e in ledger_entries if e["source_doc_type"] == "ADJUSTMENT")
    assert latest_adj_entry["qty_delta"] == -3
    assert latest_adj_entry["location_id"] == 2
