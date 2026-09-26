from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.database import get_db
from app.schemas.product import ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="", tags=["Search"])

@router.get("/search", response_model=List[ProductResponse])
@router.get("/products/search", response_model=List[ProductResponse])
def search_products(
    q: Optional[str] = Query("", description="SKU or product search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    conn=Depends(get_db)
):
    """Search products by SKU, name, or title."""
    return ProductService.list_products(conn, skip=skip, limit=limit, search=q)
