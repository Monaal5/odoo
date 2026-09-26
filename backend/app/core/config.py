import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Odoo Hackathon Boilerplate API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Security Configuration
    SECRET_KEY: str = "super-secret-odoo-hackathon-key-change-in-production"
    
    # Database Configuration (Defaults to SQLite for instant out-of-box hackathon setup)
    DATABASE_URL: str = "sqlite:///./hackathon.db"
    
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
