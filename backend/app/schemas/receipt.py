from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ReceiptItemCreate(BaseModel):
    product_id: int
    location_id: int = 1
    quantity: int

class ReceiptItemResponse(ReceiptItemCreate):
    id: int
    receipt_id: int

    model_config = ConfigDict(from_attributes=True)

class ReceiptCreate(BaseModel):
    supplier_name: str
    items: List[ReceiptItemCreate]

class ReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    supplier_name: str
    status: str
    items: List[ReceiptItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
