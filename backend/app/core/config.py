from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file into os.environ
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "StockSense IMS API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # JWT Security
    SECRET_KEY: str = "super-secret-stocksense-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI API Keys
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # PostgreSQL — raw connection params (used by psycopg2)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "stocksense"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # PostgreSQL URL & POSTGRES_* params
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "stocksense"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/stocksense"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
