import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "audit.db"


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with closing(_connect()) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    course_name TEXT,
                    subject TEXT,
                    status TEXT,
                    details TEXT
                )
                """
            )


def log_event(event_type, course_name, subject, status, details=""):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with closing(_connect()) as conn:
        with conn:
            conn.execute(
                "INSERT INTO audit_logs (timestamp, event_type, course_name, subject, status, details) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, event_type, course_name, subject, status, str(details)[:1000]),
            )


def get_all_logs(limit: int = 500):
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT id, timestamp, event_type, course_name, subject, status, details "
            "FROM audit_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]