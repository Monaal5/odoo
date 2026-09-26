from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.stock_ledger import StockLedgerEntry
from app.models.stock_level import StockLevel

class LedgerService:
    """Service handling append-only Stock Ledger writes and derived StockLevel synchronization."""

    @staticmethod
    def record_move(
        db: Session,
        product_id: int,
        location_id: int,
        qty_delta: int,
        source_doc_type: str,
        source_doc_id: int
    ) -> StockLedgerEntry:
        """Writes an immutable entry to stock_ledger and updates stock_levels."""
        # 1. Create append-only ledger record
        entry = StockLedgerEntry(
            product_id=product_id,
            location_id=location_id,
            qty_delta=qty_delta,
            source_doc_type=source_doc_type.upper(),
            source_doc_id=source_doc_id
        )
        db.add(entry)

        # 2. Update cached StockLevel for product + location
        stock_level = db.query(StockLevel).filter(
            StockLevel.product_id == product_id,
            StockLevel.location_id == location_id
        ).first()

        if not stock_level:
            stock_level = StockLevel(
                product_id=product_id,
                location_id=location_id,
                quantity=qty_delta
            )
            db.add(stock_level)
        else:
            stock_level.quantity += qty_delta

        db.flush()
        return entry

    @staticmethod
    def get_history(
        db: Session,
        product_id: Optional[int] = None,
        location_id: Optional[int] = None,
        doc_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StockLedgerEntry]:
        """Query filterable stock movement audit log."""
        query = db.query(StockLedgerEntry)
        if product_id is not None:
            query = query.filter(StockLedgerEntry.product_id == product_id)
        if location_id is not None:
            query = query.filter(StockLedgerEntry.location_id == location_id)
        if doc_type:
            query = query.filter(StockLedgerEntry.source_doc_type == doc_type.upper())
        return query.order_by(StockLedgerEntry.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_current_stock(db: Session, product_id: int, location_id: int) -> int:
        """Get current stock level for a product at a location."""
        stock = db.query(StockLevel).filter(
            StockLevel.product_id == product_id,
            StockLevel.location_id == location_id
        ).first()
        return stock.quantity if stock else 0
