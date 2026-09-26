from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.categories import router as categories_router
from app.api.warehouses import router as warehouses_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="StockSense IMS — Inventory Management System API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Open CORS for frontend dev — restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────
PREFIX = settings.API_V1_STR

app.include_router(auth_router,       prefix=PREFIX)
app.include_router(users_router,      prefix=PREFIX)
app.include_router(products_router,   prefix=PREFIX)
app.include_router(categories_router, prefix=PREFIX)
app.include_router(warehouses_router, prefix=PREFIX)


@app.get("/", tags=["System"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "version": settings.VERSION,
    }


@app.get(f"{PREFIX}/health", tags=["System"])
def health():
    """Quick liveness check — no DB call needed for container orchestration."""
    return {"status": "ok", "version": settings.VERSION}
