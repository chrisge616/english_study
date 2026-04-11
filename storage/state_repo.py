from domain.models import WordState
from storage.db import get_conn


def get_state(word_id: int) -> WordState | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM word_state WHERE word_id = ?", (word_id,)).fetchone()
        if not row:
            return None
        return WordState(**dict(row))


def create_default_state(word_id: int) -> WordState:
    state = WordState(word_id=word_id, status="NEW")
    save_state(state)
    return state


def save_state(state: WordState) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO word_state (
                word_id, status, memory_strength, difficulty_score, stability_score,
                due_at, last_seen_at, last_reviewed_at, correct_streak, wrong_streak
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(word_id) DO UPDATE SET
                status=excluded.status,
                memory_strength=excluded.memory_strength,
                difficulty_score=excluded.difficulty_score,
                stability_score=excluded.stability_score,
                due_at=excluded.due_at,
                last_seen_at=excluded.last_seen_at,
                last_reviewed_at=excluded.last_reviewed_at,
                correct_streak=excluded.correct_streak,
                wrong_streak=excluded.wrong_streak
            """,
            (
                state.word_id,
                state.status,
                state.memory_strength,
                state.difficulty_score,
                state.stability_score,
                state.due_at,
                state.last_seen_at,
                state.last_reviewed_at,
                state.correct_streak,
                state.wrong_streak,
            ),
        )


def list_state_rows() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT words.lemma, words.display_text, word_state.*
            FROM word_state
            JOIN words ON words.id = word_state.word_id
            WHERE words.is_active = 1
            """
        ).fetchall()
        return [dict(r) for r in rows]
