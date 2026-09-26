from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_sqlalchemy_db as get_db
from app.schemas.adjustment import AdjustmentCreate, AdjustmentResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/adjustments", tags=["Stock Adjustments"])

@router.post("", response_model=AdjustmentResponse, status_code=status.HTTP_201_CREATED)
def create_adjustment(data: AdjustmentCreate, db: Session = Depends(get_db)):
    """Reconcile physical stock count against system stock -> Writes delta to Stock Ledger."""
    return InventoryService.create_adjustment(db, data)
