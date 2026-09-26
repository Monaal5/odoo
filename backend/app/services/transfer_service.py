import uuid
from typing import List, Optional
from app.db.database import dict_cursor
from app.services.product_service import clean_uuid


class TransferService:

    @staticmethod
    def create_transfer(conn, product_id: str, from_warehouse: Optional[str], to_warehouse: Optional[str], quantity: float) -> dict:
        prod_id = clean_uuid(product_id)
        from_wh = clean_uuid(from_warehouse)
        to_wh = clean_uuid(to_warehouse)
        qty = float(quantity)
        transfer_no = f"TRF-{uuid.uuid4().hex[:8].upper()}"

        with dict_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO transfers
                       (transfer_number, product_id, from_warehouse_id, to_warehouse_id, quantity, status)
                   VALUES (%s, %s, %s, %s, %s, 'Draft')
                   RETURNING id, transfer_number, product_id,
                             from_warehouse_id AS from_warehouse,
                             to_warehouse_id AS to_warehouse,
                             quantity, status, created_at, updated_at""",
                (transfer_no, prod_id, from_wh, to_wh, qty),
            )
            return dict(cur.fetchone())

    @staticmethod
    def list_transfers(conn, skip: int = 0, limit: int = 100) -> list:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, transfer_number, product_id,
                          from_warehouse_id AS from_warehouse,
                          to_warehouse_id AS to_warehouse,
                          quantity, status, created_at, updated_at
                   FROM transfers
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (limit, skip),
            )
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_transfer(conn, transfer_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, transfer_number, product_id,
                          from_warehouse_id AS from_warehouse,
                          to_warehouse_id AS to_warehouse,
                          quantity, status, created_at, updated_at
                   FROM transfers WHERE id = %s""",
                (transfer_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def validate_transfer(conn, transfer_id: str) -> dict:
        transfer = TransferService.get_transfer(conn, transfer_id)
        if not transfer:
            raise ValueError("Transfer not found")
        if transfer["status"] == "Done":
            raise ValueError("Transfer is already validated")

        prod_id = transfer["product_id"]
        from_wh = transfer["from_warehouse"]
        to_wh = transfer["to_warehouse"]
        qty = float(transfer["quantity"])

        with dict_cursor(conn) as cur:
            # 1. Check stock availability at source location
            cur.execute(
                """SELECT COALESCE(SUM(qty_delta), 0) AS on_hand
                   FROM stock_ledger_entries
                   WHERE product_id = %s AND (warehouse_id = %s OR (%s IS NULL AND warehouse_id IS NULL))""",
                (prod_id, from_wh, from_wh),
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
                   SET status = 'Done', updated_at = NOW()
                   WHERE id = %s
                   RETURNING id, transfer_number, product_id,
                             from_warehouse_id AS from_warehouse,
                             to_warehouse_id AS to_warehouse,
                             quantity, status, created_at, updated_at""",
                (transfer_id,),
            )
            updated_transfer = dict(cur.fetchone())

            # 3. Create 2 immutable stock ledger entries (Out & In)
            # OUT from source location (-qty)
            cur.execute(
                """INSERT INTO stock_ledger_entries
                       (product_id, warehouse_id, qty_delta, source_document_type, source_document_id)
                   VALUES (%s, %s, %s, 'TRANSFER_OUT', %s)""",
                (prod_id, from_wh, -qty, transfer_id),
            )

            # IN to destination location (+qty)
            cur.execute(
                """INSERT INTO stock_ledger_entries
                       (product_id, warehouse_id, qty_delta, source_document_type, source_document_id)
                   VALUES (%s, %s, %s, 'TRANSFER_IN', %s)""",
                (prod_id, to_wh, qty, transfer_id),
            )

            # 4. Update cached Stock Levels
            # Decrement at source
            cur.execute(
                """UPDATE stock_levels
                   SET quantity = quantity - %s
                   WHERE product_id = %s AND (warehouse_id = %s OR (%s IS NULL AND warehouse_id IS NULL))""",
                (qty, prod_id, from_wh, from_wh),
            )

            # Increment at destination (upsert)
            cur.execute(
                """INSERT INTO stock_levels (product_id, warehouse_id, quantity)
                   VALUES (%s, %s, %s)
                   ON CONFLICT DO NOTHING""",
                (prod_id, to_wh, qty),
            )
            cur.execute(
                """UPDATE stock_levels
                   SET quantity = quantity + %s
                   WHERE product_id = %s AND (warehouse_id = %s OR (%s IS NULL AND warehouse_id IS NULL))""",
                (qty, prod_id, to_wh, to_wh),
            )

            return updated_transfer
