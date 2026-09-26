from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.stock_level import StockLevel
from app.models.stock_ledger import StockLedgerEntry
from app.models.receipt import Receipt
from app.models.delivery import Delivery
from app.models.transfer import InternalTransfer
from app.schemas.dashboard import DashboardKPIsResponse, StockLevelItem

class DashboardService:
    """Service providing aggregate operational KPIs and stock metrics."""

    @staticmethod
    def get_kpis(db: Session) -> DashboardKPIsResponse:
        # Total products with positive stock
        products_in_stock = db.query(func.count(func.distinct(StockLevel.product_id))).filter(StockLevel.quantity > 0).scalar() or 0

        # Total units across all locations
        total_units = db.query(func.sum(StockLevel.quantity)).scalar() or 0

        # Low stock count (items with stock <= 5)
        low_stock = db.query(func.count(StockLevel.id)).filter(StockLevel.quantity <= 5).scalar() or 0

        # Pending document counts
        pending_recs = db.query(func.count(Receipt.id)).filter(Receipt.status != "Done").scalar() or 0
        pending_dels = db.query(func.count(Delivery.id)).filter(Delivery.status != "Done").scalar() or 0
        pending_trfs = db.query(func.count(InternalTransfer.id)).filter(InternalTransfer.status != "Done").scalar() or 0

        # Total ledger entries
        total_ledger = db.query(func.count(StockLedgerEntry.id)).scalar() or 0

        # Stock levels overview
        stock_levels_raw = db.query(StockLevel).all()
        stock_levels = [
            StockLevelItem(
                product_id=s.product_id,
                location_id=s.location_id,
                quantity=s.quantity
            )
            for s in stock_levels_raw
        ]

        return DashboardKPIsResponse(
            total_products_in_stock=products_in_stock,
            total_units_in_stock=total_units,
            low_stock_count=low_stock,
            pending_receipts=pending_recs,
            pending_deliveries=pending_dels,
            pending_transfers=pending_trfs,
            total_ledger_transactions=total_ledger,
            stock_levels=stock_levels
        )
