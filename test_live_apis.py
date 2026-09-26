import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def print_section(title):
    print(f"\n{'='*60}\n --- {title} ---\n{'='*60}")

def test_endpoint(name, method, url, json_data=None, expected_status=200):
    print(f"\n> Testing {method} {url}...")
    start = time.time()
    try:
        if method == "GET":
            res = requests.get(url)
        elif method == "POST":
            res = requests.post(url, json=json_data)
        elif method == "PUT":
            res = requests.put(url, json=json_data)
        elif method == "DELETE":
            res = requests.delete(url)
        
        elapsed = round((time.time() - start) * 1000, 2)
        success = res.status_code == expected_status
        status_symbol = "[SUCCESS]" if success else "[FAILED]"
        
        print(f"{status_symbol} Status: {res.status_code} ({elapsed}ms)")
        try:
            payload = res.json()
            print(f"  Response: {json.dumps(payload, indent=2)[:300]}...")
            return payload
        except:
            print(f"  Response (Text): {res.text}")
            return res.text
    except Exception as e:
        print(f"[ERROR] Connecting to {url}: {e}")
        return None

def run_all_tests():
    print_section("1. SYSTEM & HEALTH ENDPOINTS")
    test_endpoint("Root", "GET", f"{BASE_URL}/")
    test_endpoint("Health Check", "GET", f"{API_V1}/health")

    print_section("2. ITEMS MANAGEMENT (CRUD)")
    item = test_endpoint("Create Item", "POST", f"{API_V1}/items", {
        "title": "Smart Barcode Scanner",
        "description": "Handheld terminal for StockSense picking",
        "category": "Hardware",
        "is_active": True
    }, expected_status=201)
    
    item_id = item["id"] if item and "id" in item else 1
    test_endpoint("List Items", "GET", f"{API_V1}/items")
    test_endpoint("Get Item by ID", "GET", f"{API_V1}/items/{item_id}")
    test_endpoint("Update Item", "PUT", f"{API_V1}/items/{item_id}", {"title": "Updated Barcode Scanner v2"})
    test_endpoint("Delete Item", "DELETE", f"{API_V1}/items/{item_id}", expected_status=204)

    print_section("3. INVENTORY RECEIPTS (INCOMING STOCK)")
    receipt = test_endpoint("Create Receipt", "POST", f"{API_V1}/receipts", {
        "supplier_name": "Apex Raw Materials Ltd",
        "items": [
            {"product_id": 301, "location_id": 1, "quantity": 200}
        ]
    }, expected_status=201)

    receipt_id = receipt["id"] if receipt and "id" in receipt else 1
    test_endpoint("Validate Receipt", "POST", f"{API_V1}/receipts/{receipt_id}/validate")
    test_endpoint("List Receipts", "GET", f"{API_V1}/receipts")

    print_section("4. INVENTORY DELIVERIES (OUTGOING STOCK)")
    delivery = test_endpoint("Create Delivery", "POST", f"{API_V1}/deliveries", {
        "customer_name": "Global Tech Logistics",
        "items": [
            {"product_id": 301, "location_id": 1, "quantity": 50}
        ]
    }, expected_status=201)

    delivery_id = delivery["id"] if delivery and "id" in delivery else 1
    test_endpoint("Validate Delivery", "POST", f"{API_V1}/deliveries/{delivery_id}/validate")
    test_endpoint("List Deliveries", "GET", f"{API_V1}/deliveries")

    print_section("5. INTERNAL TRANSFERS")
    transfer = test_endpoint("Create Transfer", "POST", f"{API_V1}/transfers", {
        "product_id": 301,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 40
    }, expected_status=201)

    transfer_id = transfer["id"] if transfer and "id" in transfer else 1
    test_endpoint("Validate Transfer", "POST", f"{API_V1}/transfers/{transfer_id}/validate")

    print_section("6. STOCK ADJUSTMENTS (COUNT RECONCILIATION)")
    test_endpoint("Create Adjustment", "POST", f"{API_V1}/adjustments", {
        "product_id": 301,
        "location_id": 1,
        "counted_qty": 105,
        "reason": "Monthly physical inventory audit"
    }, expected_status=201)

    print_section("7. STOCK LEDGER AUDIT HISTORY")
    test_endpoint("Stock Ledger History", "GET", f"{API_V1}/ledger/history?product_id=301")

    print_section("8. DASHBOARD OPERATIONAL KPIS")
    test_endpoint("Dashboard KPIs", "GET", f"{API_V1}/dashboard/kpis")

if __name__ == "__main__":
    run_all_tests()
