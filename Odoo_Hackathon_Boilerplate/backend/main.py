from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base
import app.models  # Ensures all ORM models are registered with Base metadata

from app.api.endpoints import router as system_router
from app.api.receipts import router as receipts_router
from app.api.deliveries import router as deliveries_router
from app.api.transfers import router as transfers_router
from app.api.adjustments import router as adjustments_router
from app.api.ledger import router as ledger_router
from app.api.dashboard import router as dashboard_router

# Auto-create tables on launch for fast development
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StockSense Real-Time Inventory Management System (IMS) API.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Open CORS policy for frontend client integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(receipts_router, prefix=settings.API_V1_STR)
app.include_router(deliveries_router, prefix=settings.API_V1_STR)
app.include_router(transfers_router, prefix=settings.API_V1_STR)
app.include_router(adjustments_router, prefix=settings.API_V1_STR)
app.include_router(ledger_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["System"])
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }
