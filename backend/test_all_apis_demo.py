import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
API_V1 = f"{BASE_URL}/api/v1"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(method, endpoint, response):
    status_symbol = "[SUCCESS]" if response.status_code in [200, 201, 204] else "[FAILED]"
    print(f"\n{status_symbol} {method} {endpoint} -> Status Code: {response.status_code}")
    if response.text:
        try:
            parsed = response.json()
            print(json.dumps(parsed, indent=2))
        except Exception:
            print(response.text)

def main():
    print_section("STOCKSENSE INVENTORY MANAGEMENT SYSTEM - COMPLETE API TEST DEMO")

    # 1. System & Health Check
    print_section("1. SYSTEM & HEALTH CHECK")
    r = requests.get(f"{BASE_URL}/")
    print_result("GET", "/", r)

    r = requests.get(f"{API_V1}/health")
    print_result("GET", "/api/v1/health", r)

    # 2. Master Items CRUD
    print_section("2. MASTER ITEMS API")
    item_payload = {
        "title": "Industrial Steel Rod (Grade A)",
        "description": "High tensile strength steel rod for construction",
        "category": "Raw Materials",
        "is_active": True
    }
    r = requests.post(f"{API_V1}/items", json=item_payload)
    print_result("POST", "/api/v1/items", r)
    item_data = r.json()
    created_item_id = item_data["id"]

    r = requests.get(f"{API_V1}/items")
    print_result("GET", "/api/v1/items", r)

    r = requests.get(f"{API_V1}/items/{created_item_id}")
    print_result("GET", f"/api/v1/items/{created_item_id}", r)

    update_payload = {"description": "Updated high tensile strength 12mm steel rod"}
    r = requests.put(f"{API_V1}/items/{created_item_id}", json=update_payload)
    print_result("PUT", f"/api/v1/items/{created_item_id}", r)

    # 3. Receipts API (Incoming Inventory)
    print_section("3. RECEIPTS API (INCOMING INVENTORY)")
    receipt_payload = {
        "supplier_name": "Apex Metallurgical Supplies",
        "items": [
            {"product_id": created_item_id, "location_id": 1, "quantity": 100}
        ]
    }
    r = requests.post(f"{API_V1}/receipts", json=receipt_payload)
    print_result("POST", "/api/v1/receipts", r)
    receipt_id = r.json()["id"]

    r = requests.get(f"{API_V1}/receipts")
    print_result("GET", "/api/v1/receipts", r)

    print("\nValidating Receipt #", receipt_id)
    r = requests.post(f"{API_V1}/receipts/{receipt_id}/validate")
    print_result("POST", f"/api/v1/receipts/{receipt_id}/validate", r)

    # 4. Deliveries API (Outgoing Inventory)
    print_section("4. DELIVERIES API (OUTGOING INVENTORY)")
    delivery_payload = {
        "customer_name": "Global Construction Corp",
        "items": [
            {"product_id": created_item_id, "location_id": 1, "quantity": 25}
        ]
    }
    r = requests.post(f"{API_V1}/deliveries", json=delivery_payload)
    print_result("POST", "/api/v1/deliveries", r)
    delivery_id = r.json()["id"]

    r = requests.get(f"{API_V1}/deliveries")
    print_result("GET", "/api/v1/deliveries", r)

    print("\nValidating Delivery #", delivery_id)
    r = requests.post(f"{API_V1}/deliveries/{delivery_id}/validate")
    print_result("POST", f"/api/v1/deliveries/{delivery_id}/validate", r)

    # 5. Internal Transfers API
    print_section("5. INTERNAL TRANSFERS API")
    transfer_payload = {
        "product_id": created_item_id,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 15
    }
    r = requests.post(f"{API_V1}/transfers", json=transfer_payload)
    print_result("POST", "/api/v1/transfers", r)
    transfer_id = r.json()["id"]

    print("\nValidating Internal Transfer #", transfer_id)
    r = requests.post(f"{API_V1}/transfers/{transfer_id}/validate")
    print_result("POST", f"/api/v1/transfers/{transfer_id}/validate", r)

    # 6. Physical Count Adjustments API
    print_section("6. STOCK ADJUSTMENTS API")
    adjustment_payload = {
        "product_id": created_item_id,
        "location_id": 1,
        "counted_qty": 58,
        "reason": "Routine inventory audit - 2 units missing/damaged"
    }
    r = requests.post(f"{API_V1}/adjustments", json=adjustment_payload)
    print_result("POST", "/api/v1/adjustments", r)

    # 7. Stock Ledger Audit Log API
    print_section("7. STOCK LEDGER AUDIT TRAIL")
    r = requests.get(f"{API_V1}/ledger/history?product_id={created_item_id}")
    print_result("GET", f"/api/v1/ledger/history?product_id={created_item_id}", r)

    # 8. Operational Dashboard KPIs
    print_section("8. DASHBOARD KPIS & LIVE STOCK LEVELS")
    r = requests.get(f"{API_V1}/dashboard/kpis")
    print_result("GET", "/api/v1/dashboard/kpis", r)

if __name__ == "__main__":
    main()
