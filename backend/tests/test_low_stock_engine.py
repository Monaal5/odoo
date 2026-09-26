import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import engine, Base
from app.core.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Reset database tables before running low stock engine tests."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_low_stock_engine_alert_generation_and_resolution():
    """
    Test Low Stock Engine Logic:
    1. Set Reorder Rule: Min Stock = 20
    2. Receive 25 units -> Stock = 25 (25 >= 20, no alert)
    3. Deliver 7 units -> Stock = 18 (18 < 20 -> Alert generated!)
    4. Verify Active Alert visible via GET /api/v1/alerts
    5. Receive 10 units -> Stock = 28 (28 >= 20 -> Alert resolved!)
    """
    # 1. Set Reorder Rule (Min Stock = 20, Max Stock = 100)
    rule_payload = {
        "product_id": 1,
        "warehouse_id": 2,
        "min_qty": 20,
        "max_qty": 100
    }
    rule_res = client.post(f"{settings.API_V1_STR}/alerts/reorder-rules", json=rule_payload)
    assert rule_res.status_code == 201
    assert rule_res.json()["min_qty"] == 20

    # 2. Initial Receive: 25 units
    rec_payload = {
        "supplier_name": "Supplier A",
        "items": [{"product_id": 1, "location_id": 2, "quantity": 25}]
    }
    rec = client.post(f"{settings.API_V1_STR}/receipts", json=rec_payload).json()
    client.post(f"{settings.API_V1_STR}/receipts/{rec['id']}/validate")

    # Assert no active alerts yet (25 >= 20)
    alerts_1 = client.get(f"{settings.API_V1_STR}/alerts").json()
    assert len(alerts_1) == 0

    # 3. Deliver 7 units -> Stock drops to 18 (18 < 20)
    del_payload = {
        "customer_name": "Customer B",
        "items": [{"product_id": 1, "location_id": 2, "quantity": 7}]
    }
    d = client.post(f"{settings.API_V1_STR}/deliveries", json=del_payload).json()
    client.post(f"{settings.API_V1_STR}/deliveries/{d['id']}/validate")

    # 4. Assert Active Low-Stock Alert generated
    alerts_2 = client.get(f"{settings.API_V1_STR}/alerts").json()
    assert len(alerts_2) == 1
    alert = alerts_2[0]
    assert alert["product_id"] == 1
    assert alert["location_id"] == 2
    assert alert["current_stock"] == 18
    assert alert["min_stock"] == 20
    assert alert["status"] == "ACTIVE"

    # 5. Receive 10 units -> Stock increases to 28 (28 >= 20 -> Alert resolved)
    rec_payload2 = {
        "supplier_name": "Supplier A",
        "items": [{"product_id": 1, "location_id": 2, "quantity": 10}]
    }
    rec2 = client.post(f"{settings.API_V1_STR}/receipts", json=rec_payload2).json()
    client.post(f"{settings.API_V1_STR}/receipts/{rec2['id']}/validate")

    # 6. Assert Active Alerts list is now empty (alert automatically resolved)
    alerts_3 = client.get(f"{settings.API_V1_STR}/alerts").json()
    assert len(alerts_3) == 0
