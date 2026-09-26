from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class StockLedgerEntry(Base):
    """Append-only Stock Ledger Entry representing every stock movement."""
    __tablename__ = "stock_ledger"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    qty_delta = Column(Integer, nullable=False)  # positive for gain, negative for reduction
    source_doc_type = Column(String(50), nullable=False, index=True)  # RECEIPT, DELIVERY, TRANSFER, ADJUSTMENT
    source_doc_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
