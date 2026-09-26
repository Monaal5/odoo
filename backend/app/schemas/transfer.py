from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransferCreate(BaseModel):
    product_id: Union[str, int]
    from_warehouse: Optional[Union[str, int]] = Field(None, alias="from_warehouse_id")
    to_warehouse: Optional[Union[str, int]] = Field(None, alias="to_warehouse_id")
    quantity: float = Field(..., gt=0)

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: dict):
        if isinstance(data, dict):
            if "from_warehouse" not in data:
                if "from_location_id" in data:
                    data["from_warehouse"] = data["from_location_id"]
                elif "from_warehouse_id" in data:
                    data["from_warehouse"] = data["from_warehouse_id"]
            if "to_warehouse" not in data:
                if "to_location_id" in data:
                    data["to_warehouse"] = data["to_location_id"]
                elif "to_warehouse_id" in data:
                    data["to_warehouse"] = data["to_warehouse_id"]
        return data

    model_config = ConfigDict(populate_by_name=True)


class TransferResponse(BaseModel):
    id: Union[str, int]
    transfer_number: str
    product_id: Union[str, int]
    from_warehouse: Optional[Union[str, int]] = None
    to_warehouse: Optional[Union[str, int]] = None
    quantity: float
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

