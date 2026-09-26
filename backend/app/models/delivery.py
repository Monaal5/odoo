from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Delivery(Base):
    """Delivery Order document for outgoing goods."""
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    delivery_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    warehouse_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="Draft")  # Draft, Pick, Pack, Done, Canceled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("DeliveryItem", back_populates="delivery", cascade="all, delete-orphan")

    @property
    def customer(self):
        return self.customer_name


class DeliveryItem(Base):
    """Line items for a Delivery Order."""
    __tablename__ = "delivery_items"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False)
    product_id = Column(Integer, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, default=1, index=True)
    quantity = Column(Integer, nullable=False)

    delivery = relationship("Delivery", back_populates="items")
