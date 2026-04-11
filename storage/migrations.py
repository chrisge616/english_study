from storage.db import get_conn


DDL = [
    """
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lemma TEXT NOT NULL UNIQUE,
        display_text TEXT NOT NULL,
        item_type TEXT NOT NULL,
        created_at TEXT NOT NULL,
        first_seen_at TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS word_state (
        word_id INTEGER PRIMARY KEY,
        status TEXT NOT NULL,
        memory_strength REAL NOT NULL DEFAULT 0,
        difficulty_score REAL NOT NULL DEFAULT 0,
        stability_score REAL NOT NULL DEFAULT 0,
        due_at TEXT,
        last_seen_at TEXT,
        last_reviewed_at TEXT,
        correct_streak INTEGER NOT NULL DEFAULT 0,
        wrong_streak INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(word_id) REFERENCES words(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        session_type TEXT NOT NULL,
        source_file TEXT,
        created_at TEXT NOT NULL,
        metadata_json TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        evidence_type TEXT NOT NULL,
        strength REAL NOT NULL DEFAULT 1.0,
        source TEXT NOT NULL,
        payload_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(word_id) REFERENCES words(id),
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS session_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        word_id INTEGER NOT NULL,
        task_type TEXT,
        result TEXT,
        confidence REAL,
        notes TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id),
        FOREIGN KEY(word_id) REFERENCES words(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mistake_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        pattern_type TEXT NOT NULL,
        count INTEGER NOT NULL DEFAULT 1,
        last_seen_at TEXT NOT NULL,
        FOREIGN KEY(word_id) REFERENCES words(id)
    )
    """,
]


def init_db() -> None:
    with get_conn() as conn:
        for ddl in DDL:
            conn.execute(ddl)
