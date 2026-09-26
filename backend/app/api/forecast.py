from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db.database import get_db
from app.schemas.forecast import ProductForecastResponse, ForecastListResponse
from app.services.forecast_service import ForecastService
from app.api.deps import get_current_user

router = APIRouter(prefix="/forecast", tags=["Demand Forecasting"])


@router.get("", response_model=ForecastListResponse)
def list_forecasts(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List demand forecasts for all active products.
    """
    forecasts = ForecastService.get_all_forecasts(conn)
    return {"items": forecasts, "total": len(forecasts)}


@router.get("/{product_id}", response_model=ProductForecastResponse)
def get_product_forecast(
    product_id: str,
    warehouse_id: Optional[str] = Query(None, description="Optional warehouse UUID"),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Demand Forecast endpoint for a single product.

    Example Response:
    ```json
    {
      "product": "Steel Rod",
      "days_to_stockout": 6,
      "recommended_order": 120
    }
    ```
    """
    try:
        return ForecastService.get_product_forecast(conn, product_id, warehouse_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
