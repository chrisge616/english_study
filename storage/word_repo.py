from storage.db import get_conn


def upsert_word(lemma: str, display_text: str, item_type: str, created_at: str) -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM words WHERE lemma = ?", (lemma,)).fetchone()
        if row:
            return int(row["id"])
        cur = conn.execute(
            "INSERT INTO words (lemma, display_text, item_type, created_at, first_seen_at) VALUES (?, ?, ?, ?, ?)",
            (lemma, display_text, item_type, created_at, created_at),
        )
        return int(cur.lastrowid)
