from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class DeliveryItemCreate(BaseModel):
    product_id: Union[str, int]
    quantity: float = Field(..., gt=0, description="Quantity delivered")


class DeliveryItemResponse(BaseModel):
    id: Union[str, int]
    delivery_id: Union[str, int]
    product_id: Union[str, int]
    quantity: float


class DeliveryCreate(BaseModel):
    customer: str = Field(..., alias="customer_name", description="Customer name")
    warehouse_id: Optional[Union[str, int]] = None
    items: List[DeliveryItemCreate]

    class Config:
        populate_by_name = True


class DeliveryResponse(BaseModel):
    id: Union[str, int]
    delivery_number: str
    customer: str
    warehouse_id: Optional[Union[str, int]] = None
    status: str
    items: List[DeliveryItemResponse]
    created_at: datetime
    updated_at: datetime
