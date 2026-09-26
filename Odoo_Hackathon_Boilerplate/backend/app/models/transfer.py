from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class InternalTransfer(Base):
    """Internal Transfer document moving stock between locations."""
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_number = Column(String(100), unique=True, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    from_location_id = Column(Integer, nullable=False, index=True)
    to_location_id = Column(Integer, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="Draft")  # Draft, Done, Canceled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
