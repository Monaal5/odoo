from typing import Optional, List
from pydantic import BaseModel, Field


class AnomalyItem(BaseModel):
    severity: str = Field(..., description="Severity level: High, Medium, or Low")
    message: str = Field(..., description="Human-readable anomaly description")
    anomaly_type: Optional[str] = Field(None, description="UNUSUAL_DELIVERY | REPEATED_DAMAGE | RAPID_SHRINKAGE")
    product_id: Optional[str] = Field(None, description="Associated product ID")
    product_name: Optional[str] = Field(None, description="Associated product name")


class AnomaliesResponse(BaseModel):
    anomalies: List[AnomalyItem]
    total_anomalies: int


class AnalyticsSummaryResponse(BaseModel):
    total_consumption_30d: float
    total_shrinkage_30d: float
    high_velocity_products_count: int
    anomalies_count: int
