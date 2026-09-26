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
                """INSERT INTO deliveries (delivery_number, customer, warehouse_id, status)
                   VALUES (%s, %s, %s, 'Draft')
                   RETURNING id, delivery_number, customer, warehouse_id, status, created_at, updated_at""",
                (delivery_no, customer, wh_id),
            )
            delivery = dict(cur.fetchone())

            item_responses = []
            for item in items:
                prod_id = clean_uuid(item.get("product_id"))
                qty = float(item["quantity"])
                cur.execute(
                    """INSERT INTO delivery_items (delivery_id, product_id, quantity)
                       VALUES (%s, %s, %s)
                       RETURNING id, delivery_id, product_id, quantity""",
                    (delivery["id"], prod_id, qty),
                )
                item_responses.append(dict(cur.fetchone()))

            delivery["items"] = item_responses
            return delivery

    @staticmethod
    def list_deliveries(conn, skip: int = 0, limit: int = 100) -> list:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, delivery_number, customer, warehouse_id, status, created_at, updated_at
                   FROM deliveries
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (limit, skip),
            )
            deliveries = [dict(r) for r in cur.fetchall()]

            for deliv in deliveries:
                cur.execute(
                    """SELECT id, delivery_id, product_id, quantity
                       FROM delivery_items WHERE delivery_id = %s""",
                    (deliv["id"],),
                )
                deliv["items"] = [dict(i) for i in cur.fetchall()]

            return deliveries

    @staticmethod
    def get_delivery(conn, delivery_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, delivery_number, customer, warehouse_id, status, created_at, updated_at
                   FROM deliveries WHERE id = %s""",
                (delivery_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            delivery = dict(row)
            cur.execute(
                """SELECT id, delivery_id, product_id, quantity
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
            # Check current stock for items if needed
            for item in delivery["items"]:
                prod_id = item["product_id"]
                wh_id = delivery["warehouse_id"]
                requested_qty = float(item["quantity"])

                # Check on-hand stock from ledger sum
                cur.execute(
                    """SELECT COALESCE(SUM(qty_delta), 0) AS on_hand
                       FROM stock_ledger_entries
                       WHERE product_id = %s AND (warehouse_id = %s OR (%s IS NULL AND warehouse_id IS NULL))""",
                    (prod_id, wh_id, wh_id),
                )
                stock_row = cur.fetchone()
                on_hand = float(stock_row["on_hand"]) if stock_row else 0.0

                if on_hand < requested_qty:
                    raise ValueError(
                        f"Insufficient stock for Product '{prod_id}'. Available: {on_hand}, Requested: {requested_qty}"
                    )

            # Update status to Done
            cur.execute(
                """UPDATE deliveries
                   SET status = 'Done', updated_at = NOW()
                   WHERE id = %s
                   RETURNING id, delivery_number, customer, warehouse_id, status, created_at, updated_at""",
                (delivery_id,),
            )
            updated_delivery = dict(cur.fetchone())

            # Write Stock Ledger Entries (-qty) and update Stock Levels
            for item in delivery["items"]:
                prod_id = item["product_id"]
                wh_id = delivery["warehouse_id"]
                qty = float(item["quantity"])

                # Insert immutable ledger entry (-qty_delta)
                cur.execute(
                    """INSERT INTO stock_ledger_entries
                           (product_id, warehouse_id, qty_delta, source_document_type, source_document_id)
                       VALUES (%s, %s, %s, 'DELIVERY', %s)""",
                    (prod_id, wh_id, -qty, delivery_id),
                )

                # Update cached stock level
                cur.execute(
                    """UPDATE stock_levels
                       SET quantity = quantity - %s
                       WHERE product_id = %s AND (warehouse_id = %s OR (%s IS NULL AND warehouse_id IS NULL))""",
                    (qty, prod_id, wh_id, wh_id),
                )

            updated_delivery["items"] = delivery["items"]
            return updated_delivery
