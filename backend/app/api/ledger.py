from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.ledger import LedgerEntryResponse
from app.services.ledger_service import LedgerService

router = APIRouter(prefix="/ledger", tags=["Stock Ledger"])

@router.get("/history", response_model=List[LedgerEntryResponse])
def get_ledger_history(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    doc_type: Optional[str] = Query(None, description="Filter by document type (RECEIPT, DELIVERY, TRANSFER, ADJUSTMENT)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Retrieve filterable, read-only audit log of all stock movements."""
    return LedgerService.get_history(
        db=db,
        product_id=product_id,
        location_id=location_id,
        doc_type=doc_type,
        skip=skip,
        limit=limit
    )
