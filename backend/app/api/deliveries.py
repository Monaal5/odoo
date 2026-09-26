from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import get_db
from app.schemas.delivery import DeliveryCreate, DeliveryResponse
from app.services.delivery_service import DeliveryService
from app.api.deps import get_current_user

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    data: DeliveryCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new outgoing Delivery Order in Draft status."""
    try:
        return DeliveryService.create_delivery(
            conn,
            customer=data.customer,
            warehouse_id=data.warehouse_id,
            items=[item.model_dump() for item in data.items],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[DeliveryResponse])
def list_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all delivery orders."""
    return DeliveryService.list_deliveries(conn, skip=skip, limit=limit)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get delivery by ID."""
    delivery = DeliveryService.get_delivery(conn, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery order not found")
    return delivery


@router.put("/{delivery_id}/validate", response_model=DeliveryResponse)
def validate_delivery_put(
    delivery_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Validate Delivery -> Decreases stock and logs immutable entries in Stock Ledger (PUT)."""
    try:
        return DeliveryService.validate_delivery(conn, delivery_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{delivery_id}/validate", response_model=DeliveryResponse)
def validate_delivery_post(
    delivery_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Validate Delivery (POST alias)."""
    return validate_delivery_put(delivery_id, conn, current_user)
