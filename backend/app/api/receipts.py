from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import get_db
from app.schemas.receipt import ReceiptCreate, ReceiptResponse
from app.services.receipt_service import ReceiptService
from app.api.deps import get_current_user

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt(
    data: ReceiptCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new incoming stock Receipt in Draft status."""
    try:
        supplier_name = data.supplier
        return ReceiptService.create_receipt(
            conn,
            supplier=supplier_name,
            warehouse_id=data.warehouse_id,
            items=[item.model_dump() for item in data.items],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ReceiptResponse])
def list_receipts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all receipts."""
    return ReceiptService.list_receipts(conn, skip=skip, limit=limit)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
    receipt_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get receipt by ID."""
    receipt = ReceiptService.get_receipt(conn, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@router.put("/{receipt_id}/validate", response_model=ReceiptResponse)
def validate_receipt_put(
    receipt_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Validate Receipt -> Increases stock and logs immutable entries in Stock Ledger (PUT)."""
    try:
        return ReceiptService.validate_receipt(conn, receipt_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{receipt_id}/validate", response_model=ReceiptResponse)
def validate_receipt_post(
    receipt_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Validate Receipt (POST alias)."""
    return validate_receipt_put(receipt_id, conn, current_user)
