from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AlertResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    current_stock: int
    min_stock: int
    status: str
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
