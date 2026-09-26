from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.dashboard import DashboardKPIsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/kpis", response_model=DashboardKPIsResponse)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Retrieve operational dashboard KPIs and live stock counts."""
    return DashboardService.get_kpis(db)
