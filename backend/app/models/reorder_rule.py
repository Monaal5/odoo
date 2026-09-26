from sqlalchemy import Column, Integer, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base

class ReorderRule(Base):
    """Reorder Rule establishing min/max stock thresholds per product and location."""
    __tablename__ = "reorder_rules"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    min_qty = Column(Integer, nullable=False, default=5)
    max_qty = Column(Integer, nullable=False, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('product_id', 'location_id', name='_reorder_rule_uc'),
    )
