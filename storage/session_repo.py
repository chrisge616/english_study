import json

from storage.db import get_conn


def session_exists(session_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM sessions WHERE id = ? LIMIT 1",
            (session_id,),
        ).fetchone()
        return row is not None


def create_session(
    session_id: str,
    session_type: str,
    source_file: str,
    created_at: str,
    metadata: dict | None = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions (id, session_type, source_file, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                session_type,
                source_file,
                created_at,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
