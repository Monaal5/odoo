from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DeliveryItemCreate(BaseModel):
    product_id: int
    location_id: int = 1
    quantity: int

class DeliveryItemResponse(DeliveryItemCreate):
    id: int
    delivery_id: int

    model_config = ConfigDict(from_attributes=True)

class DeliveryCreate(BaseModel):
    customer_name: str
    items: List[DeliveryItemCreate]

class DeliveryResponse(BaseModel):
    id: int
    delivery_number: str
    customer_name: str
    status: str
    items: List[DeliveryItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
