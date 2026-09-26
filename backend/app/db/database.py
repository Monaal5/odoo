import logging
import sqlite3
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Raw Database Connection (psycopg2 / sqlite3 for Dev 1) ──

def get_connection():
    """Create and return a DB connection with autocommit enabled, falling back to SQLite if PostgreSQL is unreachable."""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            connect_timeout=3,
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.warning(f"PostgreSQL raw connection failed ({e}); falling back to local SQLite database.")
        conn = sqlite3.connect("./hackathon.db", check_same_thread=False)
        conn.isolation_level = None
        return conn


def get_db():
    """FastAPI dependency: yields a raw DB connection with autocommit enabled for Dev 1 routes."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_raw_db():
    """Alias for get_db."""
    return get_db()


from contextlib import contextmanager

@contextmanager
def dict_cursor(conn):
    """
    Return a context-managed cursor that produces dict-like rows for psycopg2, sqlite3, or SQLAlchemy Session objects.
    """
    # If a SQLAlchemy Session was passed instead of a raw connection, unwrap the DBAPI connection
    if hasattr(conn, "connection"):
        try:
            raw_conn = conn.connection().dbapi_connection
            if raw_conn is not None:
                conn = raw_conn
        except Exception:
            pass

    if hasattr(conn, "cursor_factory"):
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
        finally:
            cur.close()
    elif hasattr(conn, "row_factory"):
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
    else:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()


# ─── SQLAlchemy Setup (for Dev 2 compatibility) ──────────────

db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)


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


def get_sqlalchemy_db():
    """Dependency generator to yield SQLAlchemy database sessions per request (for Dev 2 routes)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
