from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.schemas.analytics import AnomaliesResponse, AnalyticsSummaryResponse
from app.services.anomaly_service import AnomalyService
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Anomaly Detection"])


@router.get("/anomalies", response_model=AnomaliesResponse)
def get_anomalies(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Anomaly Detection Endpoint.

    Detects operational events like:
    - Delivery volume much larger than normal (spikes)
    - Repeated damaged items & shrinkage count adjustments
    - Imminent stockout risks

    Example Response:
    ```json
    {
      "anomalies": [
        {
          "severity": "High",
          "message": "Bolt deliveries are 3× higher than weekly average."
        }
      ],
      "total_anomalies": 1
    }
    ```
    """
    return AnomalyService.detect_anomalies(conn)


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Executive Analytics Summary.
    Provides 30-day consumption metrics, stock count shrinkage totals, and anomaly counts.
    """
    return AnomalyService.get_analytics_summary(conn)
