import json

from storage.db import get_conn


def add_evidence(word_id: int, session_id: str, evidence_type: str, strength: float, source: str, payload: dict, created_at: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO evidence (word_id, session_id, evidence_type, strength, source, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (word_id, session_id, evidence_type, strength, source, json.dumps(payload, ensure_ascii=False), created_at),
        )


def add_session_item(session_id: str, word_id: int, task_type: str | None, result: str | None, confidence: float | None = None, notes: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO session_items (session_id, word_id, task_type, result, confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, word_id, task_type, result, confidence, notes),
        )
