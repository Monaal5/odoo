import uuid
from typing import List, Optional
from app.db.database import dict_cursor
from app.services.product_service import clean_uuid


class ReceiptService:

    @staticmethod
    def create_receipt(conn, supplier: str, warehouse_id: Optional[str], items: list) -> dict:
        wh_id = clean_uuid(warehouse_id)
        receipt_no = f"REC-{uuid.uuid4().hex[:8].upper()}"

        with dict_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO receipts (receipt_number, supplier, warehouse_id, status)
                   VALUES (%s, %s, %s, 'Draft')
                   RETURNING id, receipt_number, supplier, warehouse_id, status, created_at, updated_at""",
                (receipt_no, supplier, wh_id),
            )
            receipt = dict(cur.fetchone())

            item_responses = []
            for item in items:
                prod_id = clean_uuid(item.get("product_id"))
                qty = float(item["quantity"])
                cur.execute(
                    """INSERT INTO receipt_items (receipt_id, product_id, quantity)
                       VALUES (%s, %s, %s)
                       RETURNING id, receipt_id, product_id, quantity""",
                    (receipt["id"], prod_id, qty),
                )
                item_responses.append(dict(cur.fetchone()))

            receipt["items"] = item_responses
            return receipt

    @staticmethod
    def list_receipts(conn, skip: int = 0, limit: int = 100) -> list:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, receipt_number, supplier, warehouse_id, status, created_at, updated_at
                   FROM receipts
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (limit, skip),
            )
            receipts = [dict(r) for r in cur.fetchall()]

            for rec in receipts:
                cur.execute(
                    """SELECT id, receipt_id, product_id, quantity
                       FROM receipt_items WHERE receipt_id = %s""",
                    (rec["id"],),
                )
                rec["items"] = [dict(i) for i in cur.fetchall()]

            return receipts

    @staticmethod
    def get_receipt(conn, receipt_id: str) -> Optional[dict]:
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, receipt_number, supplier, warehouse_id, status, created_at, updated_at
                   FROM receipts WHERE id = %s""",
                (receipt_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            receipt = dict(row)
            cur.execute(
                """SELECT id, receipt_id, product_id, quantity
                   FROM receipt_items WHERE receipt_id = %s""",
                (receipt["id"],),
            )
            receipt["items"] = [dict(i) for i in cur.fetchall()]
            return receipt

    @staticmethod
    def validate_receipt(conn, receipt_id: str) -> dict:
        receipt = ReceiptService.get_receipt(conn, receipt_id)
        if not receipt:
            raise ValueError("Receipt not found")
        if receipt["status"] == "Done":
            raise ValueError("Receipt is already validated")

        with dict_cursor(conn) as cur:
            # 1. Update status to Done
            cur.execute(
                """UPDATE receipts
                   SET status = 'Done', updated_at = NOW()
                   WHERE id = %s
                   RETURNING id, receipt_number, supplier, warehouse_id, status, created_at, updated_at""",
                (receipt_id,),
            )
            updated_receipt = dict(cur.fetchone())

            # 2. Write Stock Ledger Entries (+qty) and update Stock Levels
            for item in receipt["items"]:
                prod_id = item["product_id"]
                wh_id = receipt["warehouse_id"]
                qty = float(item["quantity"])

                # Insert immutable ledger entry
                cur.execute(
                    """INSERT INTO stock_ledger_entries
                           (product_id, warehouse_id, qty_delta, source_document_type, source_document_id)
                       VALUES (%s, %s, %s, 'RECEIPT', %s)""",
                    (prod_id, wh_id, qty, receipt_id),
                )

                # Upsert stock level
                cur.execute(
                    """INSERT INTO stock_levels (product_id, warehouse_id, quantity)
                       VALUES (%s, %s, %s)
                       ON CONFLICT DO NOTHING""",
                    (prod_id, wh_id, qty),
                )
                cur.execute(
                    """UPDATE stock_levels
                       SET quantity = quantity + %s
                       WHERE product_id = %s AND (warehouse_id = %s OR (%s IS NULL AND warehouse_id IS NULL))""",
                    (qty, prod_id, wh_id, wh_id),
                )

            updated_receipt["items"] = receipt["items"]
            return updated_receipt
