from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db.database import get_db
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.services.product_service import ProductService
from app.api.deps import get_current_user, require_manager

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    body: WarehouseCreate,
    conn=Depends(get_db),
    current_user: dict = Depends(require_manager),
):
    try:
        return ProductService.create_warehouse(conn, body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[WarehouseResponse])
def list_warehouses(
    active_only: bool = Query(False, description="Return only active warehouses"),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return ProductService.list_warehouses(conn, active_only=active_only)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    wh = ProductService.get_warehouse(conn, warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return wh


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: str,
    body: WarehouseUpdate,
    conn=Depends(get_db),
    current_user: dict = Depends(require_manager),
):
    wh = ProductService.update_warehouse(
        conn, warehouse_id, body.model_dump(exclude_none=True)
    )
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return wh


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(
    warehouse_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(require_manager),
):
    if not ProductService.delete_warehouse(conn, warehouse_id):
        raise HTTPException(status_code=404, detail="Warehouse not found")
