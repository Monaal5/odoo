from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.schemas.health import HealthCheck
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item_service import ItemService
from app.services.odoo_service import OdooService
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthCheck, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint validating application, database, and Odoo connectivity."""
    db_status = "Healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"Unhealthy ({str(e)})"
        
    odoo_res = OdooService.check_connection()
    odoo_status = (
        f"Connected (v{odoo_res.get('server_version')})" 
        if odoo_res.get("connected") 
        else f"Disconnected ({odoo_res.get('error', 'Target server unreachable')})"
    )
    
    return HealthCheck(
        status="OK",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        database=db_status,
        odoo_connection=odoo_status,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@router.get("/items", response_model=List[ItemResponse], tags=["Items"])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all items from local database."""
    return ItemService.get_items(db, skip=skip, limit=limit)

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["Items"])
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item in local database."""
    return ItemService.create_item(db, item_in)

@router.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item details by ID."""
    item = ItemService.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return item

@router.put("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    """Update existing item."""
    updated_item = ItemService.update_item(db, item_id, item_in)
    if not updated_item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return updated_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by ID."""
    success = ItemService.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    return None

@router.get("/odoo/status", tags=["Odoo Integration"])
def odoo_status():
    """Check connectivity to target Odoo instance."""
    return OdooService.check_connection()

@router.get("/odoo/fetch-partners", tags=["Odoo Integration"])
def fetch_odoo_partners(limit: int = 10):
    """Fetch contacts/partners (res.partner) directly from Odoo via XML-RPC."""
    return OdooService.search_read_records("res.partner", domain=[], fields=["id", "name", "email", "phone"], limit=limit)
