import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL

def get_engine(url: str):
    engine_kwargs = {}
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_recycle"] = 3600

    eng = create_engine(url, echo=settings.DEBUG, **engine_kwargs)
    
    # Test connection if not sqlite
    if not url.startswith("sqlite"):
        try:
            with eng.connect() as conn:
                pass
        except Exception as e:
            logger.warning(f"PostgreSQL server unreachable at {url}: {e}. Defaulting to local SQLite database.")
            eng = create_engine("sqlite:///./hackathon.db", echo=settings.DEBUG, connect_args={"check_same_thread": False})
    return eng

engine = get_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency generator to yield SQLAlchemy database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
