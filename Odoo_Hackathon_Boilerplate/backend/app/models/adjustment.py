from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class StockAdjustment(Base):
    """Stock Adjustment record for count reconciliations and physical audits."""
    __tablename__ = "adjustments"

    id = Column(Integer, primary_key=True, index=True)
    adjustment_number = Column(String(100), unique=True, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    counted_qty = Column(Integer, nullable=False)
    system_qty = Column(Integer, nullable=False)
    delta_qty = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)  # Damage, Loss, Inventory Count Correction
    created_at = Column(DateTime(timezone=True), server_default=func.now())
