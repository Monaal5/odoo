from typing import Optional, List
from pydantic import BaseModel, Field


class ProductForecastResponse(BaseModel):
    product: str = Field(..., description="Product name")
    days_to_stockout: int = Field(..., description="Estimated days remaining until stockout")
    recommended_order: float = Field(..., description="Recommended reorder quantity")
    product_id: Optional[str] = Field(None, description="Product UUID")
    current_stock: Optional[float] = Field(0.0, description="Current total on-hand stock")
    daily_consumption_rate: Optional[float] = Field(0.0, description="Average daily units consumed")


class ForecastListResponse(BaseModel):
    items: List[ProductForecastResponse]
    total: int
