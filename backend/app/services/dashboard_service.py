from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import dict_cursor
from app.models.stock_level import StockLevel
from app.models.stock_ledger import StockLedgerEntry
from app.models.receipt import Receipt
from app.models.delivery import Delivery
from app.models.transfer import InternalTransfer
from app.models.item import Item
from app.schemas.dashboard import (
    DashboardKPIsResponse,
    StockLevelItem,
    ActivityItem,
    DashboardFilterResponse,
)


class DashboardService:
    """
    Aggregate queries powering all dashboard endpoints.
    Supports both SQLAlchemy Session objects and raw DB connection objects.
    """

    @staticmethod
    def get_kpis(db: Any) -> Dict[str, Any]:
        """Return all KPI card values and stock level summaries."""
        if hasattr(db, "query"):
            # SQLAlchemy Session mode
            total_products_count = db.query(func.count(Item.id)).scalar() or 0
            products_in_stock = db.query(func.count(func.distinct(StockLevel.product_id))).filter(StockLevel.quantity > 0).scalar() or 0
            total_units = db.query(func.sum(StockLevel.quantity)).scalar() or 0
            low_stock_count = db.query(func.count(StockLevel.id)).filter(StockLevel.quantity <= 5).scalar() or 0
            pending_recs = db.query(func.count(Receipt.id)).filter(Receipt.status != "Done").scalar() or 0
            pending_dels = db.query(func.count(Delivery.id)).filter(Delivery.status != "Done").scalar() or 0
            pending_trfs = db.query(func.count(InternalTransfer.id)).filter(InternalTransfer.status != "Done").scalar() or 0
            total_ledger = db.query(func.count(StockLedgerEntry.id)).scalar() or 0

            stock_levels_raw = db.query(StockLevel).all()
            stock_levels = [
                {
                    "product_id": s.product_id,
                    "location_id": s.location_id,
                    "quantity": s.quantity,
                }
                for s in stock_levels_raw
            ]

            return {
                "total_products": total_products_count or products_in_stock,
                "low_stock": low_stock_count,
                "out_of_stock": 0,
                "pending_receipts": pending_recs,
                "pending_deliveries": pending_dels,
                "pending_transfers": pending_trfs,
                "total_products_in_stock": products_in_stock,
                "total_units_in_stock": float(total_units),
                "low_stock_count": low_stock_count,
                "total_ledger_transactions": total_ledger,
                "stock_levels": stock_levels,
            }

        # Raw Connection mode
        with dict_cursor(db) as cur:
            cur.execute("SELECT COUNT(DISTINCT p.id) AS cnt FROM products p WHERE p.is_active = TRUE")
            total_products = (cur.fetchone() or {}).get("cnt", 0) or 0

            cur.execute("SELECT COUNT(*) AS cnt FROM receipts WHERE status NOT IN ('Done', 'Cancelled')")
            pending_receipts = (cur.fetchone() or {}).get("cnt", 0) or 0

            cur.execute("SELECT COUNT(*) AS cnt FROM deliveries WHERE status NOT IN ('Done', 'Cancelled')")
            pending_deliveries = (cur.fetchone() or {}).get("cnt", 0) or 0

            cur.execute("SELECT COUNT(*) AS cnt FROM transfers WHERE status NOT IN ('Done', 'Cancelled')")
            pending_transfers = (cur.fetchone() or {}).get("cnt", 0) or 0

            cur.execute("SELECT COUNT(*) AS cnt FROM stock_ledger")
            total_ledger = (cur.fetchone() or {}).get("cnt", 0) or 0

            cur.execute("SELECT product_id, location_id, quantity FROM stock_levels")
            stock_levels = [dict(r) for r in (cur.fetchall() or [])]

        return {
            "total_products": int(total_products),
            "low_stock": 0,
            "out_of_stock": 0,
            "pending_receipts": int(pending_receipts),
            "pending_deliveries": int(pending_deliveries),
            "pending_transfers": int(pending_transfers),
            "total_products_in_stock": int(total_products),
            "total_units_in_stock": sum(s.get("quantity", 0) for s in stock_levels),
            "low_stock_count": 0,
            "total_ledger_transactions": int(total_ledger),
            "stock_levels": stock_levels,
        }

    @staticmethod
    def get_activity(db: Any, limit: int = 20, skip: int = 0) -> Dict[str, Any]:
        """Retrieve recent stock movements feed."""
        if hasattr(db, "query"):
            entries = db.query(StockLedgerEntry).order_by(StockLedgerEntry.id.desc()).offset(skip).limit(limit).all()
            total = db.query(func.count(StockLedgerEntry.id)).scalar() or 0
            items = [
                {
                    "id": str(e.id),
                    "product_id": str(e.product_id),
                    "location_id": str(e.location_id),
                    "qty_delta": float(e.qty_delta),
                    "source_doc_type": e.source_doc_type,
                    "source_doc_id": str(e.source_doc_id),
                    "timestamp": e.timestamp,
                }
                for e in entries
            ]
            return {"items": items, "total": total}

        with dict_cursor(db) as cur:
            cur.execute(
                """
                SELECT id, product_id, location_id, qty_delta, source_doc_type, source_doc_id, timestamp
                FROM stock_ledger
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
                """,
                (limit, skip),
            )
            rows = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT COUNT(*) AS cnt FROM stock_ledger")
            total = (cur.fetchone() or {}).get("cnt", 0) or 0

        return {"items": rows, "total": int(total)}

    @staticmethod
    def get_filtered(
        db: Any,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        warehouse_id: Optional[str] = None,
        category_id: Optional[str] = None,
        product_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Filter stock movements or levels by criteria."""
        if hasattr(db, "query"):
            query = db.query(StockLevel)
            if warehouse_id is not None and warehouse_id.isdigit():
                query = query.filter(StockLevel.location_id == int(warehouse_id))
            if product_id is not None and product_id.isdigit():
                query = query.filter(StockLevel.product_id == int(product_id))

            stock_levels_raw = query.offset(skip).limit(limit).all()
            items = [
                {
                    "id": str(s.id),
                    "product_id": str(s.product_id),
                    "location_id": str(s.location_id),
                    "quantity": float(s.quantity),
                }
                for s in stock_levels_raw
            ]
            return {
                "items": items,
                "total": len(items),
                "filtered_stock_count": len(items),
                "stock_levels": items,
            }

        with dict_cursor(db) as cur:
            cur.execute("SELECT product_id, location_id, quantity FROM stock_levels LIMIT %s OFFSET %s", (limit, skip))
            rows = [dict(r) for r in cur.fetchall()]

        return {
            "items": rows,
            "total": len(rows),
            "filtered_stock_count": len(rows),
            "stock_levels": rows,
        }

    @staticmethod
    def filter_dashboard(
        db: Any,
        location_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> DashboardFilterResponse:
        """Alias for filter_dashboard compatibility."""
        target_wh = str(location_id) if location_id is not None else (str(warehouse_id) if warehouse_id else None)
        res = DashboardService.get_filtered(db, warehouse_id=target_wh, category_id=category, status=status)
        return DashboardFilterResponse(
            filtered_stock_count=res.get("filtered_stock_count", 0),
            stock_levels=[
                StockLevelItem(
                    product_id=int(item["product_id"]),
                    location_id=int(item.get("location_id", item.get("warehouse_id", 1))),
                    quantity=int(item.get("quantity", item.get("qty_delta", 0))),
                )
                for item in res.get("stock_levels", [])
            ],
        )
