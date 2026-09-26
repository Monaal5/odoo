import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert data["docs"] == "/docs"

def test_health_check():
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert "database" in data
    assert "odoo_connection" in data

def test_item_crud_flow():
    # 1. Create Item
    payload = {
        "title": "Hackathon Demo Product",
        "description": "A sample item created for testing API flow",
        "category": "Integration",
        "is_active": True,
        "odoo_ref_id": 42
    }
    create_res = client.post(f"{settings.API_V1_STR}/items", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["title"] == payload["title"]
    item_id = created_data["id"]

    # 2. Get Item by ID
    get_res = client.get(f"{settings.API_V1_STR}/items/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == item_id

    # 3. List Items
    list_res = client.get(f"{settings.API_V1_STR}/items")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Update Item
    update_payload = {"title": "Updated Hackathon Demo Product"}
    update_res = client.put(f"{settings.API_V1_STR}/items/{item_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Hackathon Demo Product"

    # 5. Delete Item
    del_res = client.delete(f"{settings.API_V1_STR}/items/{item_id}")
    assert del_res.status_code == 204
    
    # 6. Confirm Deletion
    get_again = client.get(f"{settings.API_V1_STR}/items/{item_id}")
    assert get_again.status_code == 404
