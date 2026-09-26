from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LedgerEntryResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    qty_delta: int
    source_doc_type: str
    source_doc_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
