from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/transfers", tags=["Internal Transfers"])

@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(data: TransferCreate, db: Session = Depends(get_db)):
    """Create a new Internal Transfer request."""
    return InventoryService.create_transfer(db, data)

@router.post("/{transfer_id}/validate", response_model=TransferResponse)
def validate_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """Validate Internal Transfer -> Moves stock between locations and updates Stock Ledger."""
    return InventoryService.validate_transfer(db, transfer_id)
