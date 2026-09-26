import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from app.core.config import settings


def get_connection():
    """Create and return a raw psycopg2 connection."""
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    conn.autocommit = True
    return conn


def get_db():
    """
    FastAPI dependency: yields a psycopg2 connection with autocommit enabled.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def dict_cursor(conn):
    """Return a cursor that produces rows as dicts (RealDictRow)."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
