from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, conn=Depends(get_db)):
    try:
        return ProductService.create_category(conn, body.name, body.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[CategoryResponse])
def list_categories(conn=Depends(get_db)):
    return ProductService.list_categories(conn)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: str, conn=Depends(get_db)):
    cat = ProductService.get_category(conn, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: str, body: CategoryUpdate, conn=Depends(get_db)):
    cat = ProductService.update_category(conn, category_id, body.name, body.description)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, conn=Depends(get_db)):
    if not ProductService.delete_category(conn, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
