from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoleUpdate(BaseModel):
    role: str = Field(..., description="Role must be 'inventory_manager' or 'warehouse_staff'")
