import uuid
from typing import List, Optional
from app.db.database import dict_cursor
from app.services.product_service import clean_uuid


class DeliveryService:

    @staticmethod
    def create_delivery(conn, customer: str, warehouse_id: Optional[str], items: list) -> dict:
        wh_id = clean_uuid(warehouse_id)
        delivery_no = f"DEL-{uuid.uuid4().hex[:8].upper()}"

        with dict_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO deliveries (delivery_number, customer_name, status)
                   VALUES (%s, %s, 'Draft')
                   RETURNING id, delivery_number, customer_name AS customer, status, created_at, updated_at""",
                (delivery_no, customer),
            )
            delivery = dict(cur.fetchone())
            delivery["warehouse_id"] = wh_id

            item_responses = []
            for item in items:
                prod_id = str(item.get("product_id"))
                loc_id = int(item.get("location_id") or item.get("warehouse_id") or 1)
                qty = float(item["quantity"])
                cur.execute(
                    """INSERT INTO delivery_items (delivery_id, product_id, location_id, quantity)
                       VALUES (%s, %s, %s, %s)
                       RETURNING id, delivery_id, product_id, location_id, quantity""",
                    (delivery["id"], prod_id, loc_id, qty),
                )
                item_responses.append(dict(cur.fetchone()))

            delivery["items"] = item_responses
            return delivery

    @staticmethod
    def list_deliveries(conn, skip: int = 0, limit: int = 100) -> list:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, delivery_number, customer_name AS customer, status, created_at, updated_at
                   FROM deliveries
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (limit, skip),
            )
            deliveries = [dict(r) for r in cur.fetchall()]

            for deliv in deliveries:
                cur.execute(
                    """SELECT id, delivery_id, product_id, location_id, quantity
                       FROM delivery_items WHERE delivery_id = %s""",
                    (deliv["id"],),
                )
                deliv["items"] = [dict(i) for i in cur.fetchall()]

            return deliveries

    @staticmethod
    def get_delivery(conn, delivery_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, delivery_number, customer_name AS customer, status, created_at, updated_at
                   FROM deliveries WHERE id = %s""",
                (delivery_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            delivery = dict(row)
            delivery["warehouse_id"] = None
            cur.execute(
                """SELECT id, delivery_id, product_id, location_id, quantity
                   FROM delivery_items WHERE delivery_id = %s""",
                (delivery["id"],),
            )
            delivery["items"] = [dict(i) for i in cur.fetchall()]
            return delivery

    @staticmethod
    def validate_delivery(conn, delivery_id: str) -> dict:
        delivery = DeliveryService.get_delivery(conn, delivery_id)
        if not delivery:
            raise ValueError("Delivery not found")
        if delivery["status"] == "Done":
            raise ValueError("Delivery is already validated")

        with dict_cursor(conn) as cur:
            # Check current stock for items
            for item in delivery["items"]:
                prod_id = item["product_id"]
                loc_id = int(item.get("location_id") or 1)
                requested_qty = float(item["quantity"])

                # Check on-hand stock from stock_ledger sum for this location
                cur.execute(
                    """SELECT COALESCE(SUM(qty_delta), 0) AS on_hand
                       FROM stock_ledger
                       WHERE product_id = %s AND location_id = %s""",
                    (prod_id, loc_id),
                )
                stock_row = cur.fetchone()
                on_hand = float(stock_row["on_hand"]) if stock_row else 0.0

                if on_hand < requested_qty:
                    cur.execute("SELECT name FROM products WHERE id = %s", (prod_id,))
                    p_row = cur.fetchone()
                    prod_name = p_row["name"] if p_row else prod_id
                    raise ValueError(
                        f"Insufficient stock for Product '{prod_name}'. Available: {on_hand}, Requested: {requested_qty}"
                    )

            # Update status to Done
            cur.execute(
                """UPDATE deliveries
                   SET status = 'Done', updated_at = NOW()
                   WHERE id = %s
                   RETURNING id, delivery_number, customer_name AS customer, status, created_at, updated_at""",
                (delivery_id,),
            )
            updated_delivery = dict(cur.fetchone())

            # Write Stock Ledger Entries (-qty) and update Stock Levels
            for item in delivery["items"]:
                prod_id = item["product_id"]
                loc_id = int(item.get("location_id") or 1)
                qty = float(item["quantity"])

                cur.execute(
                    """INSERT INTO stock_ledger
                           (product_id, location_id, qty_delta, source_doc_type, source_doc_id)
                       VALUES (%s, %s, %s, 'DELIVERY', %s)""",
                    (prod_id, loc_id, -qty, delivery_id),
                )

                cur.execute(
                    """INSERT INTO stock_levels (product_id, location_id, quantity)
                       VALUES (%s, %s, %s)
                       ON CONFLICT(product_id, location_id) DO UPDATE SET quantity = quantity - EXCLUDED.quantity""",
                    (prod_id, loc_id, qty),
                )

            updated_delivery["items"] = delivery["items"]
            return updated_delivery
