import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def print_banner(step_num, title):
    print(f"\n{'='*70}")
    print(f" [APPLE WORKFLOW] STEP {step_num}: {title}")
    print(f"{'='*70}")

def run_apple_workflow():
    print_banner(1, "CREATE ITEM - Fresh Fuji Apples")
    item_res = requests.post(f"{API_V1}/items", json={
        "title": "Fresh Fuji Apples",
        "description": "Crisp Grade A Fuji Apples (1kg bags)",
        "category": "Produce",
        "is_active": True
    })
    item = item_res.json()
    product_id = item["id"]
    print(f"[OK] Created Item #{product_id}: {item['title']} (Category: {item['category']})")

    print_banner(2, "RECEIPT - Receive 500 kg Apples from Orchard Farms")
    rec_res = requests.post(f"{API_V1}/receipts", json={
        "supplier_name": "Orchard Farms Supplier",
        "items": [
            {"product_id": product_id, "location_id": 1, "quantity": 500}
        ]
    })
    rec = rec_res.json()
    receipt_id = rec["id"]
    print(f"[OK] Draft Receipt Created: #{receipt_id} ({rec['receipt_number']}) - Status: {rec['status']}")

    # Validate Receipt
    val_rec = requests.post(f"{API_V1}/receipts/{receipt_id}/validate").json()
    print(f"[OK] Validated Receipt #{receipt_id} - Status: {val_rec['status']}")
    print(f"     Stock at Location 1 (Main Cold Storage) = +500 kg")

    print_banner(3, "DELIVERY - Ship 120 kg Apples to SuperMart Supermarket")
    del_res = requests.post(f"{API_V1}/deliveries", json={
        "customer_name": "SuperMart Supermarket",
        "items": [
            {"product_id": product_id, "location_id": 1, "quantity": 120}
        ]
    })
    delivery = del_res.json()
    delivery_id = delivery["id"]
    print(f"[OK] Draft Delivery Created: #{delivery_id} ({delivery['delivery_number']}) - Status: {delivery['status']}")

    # Validate Delivery
    val_del = requests.post(f"{API_V1}/deliveries/{delivery_id}/validate").json()
    print(f"[OK] Validated Delivery #{delivery_id} - Status: {val_del['status']}")
    print(f"     Stock at Location 1 reduced by 120 kg (Current: 380 kg)")

    print_banner(4, "INTERNAL TRANSFER - Move 100 kg Apples from Cold Storage (Loc 1) to Display Rack (Loc 2)")
    trf_res = requests.post(f"{API_V1}/transfers", json={
        "product_id": product_id,
        "from_location_id": 1,
        "to_location_id": 2,
        "quantity": 100
    })
    transfer = trf_res.json()
    transfer_id = transfer["id"]

    # Validate Transfer
    val_trf = requests.post(f"{API_V1}/transfers/{transfer_id}/validate").json()
    print(f"[OK] Validated Transfer #{transfer_id} ({transfer['transfer_number']}) - Status: {val_trf['status']}")
    print(f"     Location 1 (Cold Storage) = 280 kg")
    print(f"     Location 2 (Display Rack)  = 100 kg")

    print_banner(5, "STOCK ADJUSTMENT - Physical Count at Cold Storage finds 275 kg (5 kg spoiled)")
    adj_res = requests.post(f"{API_V1}/adjustments", json={
        "product_id": product_id,
        "location_id": 1,
        "counted_qty": 275,
        "reason": "5 kg spoiled apples discarded during cycle count audit"
    })
    adj = adj_res.json()
    print(f"[OK] Adjustment Saved: #{adj['id']} ({adj['adjustment_number']})")
    print(f"     System Qty: {adj['system_qty']} kg | Counted Qty: {adj['counted_qty']} kg | Delta: {adj['delta_qty']} kg")
    print(f"     Reason: {adj['reason']}")

    print_banner(6, "STOCK LEDGER AUDIT TRAIL for Fresh Fuji Apples")
    history = requests.get(f"{API_V1}/ledger/history?product_id={product_id}").json()
    print(f"[OK] Audit Log ({len(history)} Events Recorded):")
    for h in history:
        print(f"     * [{h['timestamp']}] Document: {h['source_doc_type']} #{h['source_doc_id']} | Loc: {h['location_id']} | Qty Delta: {h['qty_delta']:+d} kg")

    print_banner(7, "LIVE DASHBOARD KPIS")
    kpis = requests.get(f"{API_V1}/dashboard/kpis").json()
    print(f"[OK] Dashboard Metrics:")
    print(f"     * Total Units in Stock: {kpis['total_units_in_stock']} kg")
    print(f"     * Total Ledger Transactions: {kpis['total_ledger_transactions']}")
    print(f"     * Current Stock Breakdown:")
    for s in kpis['stock_levels']:
        if s['product_id'] == product_id:
            loc_name = "Cold Storage (Loc 1)" if s['location_id'] == 1 else "Display Rack (Loc 2)"
            print(f"       - Product #{s['product_id']} at {loc_name}: {s['quantity']} kg")

if __name__ == "__main__":
    run_apple_workflow()
