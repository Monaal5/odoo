import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import get_db, dict_cursor
from app.schemas.mobile import MobileStockResponse, MobileCountRequest, MobileCountResponse, MobileTask
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile", tags=["Mobile APIs for Warehouse Staff"])


@router.get("/tasks", response_model=List[MobileTask])
def get_mobile_tasks(conn=Depends(get_db)):
    """
    GET /mobile/tasks
    Returns lightweight pending picks / tasks for warehouse staff.
    """
    tasks = []
    with dict_cursor(conn) as cur:
        # Fetch pending deliveries (Picks)
        cur.execute(
            """
            SELECT d.id, d.delivery_number, di.product_id, di.quantity,
                   COALESCE(i.title, 'Product') AS product_name,
                   'Rack-A1' AS location
            FROM deliveries d
            JOIN delivery_items di ON di.delivery_id = d.id
            LEFT JOIN items i ON i.id = di.product_id
            WHERE d.status = 'Draft'
            LIMIT 50
            """
        )
        deliveries = cur.fetchall()
        for row in deliveries:
            tasks.append(
                MobileTask(
                    id=f"PICK-{row['id']}",
                    task_type="Pick",
                    doc_number=row["delivery_number"],
                    location=row.get("location") or "Rack-A1",
                    sku=f"PRD-{row['product_id']}",
                    qty=float(row["quantity"]),
                    status="Pending",
                )
            )

        # Fetch pending transfers if any
        cur.execute(
            """
            SELECT t.id, t.transfer_number, t.product_id, t.quantity,
                   'Rack-B1' AS location
            FROM transfers t
            WHERE t.status = 'Draft'
            LIMIT 50
            """
        )
        transfers = cur.fetchall()
        for row in transfers:
            tasks.append(
                MobileTask(
                    id=f"TRF-{row['id']}",
                    task_type="Transfer",
                    doc_number=row["transfer_number"],
                    location=row.get("location") or "Rack-B1",
                    sku=f"PRD-{row['product_id']}",
                    qty=float(row["quantity"]),
                    status="Pending",
                )
            )

    return tasks


def _resolve_product(cur, sku_or_id: str):
    """Resolve a product SKU or ID to (product_id: int, sku: str). Creates item if needed."""
    # 1. Try products table by SKU
    cur.execute("SELECT id, sku FROM products WHERE LOWER(sku) = LOWER(%s)", (sku_or_id,))
    prod = cur.fetchone()
    if prod:
        # products.id is VARCHAR, but we need integer for stock_ledger
        # Check if there's a matching item
        cur.execute("SELECT id FROM items WHERE LOWER(title) = LOWER(%s)", (prod["sku"],))
        item = cur.fetchone()
        if item:
            return int(item["id"]), prod["sku"]
        # Create item for this product
        cur.execute("INSERT INTO items (title, category) VALUES (%s, 'General')", (prod["sku"],))
        cur.execute("SELECT last_insert_rowid() AS id")
        row = cur.fetchone()
        return int(row["id"]), prod["sku"]

    # 2. Try items table by id or title
    if sku_or_id.isdigit():
        cur.execute("SELECT id, title FROM items WHERE id = %s", (int(sku_or_id),))
    else:
        cur.execute("SELECT id, title FROM items WHERE LOWER(title) = LOWER(%s)", (sku_or_id,))
    item = cur.fetchone()
    if item:
        return int(item["id"]), item.get("title") or sku_or_id

    # 3. Create new item
    cur.execute("INSERT INTO items (title, category) VALUES (%s, 'General')", (sku_or_id,))
    cur.execute("SELECT last_insert_rowid() AS id")
    new_item = cur.fetchone()
    return int(new_item["id"]), sku_or_id


@router.get("/stock/{sku}", response_model=MobileStockResponse)
def get_mobile_stock(sku: str, conn=Depends(get_db)):
    """
    GET /mobile/stock/{sku}
    Returns lightweight current stock JSON for warehouse staff:
    {"sku":"STL001","qty":42,"location":"Rack-B2"}
    """
    with dict_cursor(conn) as cur:
        product_id, prod_sku = _resolve_product(cur, sku)

        # Calculate current on-hand stock from ledger
        cur.execute(
            "SELECT COALESCE(SUM(qty_delta), 0) AS current_stock FROM stock_ledger WHERE product_id = %s",
            (product_id,),
        )
        stock_row = cur.fetchone()
        current_qty = float(stock_row["current_stock"]) if stock_row else 0.0

        # Fallback: check stock_levels table
        if current_qty == 0.0:
            cur.execute(
                "SELECT COALESCE(SUM(quantity), 0) AS qty FROM stock_levels WHERE product_id = %s",
                (product_id,),
            )
            sl_row = cur.fetchone()
            if sl_row and float(sl_row["qty"]) > 0:
                current_qty = float(sl_row["qty"])

        # Location: use first warehouse or default
        cur.execute("SELECT name FROM warehouses LIMIT 1")
        wh_row = cur.fetchone()
        location_name = wh_row["name"] if wh_row else "Rack-B2"

        return MobileStockResponse(sku=prod_sku, qty=current_qty, location=location_name)


@router.post("/count", response_model=MobileCountResponse, status_code=status.HTTP_200_OK)
def post_mobile_count(data: MobileCountRequest, conn=Depends(get_db)):
    """
    POST /mobile/count
    Submit stock count for warehouse staff.
    Input: {"sku":"STL001","qty":42,"location":"Rack-B2"}
    """
    with dict_cursor(conn) as cur:
        product_id, prod_sku = _resolve_product(cur, data.sku)

        # Calculate current system stock
        cur.execute(
            "SELECT COALESCE(SUM(qty_delta), 0) AS total FROM stock_ledger WHERE product_id = %s",
            (product_id,),
        )
        system_qty = float(cur.fetchone()["total"])
        delta_qty = data.qty - system_qty

        # Record delta in stock_ledger
        if delta_qty != 0:
            cur.execute(
                "INSERT INTO stock_ledger (product_id, location_id, qty_delta, source_doc_type, source_doc_id) VALUES (%s, 1, %s, 'MOBILE_COUNT', 0)",
                (product_id, int(delta_qty)),
            )

        # Log audit entry
        AuditService.log_action(
            conn, action="ADJUST", entity="Stock", entity_id=prod_sku, user_id="WarehouseStaff",
        )

        return MobileCountResponse(
            sku=prod_sku,
            qty=data.qty,
            location=data.location or "Rack-B2",
            status="success",
            message="Stock count updated successfully",
        )
