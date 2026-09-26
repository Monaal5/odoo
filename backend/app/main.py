from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Developer 1 Routers (Auth & Master Data)
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.categories import router as categories_router
from app.api.warehouses import router as warehouses_router
from app.api.profile import router as profile_router
from app.api.reports import router as reports_router
from app.api.search import router as search_router

# Developer 2 Routers (Stock Operations & Intelligence)
from app.api.endpoints import router as system_router
from app.api.receipts import router as receipts_router
from app.api.deliveries import router as deliveries_router
from app.api.transfers import router as transfers_router
from app.api.adjustments import router as adjustments_router
from app.api.ledger import router as ledger_router
from app.api.dashboard import router as dashboard_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StockSense Real-Time Inventory Management System (IMS) API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Open CORS policy for frontend client integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all API Routers ─────────────────────────────────
PREFIX = settings.API_V1_STR

# Auth & Master Data
app.include_router(auth_router,       prefix=PREFIX)
app.include_router(users_router,      prefix=PREFIX)
app.include_router(products_router,   prefix=PREFIX)
app.include_router(categories_router, prefix=PREFIX)
app.include_router(warehouses_router, prefix=PREFIX)
app.include_router(profile_router,    prefix=PREFIX)
app.include_router(reports_router,    prefix=PREFIX)
app.include_router(search_router,     prefix=PREFIX)

# Stock Operations & Intelligence
app.include_router(system_router,      prefix=PREFIX)
app.include_router(receipts_router,    prefix=PREFIX)
app.include_router(deliveries_router,  prefix=PREFIX)
app.include_router(transfers_router,   prefix=PREFIX)
app.include_router(adjustments_router, prefix=PREFIX)
app.include_router(ledger_router,      prefix=PREFIX)
app.include_router(dashboard_router,   prefix=PREFIX)


@app.get("/", tags=["System"])
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health_check": f"{PREFIX}/health"
    }


@app.get(f"{PREFIX}/health", tags=["System"])
def health():
    """Quick liveness check — no DB call needed for container orchestration."""
    return {"status": "ok", "version": settings.VERSION}
