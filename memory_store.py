import sqlite3
from typing import List, Optional

DB_PATH = "memory.db"

def _conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with _conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            item TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_session ON memories(session_id)")

def add_memory(session_id: str, item: str):
    with _conn() as con:
        con.execute(
            "INSERT INTO memories(session_id, item) VALUES(?, ?)",
            (session_id, item)
        )

def get_memories(session_id: str, limit: int = 50) -> List[str]:
    with _conn() as con:
        cur = con.execute(
            "SELECT item FROM memories WHERE session_id=? ORDER BY id ASC LIMIT ?",
            (session_id, limit)
        )
        return [row[0] for row in cur.fetchall()]

def clear_session(session_id: str):
    with _conn() as con:
        con.execute("DELETE FROM memories WHERE session_id=?", (session_id,))

def find_first_by_prefix(session_id: str, prefix: str) -> Optional[str]:
    with _conn() as con:
        cur = con.execute(
            "SELECT item FROM memories WHERE session_id=? AND item LIKE ? ORDER BY id ASC LIMIT 1",
            (session_id, f"{prefix}%")
        )
        row = cur.fetchone()
        return row[0] if row else None
