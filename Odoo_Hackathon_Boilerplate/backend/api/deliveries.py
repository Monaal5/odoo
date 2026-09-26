from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.delivery import DeliveryCreate, DeliveryResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])

@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(data: DeliveryCreate, db: Session = Depends(get_db)):
    """Create a new outgoing Delivery Order in Draft status."""
    return InventoryService.create_delivery(db, data)

@router.post("/{delivery_id}/validate", response_model=DeliveryResponse)
def validate_delivery(delivery_id: int, db: Session = Depends(get_db)):
    """Validate Delivery -> Decreases stock and logs immutable entries in Stock Ledger."""
    return InventoryService.validate_delivery(db, delivery_id)

@router.get("", response_model=List[DeliveryResponse])
def list_deliveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all delivery orders."""
    return InventoryService.list_deliveries(db, skip=skip, limit=limit)
