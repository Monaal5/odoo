from sqlalchemy import Column, Integer, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base

class StockLevel(Base):
    """Derived/Cached current stock level per product per location."""
    __tablename__ = "stock_levels"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('product_id', 'location_id', name='_product_location_uc'),
    )
