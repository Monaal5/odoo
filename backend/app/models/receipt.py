from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Receipt(Base):
    """Receipt document for incoming goods."""
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(100), unique=True, nullable=False, index=True)
    supplier_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="Draft")  # Draft, Waiting, Ready, Done, Canceled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptItem(Base):
    """Line items for a Receipt."""
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, default=1, index=True)
    quantity = Column(Integer, nullable=False)

    receipt = relationship("Receipt", back_populates="items")
