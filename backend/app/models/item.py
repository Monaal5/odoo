from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Item(Base):
    """SQLAlchemy ORM Model representing a hackathon entity linked with optional Odoo records."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="General", index=True)
    is_active = Column(Boolean, default=True)
    odoo_ref_id = Column(Integer, nullable=True, index=True)  # Reference ID to Odoo record (e.g. res.partner, product.product)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
