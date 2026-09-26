from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    """
    Audit Log table recording all important actions across system entities.
    Example entries:
      User: Monaal | Action: CREATE   | Entity: Product
      User: Rahul  | Action: VALIDATE | Entity: Receipt
      User: Admin  | Action: ADJUST   | Entity: Stock
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(100), nullable=True)
