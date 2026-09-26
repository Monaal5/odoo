from typing import Optional, List
from app.db.database import dict_cursor


class DashboardService:
    """
    Aggregate queries powering all dashboard endpoints.
    Uses raw psycopg2/sqlite connections (Dev 1 pattern) with dict_cursor.
    """

    # ── KPIs ─────────────────────────────────────────────────

    @staticmethod
    def get_kpis(conn) -> dict:
        """
        Return all KPI card values:
          - total_products: distinct active products with any stock entry
          - low_stock: products whose total on-hand is <= reorder_min (and > 0)
          - out_of_stock: products with zero or negative total on-hand
          - pending_receipts / pending_deliveries / pending_transfers
        """
        with dict_cursor(conn) as cur:

            # Total distinct active products that have ever had stock
            cur.execute(
                """
                SELECT COUNT(DISTINCT p.id) AS cnt
                FROM products p
                WHERE p.is_active = TRUE
                """
            )
            total_products = (cur.fetchone() or {}).get("cnt", 0) or 0

            # Aggregate on-hand per product from ledger
            # low stock = on_hand > 0 AND on_hand <= reorder_min (where reorder_min > 0)
            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE on_hand > 0
                          AND p.reorder_min > 0
                          AND on_hand <= p.reorder_min
                    ) AS low_stock,
                    COUNT(*) FILTER (WHERE on_hand <= 0) AS out_of_stock
                FROM (
                    SELECT
                        sle.product_id,
                        COALESCE(SUM(sle.qty_delta), 0) AS on_hand
                    FROM stock_ledger_entries sle
                    GROUP BY sle.product_id
                ) agg
                JOIN products p ON p.id = agg.product_id
                WHERE p.is_active = TRUE
                """
            )
            stock_row = cur.fetchone() or {}
            low_stock = stock_row.get("low_stock", 0) or 0
            out_of_stock = stock_row.get("out_of_stock", 0) or 0

            # Pending receipts (not Done, not Cancelled)
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM receipts WHERE status NOT IN ('Done', 'Cancelled')"
            )
            pending_receipts = (cur.fetchone() or {}).get("cnt", 0) or 0

            # Pending deliveries
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM deliveries WHERE status NOT IN ('Done', 'Cancelled')"
            )
            pending_deliveries = (cur.fetchone() or {}).get("cnt", 0) or 0

            # Pending transfers
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM transfers WHERE status NOT IN ('Done', 'Cancelled')"
            )
            pending_transfers = (cur.fetchone() or {}).get("cnt", 0) or 0

        return {
            "total_products": int(total_products),
            "low_stock": int(low_stock),
            "out_of_stock": int(out_of_stock),
            "pending_receipts": int(pending_receipts),
            "pending_deliveries": int(pending_deliveries),
            "pending_transfers": int(pending_transfers),
        }

    # ── Recent Activity ───────────────────────────────────────

    @staticmethod
    def get_activity(conn, limit: int = 20, skip: int = 0) -> dict:
                        SELECT
                    sle.id,
                    sle.product_id,
                    p.name  AS product_name,
                    sle.warehouse_id,
                    w.name  AS warehouse_name,
                    sle.qty_delta,
                    sle.source_document_type,
                    sle.source_document_id,
                    sle.timestamp AS created_at
                FROM stock_ledger_entries sle
                LEFT JOIN products   p ON p.id = sle.product_id
                LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                ORDER BY sle.timestamp DESC
                LIMIT %s OFFSET %s
                """,
                (limit, skip),
            )
            rows = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT COUNT(*) AS cnt FROM stock_ledger_entries")
            total = (cur.fetchone() or {}).get("cnt", 0) or 0

        return {"items": rows, "total": int(total)}

    # ── Filtered Movements ────────────────────────────────────

    @staticmethod
    def get_filtered(
        conn,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        warehouse_id: Optional[str] = None,
        category_id: Optional[str] = None,
        product_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        """
        Filter stock ledger entries by document type, status, warehouse,
        product category, or specific product. Joins to resolve human-readable names.
        """
        conditions = ["1=1"]
        params: list = []

        if doc_type:
            conditions.append("sle.source_document_type = %s")
            params.append(doc_type.upper())

        if warehouse_id:
            conditions.append("sle.warehouse_id = %s")
            params.append(warehouse_id)

        if product_id:
            conditions.append("sle.product_id = %s")
            params.append(product_id)

        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)

        where_clause = " AND ".join(conditions)

        # Status filtering: receipts/deliveries/transfers have a status column;
        # we resolve the status from the source document table.
        # We union across tables rather than a complex join for simplicity.
        status_filter = ""
        if status:
            status_filter = f"AND doc_status = %s"
            params_with_status = params + [status.capitalize()]
        else:
            params_with_status = params

        with dict_cursor(conn) as cur:
            if status:
                # Subquery that resolves status from source documents
                sql = f"""
                    SELECT
                        sle.id,
                        sle.source_document_type  AS document_type,
                        COALESCE(r.receipt_number, d.delivery_number, t.transfer_number) AS document_number,
                        sle.product_id,
                        p.name                    AS product_name,
                        sle.warehouse_id,
                        w.name                    AS warehouse_name,
                        sle.qty_delta,
                        COALESCE(r.status, d.status, t.status) AS status,
                        sle.timestamp AS created_at
                    FROM stock_ledger_entries sle
                    LEFT JOIN products   p ON p.id = sle.product_id
                    LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                    LEFT JOIN receipts   r ON r.id = sle.source_document_id AND sle.source_document_type = 'RECEIPT'
                    LEFT JOIN deliveries d ON d.id = sle.source_document_id AND sle.source_document_type = 'DELIVERY'
                    LEFT JOIN transfers  t ON t.id = sle.source_document_id AND sle.source_document_type IN ('TRANSFER_IN','TRANSFER_OUT')
                    WHERE {where_clause}
                      AND COALESCE(r.status, d.status, t.status) = %s
                    ORDER BY sle.timestamp DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(sql, params_with_status + [limit, skip])
                rows = [dict(r) for r in cur.fetchall()]

                count_sql = f"""
                    SELECT COUNT(*) AS cnt
                    FROM stock_ledger_entries sle
                    LEFT JOIN products   p ON p.id = sle.product_id
                    LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                    LEFT JOIN receipts   r ON r.id = sle.source_document_id AND sle.source_document_type = 'RECEIPT'
                    LEFT JOIN deliveries d ON d.id = sle.source_document_id AND sle.source_document_type = 'DELIVERY'
                    LEFT JOIN transfers  t ON t.id = sle.source_document_id AND sle.source_document_type IN ('TRANSFER_IN','TRANSFER_OUT')
                    WHERE {where_clause}
                      AND COALESCE(r.status, d.status, t.status) = %s
                """
                cur.execute(count_sql, params_with_status)
            else:
                sql = f"""
                    SELECT
                        sle.id,
                        sle.source_document_type  AS document_type,
                        COALESCE(r.receipt_number, d.delivery_number, t.transfer_number) AS document_number,
                        sle.product_id,
                        p.name                    AS product_name,
                        sle.warehouse_id,
                        w.name                    AS warehouse_name,
                        sle.qty_delta,
                        COALESCE(r.status, d.status, t.status) AS status,
                        sle.timestamp AS created_at
                    FROM stock_ledger_entries sle
                    LEFT JOIN products   p ON p.id = sle.product_id
                    LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                    LEFT JOIN receipts   r ON r.id = sle.source_document_id AND sle.source_document_type = 'RECEIPT'
                    LEFT JOIN deliveries d ON d.id = sle.source_document_id AND sle.source_document_type = 'DELIVERY'
                    LEFT JOIN transfers  t ON t.id = sle.source_document_id AND sle.source_document_type IN ('TRANSFER_IN','TRANSFER_OUT')
                    WHERE {where_clause}
                    ORDER BY sle.timestamp DESC
                    LIMIT %s OFFSET %s
                """IN transfers  t ON t.id = sle.source_document_id AND sle.source_document_type IN ('TRANSFER_IN','TRANSFER_OUT')
                    WHERE {where_clause}
                    ORDER BY sle.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(sql, params + [limit, skip])
                rows = [dict(r) for r in cur.fetchall()]

                count_sql = f"""
                    SELECT COUNT(*) AS cnt
                    FROM stock_ledger_entries sle
                    LEFT JOIN products   p ON p.id = sle.product_id
                    LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                    WHERE {where_clause}
                """
                cur.execute(count_sql, params)

            total = (cur.fetchone() or {}).get("cnt", 0) or 0

        return {"items": rows, "total": int(total)}

    # ── Legacy: full KPI with stock levels (backward compat) ──

    @staticmethod
    def get_kpis_legacy(conn) -> dict:
        """
        Original full KPI payload including per-location stock level list.
        Kept for any existing frontend consumers of the old /kpis shape.
        """
        kpis = DashboardService.get_kpis(conn)
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM stock_ledger_entries"
            )
            total_ledger = (cur.fetchone() or {}).get("cnt", 0) or 0

            cur.execute(
                "SELECT COALESCE(SUM(qty_delta), 0) AS total FROM stock_ledger_entries"
            )
            total_units = (cur.fetchone() or {}).get("total", 0) or 0

            cur.execute(
                """
                SELECT product_id, warehouse_id AS location_id,
                       COALESCE(SUM(qty_delta), 0) AS quantity
                FROM stock_ledger_entries
                GROUP BY product_id, warehouse_id
                ORDER BY product_id
                LIMIT 200
                """
            )
            stock_levels = [dict(r) for r in cur.fetchall()]

        return {
            "total_products_in_stock": kpis["total_products"],
            "total_units_in_stock": float(total_units),
            "low_stock_count": kpis["low_stock"],
            "pending_receipts": kpis["pending_receipts"],
            "pending_deliveries": kpis["pending_deliveries"],
            "pending_transfers": kpis["pending_transfers"],
            "total_ledger_transactions": int(total_ledger),
            "stock_levels": stock_levels,
        }
