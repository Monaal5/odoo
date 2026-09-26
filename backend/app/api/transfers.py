from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import get_db
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.transfer_service import TransferService
from app.api.deps import get_current_user

router = APIRouter(prefix="/transfers", tags=["Internal Transfers"])


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(
    data: TransferCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new internal stock transfer in Draft status."""
    try:
        from_wh = data.from_warehouse
        to_wh = data.to_warehouse
        return TransferService.create_transfer(
            conn,
            product_id=data.product_id,
            from_warehouse=from_wh,
            to_warehouse=to_wh,
            quantity=data.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[TransferResponse])
def list_transfers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List internal transfers."""
    return TransferService.list_transfers(conn, skip=skip, limit=limit)


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer(
    transfer_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get internal transfer by ID."""
    transfer = TransferService.get_transfer(conn, transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.put("/{transfer_id}/validate", response_model=TransferResponse)
def validate_transfer_put(
    transfer_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Validate transfer -> Complete transfer by decreasing source stock,
    increasing destination stock, and logging immutable entries in Stock Ledger.
    """
    try:
        return TransferService.validate_transfer(conn, transfer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{transfer_id}/validate", response_model=TransferResponse)
def validate_transfer_post(
    transfer_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Validate transfer (POST alias)."""
    return validate_transfer_put(transfer_id, conn, current_user)
