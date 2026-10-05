"""Tiny SQLite layer for the Red Gate demo target app."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the users table and seed a couple of rows (idempotent)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT NOT NULL DEFAULT 'user'
        )
        """
    )
    cur.execute("SELECT COUNT(*) AS n FROM users")
    if cur.fetchone()["n"] == 0:
        cur.executemany(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [
                ("alice", "alice-pw", "user"),
                ("admin", "super-secret-admin-pw", "admin"),
            ],
        )
    conn.commit()
    conn.close()
