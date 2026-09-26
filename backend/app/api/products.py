from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(body: ProductCreate, conn=Depends(get_db)):
    try:
        return ProductService.create_product(conn, body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    conn=Depends(get_db),
):
    return ProductService.list_products(conn, skip=skip, limit=limit,
                                        category_id=category_id, search=search)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, conn=Depends(get_db)):
    product = ProductService.get_product(conn, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, body: ProductUpdate, conn=Depends(get_db)):
    product = ProductService.update_product(
        conn, product_id, body.model_dump(exclude_none=True)
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, conn=Depends(get_db)):
    """Soft-deletes (sets is_active=False) to preserve stock ledger integrity."""
    if not ProductService.delete_product(conn, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
