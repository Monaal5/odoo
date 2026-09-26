from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "General"
    is_active: bool = True
    odoo_ref_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    odoo_ref_id: Optional[int] = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
