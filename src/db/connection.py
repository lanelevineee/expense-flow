import os
import sqlite3
import logging
from typing import Optional
from contextlib import contextmanager

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(
        self,
        db_type: Optional[str] = None,
        pg_host: Optional[str] = None,
        pg_port: Optional[int] = None,
        pg_name: Optional[str] = None,
        pg_user: Optional[str] = None,
        pg_password: Optional[str] = None,
        sqlite_path: Optional[str] = None,
    ):
        self._pg_host = pg_host or os.getenv("DB_HOST", "")
        self._pg_port = pg_port or int(os.getenv("DB_PORT", "5432"))
        self._pg_name = pg_name or os.getenv("DB_NAME", "expense_tracker")
        self._pg_user = pg_user or os.getenv("DB_USER", "expense_user")
        self._pg_password = pg_password or os.getenv("DB_PASSWORD", "")
        self._sqlite_path = sqlite_path

        self._use_postgres = False
        self._pool = None
        self._conn = None
        self._psycopg2 = None

        if db_type == "postgresql" or (db_type is None and self._pg_host):
            if self._init_postgres():
                self._use_postgres = True
                return

        self._init_sqlite()

    def _init_postgres(self) -> bool:
        try:
            import psycopg2
            import psycopg2.pool
            import psycopg2.extras
            self._psycopg2 = psycopg2

            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=self._pg_host,
                port=self._pg_port,
                dbname=self._pg_name,
                user=self._pg_user,
                password=self._pg_password,
            )
            conn = self._pool.getconn()
            self._pool.putconn(conn)
            logger.info("Connected to PostgreSQL at %s:%d/%s", self._pg_host, self._pg_port, self._pg_name)
            return True
        except Exception as e:
            logger.warning("PostgreSQL connection failed: %s. Falling back to SQLite.", e)
            return False

    def _init_sqlite(self):
        from src import config as cfg

        os.makedirs(cfg.CONFIG_DIR, exist_ok=True)
        path = self._sqlite_path or os.path.join(cfg.CONFIG_DIR, "expenses.db")
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        logger.info("Connected to SQLite at %s", path)

    @property
    def is_postgres(self) -> bool:
        return self._use_postgres

    @contextmanager
    def cursor(self):
        if self._use_postgres:
            conn = self._pool.getconn()
            try:
                cur = conn.cursor(cursor_factory=self._psycopg2.extras.RealDictCursor)
                yield cur
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                self._pool.putconn(conn)
        else:
            cur = self._conn.cursor()
            try:
                yield cur
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    @staticmethod
    def _is_select(query: str) -> bool:
        stripped = query.lstrip().upper()
        return stripped.startswith("SELECT") or "RETURNING" in stripped

    @contextmanager
    def transaction(self):
        if self._use_postgres:
            conn = self._pool.getconn()
            try:
                cur = conn.cursor(cursor_factory=self._psycopg2.extras.RealDictCursor)
                yield cur
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                self._pool.putconn(conn)
        else:
            cur = self._conn.cursor()
            try:
                yield cur
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    def execute(self, query: str, params=None):
        with self.cursor() as cur:
            cur.execute(query, params or ())
            if self._is_select(query):
                return cur.fetchall()
            return []

    def execute_one(self, query: str, params=None):
        with self.cursor() as cur:
            cur.execute(query, params or ())
            if self._is_select(query):
                return cur.fetchone()
            return None

    def execute_insert(self, query: str, params=None):
        with self.cursor() as cur:
            cur.execute(query, params or ())
            if self._use_postgres and self._is_select(query):
                result = cur.fetchone()
                return result["id"] if result else None
            elif not self._use_postgres:
                return cur.lastrowid
            return None

    @property
    def conn(self):
        if self._use_postgres:
            return self._pool.getconn()
        return self._conn

    def putconn(self, conn):
        if self._use_postgres:
            self._pool.putconn(conn)

    def close(self):
        if self._use_postgres and self._pool:
            self._pool.closeall()
        elif self._conn:
            self._conn.close()
