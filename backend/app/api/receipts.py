from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.receipt import ReceiptCreate, ReceiptResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/receipts", tags=["Receipts"])

@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt(data: ReceiptCreate, db: Session = Depends(get_db)):
    """Create a new incoming stock Receipt in Draft status."""
    return InventoryService.create_receipt(db, data)

@router.post("/{receipt_id}/validate", response_model=ReceiptResponse)
def validate_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """Validate Receipt -> Increases stock and logs immutable entries in Stock Ledger."""
    return InventoryService.validate_receipt(db, receipt_id)

@router.get("", response_model=List[ReceiptResponse])
def list_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all receipts."""
    return InventoryService.list_receipts(db, skip=skip, limit=limit)
