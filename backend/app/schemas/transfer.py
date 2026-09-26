from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TransferCreate(BaseModel):
    product_id: int
    from_location_id: int
    to_location_id: int
    quantity: int

class TransferResponse(TransferCreate):
    id: int
    transfer_number: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
