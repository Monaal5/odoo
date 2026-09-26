from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Alert(Base):
    """Low Stock Alert generated automatically when stock falls below minimum threshold."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    current_stock = Column(Integer, nullable=False)
    min_stock = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, RESOLVED, DISMISSED
    message = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
