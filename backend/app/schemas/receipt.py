from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class ReceiptItemCreate(BaseModel):
    product_id: Union[str, int]
    location_id: Optional[Union[str, int]] = None
    warehouse_id: Optional[Union[str, int]] = None
    quantity: float = Field(..., gt=0, description="Quantity received")


class ReceiptItemResponse(BaseModel):
    id: Union[str, int]
    receipt_id: Union[str, int]
    product_id: Union[str, int]
    location_id: Optional[Union[str, int]] = 1
    quantity: float

    model_config = ConfigDict(from_attributes=True)


class ReceiptCreate(BaseModel):
    supplier: str = Field(..., alias="supplier_name", description="Supplier name")
    warehouse_id: Optional[Union[str, int]] = None
    items: List[ReceiptItemCreate]

    model_config = ConfigDict(populate_by_name=True)


class ReceiptResponse(BaseModel):
    id: Union[str, int]
    receipt_number: str
    supplier: str
    warehouse_id: Optional[Union[str, int]] = None
    status: str
    items: List[ReceiptItemResponse]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

