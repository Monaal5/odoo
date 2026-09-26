import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "StockSense Inventory Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Security Configuration
    SECRET_KEY: str = "super-secret-stocksense-key-change-in-production"
    
    # Database Configuration (PostgreSQL URL as Primary Default)
    # Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "stocksense_db"
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/stocksense_db"
    
    # Odoo XML-RPC / JSON-RPC Connection Settings
    ODOO_URL: Optional[str] = "http://localhost:8069"
    ODOO_DB: Optional[str] = "odoo_db"
    ODOO_USER: Optional[str] = "admin"
    ODOO_PASSWORD: Optional[str] = "admin"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
