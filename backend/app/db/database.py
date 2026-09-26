import logging
import sqlite3
from pathlib import Path
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Raw Database Connection (psycopg2 / sqlite3 for Dev 1) ──

_pg_unavailable = False  # Cache PG failure to avoid 3s timeout on every request
_SQLITE_DB_PATH = str((Path(__file__).parent.parent.parent.parent / "hackathon.db").resolve())
_schema_initialized = False


def get_connection():
    """Create and return a DB connection with autocommit enabled, falling back to SQLite if PostgreSQL is unreachable."""
    global _pg_unavailable, _schema_initialized

    if not _pg_unavailable:
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
            _pg_unavailable = True
            logger.warning(f"PostgreSQL raw connection failed ({e}); falling back to local SQLite database.")

    conn = sqlite3.connect(_SQLITE_DB_PATH, check_same_thread=False)
    conn.isolation_level = None
    try:
        schema_file = Path(__file__).parent.parent.parent.parent / "database" / "schema.sql"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()
                schema_sql = schema_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
                schema_sql = schema_sql.replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP")
                conn.executescript(schema_sql)
    except Exception as schema_err:
        logger.warning(f"SQLite schema auto-init warning: {schema_err}")
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

class SqliteDictCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    @staticmethod
    def _translate_sql(query: str) -> str:
        """Translate PostgreSQL-specific SQL to SQLite-compatible SQL."""
        if "%s" in query:
            query = query.replace("%s", "?")
        # NOW() is PostgreSQL; SQLite uses CURRENT_TIMESTAMP
        if "NOW()" in query.upper():
            import re
            query = re.sub(r'\bNOW\(\)', 'CURRENT_TIMESTAMP', query, flags=re.IGNORECASE)
        return query

    def execute(self, query, params=None):
        query = self._translate_sql(query)
        if params is not None:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)

    def executemany(self, query, params_seq):
        query = self._translate_sql(query)
        return self.cursor.executemany(query, params_seq)


    def fetchone(self):
        res = self.cursor.fetchone()
        return dict(res) if res is not None else None

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows] if rows else []

    def fetchmany(self, size=None):
        rows = self.cursor.fetchmany(size) if size else self.cursor.fetchmany()
        return [dict(r) for r in rows] if rows else []

    @property
    def rowcount(self):
        return self.cursor.rowcount

    @property
    def lastrowid(self):
        return self.cursor.lastrowid


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
        raw_cur = conn.cursor()
        wrapper = SqliteDictCursorWrapper(raw_cur)
        try:
            yield wrapper
        finally:
            raw_cur.close()
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
            eng = create_engine(f"sqlite:///{_SQLITE_DB_PATH}", echo=settings.DEBUG, connect_args={"check_same_thread": False})
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
