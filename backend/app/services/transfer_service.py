import uuid
from typing import List, Optional
from app.db.database import dict_cursor
from app.services.product_service import clean_uuid
from app.services.alert_service import AlertService


class TransferService:

    @staticmethod
    def create_transfer(conn, product_id, from_warehouse: Optional[str], to_warehouse: Optional[str], quantity: float) -> dict:
        prod_id = int(product_id) if str(product_id).isdigit() else str(product_id)
        from_loc = int(from_warehouse) if from_warehouse is not None and str(from_warehouse).isdigit() else 1
        to_loc = int(to_warehouse) if to_warehouse is not None and str(to_warehouse).isdigit() else 2
        qty = float(quantity)
        transfer_no = f"TRF-{uuid.uuid4().hex[:8].upper()}"

        with dict_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO transfers
                       (transfer_number, product_id, from_location_id, to_location_id, quantity, status)
                   VALUES (%s, %s, %s, %s, %s, 'Draft')
                   RETURNING id, transfer_number, product_id,
                             from_location_id AS from_warehouse,
                             to_location_id AS to_warehouse,
                             quantity, status, created_at""",
                (transfer_no, prod_id, from_loc, to_loc, qty),
            )
            res = dict(cur.fetchone())
            res["updated_at"] = res.get("created_at")
            return res

    @staticmethod
    def list_transfers(conn, skip: int = 0, limit: int = 100) -> list:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, transfer_number, product_id,
                          from_location_id AS from_warehouse,
                          to_location_id AS to_warehouse,
                          quantity, status, created_at
                   FROM transfers
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (limit, skip),
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                r["updated_at"] = r.get("created_at")
            return rows

    @staticmethod
    def get_transfer(conn, transfer_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, transfer_number, product_id,
                          from_location_id AS from_warehouse,
                          to_location_id AS to_warehouse,
                          quantity, status, created_at
                   FROM transfers WHERE id = %s""",
                (transfer_id,),
            )
            row = cur.fetchone()
            if row:
                res = dict(row)
                res["updated_at"] = res.get("created_at")
                return res
            return None

    @staticmethod
    def validate_transfer(conn, transfer_id: str) -> dict:
        transfer = TransferService.get_transfer(conn, transfer_id)
        if not transfer:
            raise ValueError("Transfer not found")
        if transfer["status"] == "Done":
            raise ValueError("Transfer is already validated")

        prod_id = int(transfer["product_id"]) if str(transfer["product_id"]).isdigit() else str(transfer["product_id"])
        from_loc = int(transfer["from_warehouse"]) if transfer.get("from_warehouse") is not None and str(transfer["from_warehouse"]).isdigit() else 1
        to_loc = int(transfer["to_warehouse"]) if transfer.get("to_warehouse") is not None and str(transfer["to_warehouse"]).isdigit() else 2
        qty = float(transfer["quantity"])

        with dict_cursor(conn) as cur:
            # 1. Check stock availability at source location
            cur.execute(
                """SELECT quantity FROM stock_levels
                   WHERE CAST(product_id AS VARCHAR) = CAST(%s AS VARCHAR)
                     AND CAST(location_id AS VARCHAR) = CAST(%s AS VARCHAR)""",
                (prod_id, from_loc),
            )
            stock_row = cur.fetchone()
            on_hand = float(stock_row["quantity"]) if stock_row else 0.0

            if on_hand == 0.0:
                cur.execute(
                    """SELECT COALESCE(SUM(qty_delta), 0) AS on_hand
                       FROM stock_ledger
                       WHERE CAST(product_id AS VARCHAR) = CAST(%s AS VARCHAR)
                         AND CAST(location_id AS VARCHAR) = CAST(%s AS VARCHAR)""",
                    (prod_id, from_loc),
                )
                stock_row = cur.fetchone()
                on_hand = float(stock_row["on_hand"]) if stock_row else 0.0


            if on_hand < qty:
                cur.execute("SELECT name FROM products WHERE id = %s", (prod_id,))
                p_row = cur.fetchone()
                prod_name = p_row["name"] if p_row else prod_id
                raise ValueError(
                    f"Insufficient stock for Product '{prod_name}' at source location. Available: {on_hand}, Requested: {qty}"
                )

            # 2. Update status to Done
            cur.execute(
                """UPDATE transfers
                   SET status = 'Done'
                   WHERE id = %s
                   RETURNING id, transfer_number, product_id,
                             from_location_id AS from_warehouse,
                             to_location_id AS to_warehouse,
                             quantity, status, created_at""",
                (transfer_id,),
            )
            updated_transfer = dict(cur.fetchone())
            updated_transfer["updated_at"] = updated_transfer.get("created_at")

            # 3. Write Stock Ledger & Stock Level updates
            # OUT from source location (-qty)
            cur.execute(
                """INSERT INTO stock_ledger
                       (product_id, location_id, qty_delta, source_doc_type, source_doc_id)
                   VALUES (%s, %s, %s, 'TRANSFER_OUT', %s)""",
                (prod_id, from_loc, -qty, transfer_id),
            )
            cur.execute(
                """INSERT INTO stock_levels (product_id, location_id, quantity)
                   VALUES (%s, %s, %s)
                   ON CONFLICT(product_id, location_id)
                   DO UPDATE SET quantity = stock_levels.quantity + EXCLUDED.quantity""",
                (prod_id, from_loc, -qty),
            )

            # IN to target location (+qty)
            cur.execute(
                """INSERT INTO stock_ledger
                       (product_id, location_id, qty_delta, source_doc_type, source_doc_id)
                   VALUES (%s, %s, %s, 'TRANSFER_IN', %s)""",
                (prod_id, to_loc, qty, transfer_id),
            )
            cur.execute(
                """INSERT INTO stock_levels (product_id, location_id, quantity)
                   VALUES (%s, %s, %s)
                   ON CONFLICT(product_id, location_id)
                   DO UPDATE SET quantity = stock_levels.quantity + EXCLUDED.quantity""",
                (prod_id, to_loc, qty),
            )

            # Re-evaluate alert thresholds
            AlertService.evaluate_reorder_alert(conn, prod_id, from_loc)
            AlertService.evaluate_reorder_alert(conn, prod_id, to_loc)

            return updated_transfer

