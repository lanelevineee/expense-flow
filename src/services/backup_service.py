import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


def backup_pg_to_sqlite(pg_db, sqlite_path: str = None) -> str:
    if not pg_db.is_postgres:
        raise RuntimeError("Backup requires PostgreSQL as source")

    from src import config as cfg
    if not sqlite_path:
        os.makedirs(cfg.CONFIG_DIR, exist_ok=True)
        sqlite_path = os.path.join(cfg.CONFIG_DIR, "backup.db")

    tables = [
        "staff", "expenses", "categories", "payment_methods",
        "recurring_expenses", "user_stats", "achievements",
        "user_achievements", "challenges", "challenge_progress", "audit_log",
    ]

    s_conn = sqlite3.connect(sqlite_path)
    s_conn.execute("PRAGMA journal_mode=WAL")
    s_conn.execute("PRAGMA foreign_keys=ON")

    cur = pg_db.conn.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' ORDER BY table_name"
    )
    pg_tables = {row[0] for row in cur.fetchall()}
    pg_db.putconn(pg_db.conn)

    for table in tables:
        if table not in pg_tables:
            continue

        cur2 = pg_db.conn.cursor()
        cur2.execute(f"SELECT * FROM {table}")
        rows = cur2.fetchall()
        pg_db.putconn(pg_db.conn)

        if not rows:
            continue

        col_names = [desc[0] for desc in cur2.description] if cur2.description else []

        s_conn.execute(f"DROP TABLE IF EXISTS {table}")
        cols_def = ", ".join(f"{c} TEXT" for c in col_names)
        s_conn.execute(f"CREATE TABLE {table} ({cols_def})")

        if rows and col_names:
            placeholders = ", ".join(["?"] * len(col_names))
            insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({placeholders})"
            for row in rows:
                vals = [str(v) if v is not None else None for v in row]
                s_conn.execute(insert_sql, vals)

        s_conn.commit()

    s_conn.close()
    return sqlite_path


def restore_sqlite_to_pg(sqlite_path: str, pg_db) -> int:
    if not pg_db.is_postgres:
        raise RuntimeError("Restore requires PostgreSQL as target")

    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"Backup file not found: {sqlite_path}")

    s_conn = sqlite3.connect(sqlite_path)
    s_conn.row_factory = sqlite3.Row

    total_rows = 0

    cur = s_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()]

    for table in tables:
        s_rows = s_conn.execute(f"SELECT * FROM {table}").fetchall()
        if not s_rows:
            continue

        col_names = list(s_rows[0].keys())

        conn = pg_db.conn
        pg_cur = conn.cursor()
        pg_cur.execute(f"DELETE FROM {table}")
        pg_db.putconn(conn)

        for row in s_rows:
            vals = [row[c] for c in col_names]
            ph = ", ".join(["%s"] * len(col_names))
            insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({ph})"

            conn2 = pg_db.conn
            pg_cur2 = conn2.cursor()
            try:
                pg_cur2.execute(insert_sql, vals)
                conn2.commit()
                total_rows += 1
            except Exception:
                conn2.rollback()
            finally:
                pg_db.putconn(conn2)

    s_conn.close()
    return total_rows
