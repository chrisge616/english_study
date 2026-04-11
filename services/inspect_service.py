from __future__ import annotations

import json
from datetime import datetime

from domain.scoring import compute_priority
from storage.db import get_conn
from storage.state_repo import list_state_rows


VALID_SORTS = {"priority", "alpha", "status"}


def _format_float(value: float) -> str:
    return f"{value:.1f}"


def _truncate(value: str | None, width: int) -> str:
    text = (value or "").strip()
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def _sort_rows(rows: list[dict], sort_by: str) -> list[dict]:
    if sort_by not in VALID_SORTS:
        sort_by = "priority"

    if sort_by == "alpha":
        return sorted(rows, key=lambda r: (r["display_text"].lower(), r["status"]))

    if sort_by == "status":
        status_order = {"WEAK": 0, "NEW": 1, "STABLE": 2, "STRONG": 3, "ARCHIVED": 4}
        return sorted(
            rows,
            key=lambda r: (status_order.get(r["status"], 99), -float(r.get("priority_score", 0.0)), r["display_text"].lower()),
        )

    return sorted(rows, key=lambda r: (-float(r.get("priority_score", 0.0)), r["display_text"].lower()))


def build_state_inspection_text(
    *,
    status: str | None = None,
    limit: int | None = None,
    sort_by: str = "priority",
) -> str:
    rows = list_state_rows()

    for row in rows:
        row["priority_score"] = compute_priority(row)

    if status:
        normalized = status.strip().upper()
        rows = [row for row in rows if row["status"].upper() == normalized]

    rows = _sort_rows(rows, sort_by)

    if limit is not None and limit > 0:
        rows = rows[:limit]

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# State Inspection ({generated_at})",
        "",
        f"Rows: {len(rows)}",
    ]

    if status:
        lines.append(f"Filter: status={status.upper()}")
    lines.append(f"Sort: {sort_by}")
    if limit is not None and limit > 0:
        lines.append(f"Limit: {limit}")

    lines.extend([
        "",
        "| Word | Status | Priority | Memory | Diff | Stability | Correct | Wrong | Due | Last Review |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ])

    for row in rows:
        lines.append(
            "| {word} | {status} | {priority} | {memory} | {difficulty} | {stability} | {correct} | {wrong} | {due} | {reviewed} |".format(
                word=_truncate(row.get("display_text"), 24),
                status=row.get("status", ""),
                priority=_format_float(float(row.get("priority_score", 0.0))),
                memory=_format_float(float(row.get("memory_strength", 0.0))),
                difficulty=_format_float(float(row.get("difficulty_score", 0.0))),
                stability=_format_float(float(row.get("stability_score", 0.0))),
                correct=int(row.get("correct_streak", 0)),
                wrong=int(row.get("wrong_streak", 0)),
                due=_truncate(row.get("due_at"), 16),
                reviewed=_truncate(row.get("last_reviewed_at"), 16),
            )
        )

    if not rows:
        lines.append("| _no rows_ |  |  |  |  |  |  |  |  |  |")

    return "\n".join(lines)


def _find_word_row(query: str) -> dict | None:
    normalized = query.strip().lower()
    if not normalized:
        return None

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT
                words.id,
                words.lemma,
                words.display_text,
                words.item_type,
                words.created_at,
                words.first_seen_at,
                words.is_active,
                word_state.status,
                word_state.memory_strength,
                word_state.difficulty_score,
                word_state.stability_score,
                word_state.due_at,
                word_state.last_seen_at,
                word_state.last_reviewed_at,
                word_state.correct_streak,
                word_state.wrong_streak
            FROM words
            LEFT JOIN word_state ON word_state.word_id = words.id
            WHERE lower(words.lemma) = ?
               OR lower(words.display_text) = ?
            LIMIT 1
            """,
            (normalized, normalized),
        ).fetchone()

        if row:
            return dict(row)

        row = conn.execute(
            """
            SELECT
                words.id,
                words.lemma,
                words.display_text,
                words.item_type,
                words.created_at,
                words.first_seen_at,
                words.is_active,
                word_state.status,
                word_state.memory_strength,
                word_state.difficulty_score,
                word_state.stability_score,
                word_state.due_at,
                word_state.last_seen_at,
                word_state.last_reviewed_at,
                word_state.correct_streak,
                word_state.wrong_streak
            FROM words
            LEFT JOIN word_state ON word_state.word_id = words.id
            WHERE lower(words.lemma) LIKE ?
               OR lower(words.display_text) LIKE ?
            ORDER BY words.lemma
            LIMIT 1
            """,
            (f"%{normalized}%", f"%{normalized}%"),
        ).fetchone()
        return dict(row) if row else None


def _list_recent_evidence(word_id: int, limit: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                evidence.evidence_type,
                evidence.strength,
                evidence.source,
                evidence.payload_json,
                evidence.created_at,
                evidence.session_id
            FROM evidence
            WHERE evidence.word_id = ?
            ORDER BY evidence.created_at DESC, evidence.id DESC
            LIMIT ?
            """,
            (word_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def _list_recent_session_items(word_id: int, limit: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                session_items.task_type,
                session_items.result,
                session_items.confidence,
                session_items.notes,
                session_items.session_id
            FROM session_items
            WHERE session_items.word_id = ?
            ORDER BY session_items.id DESC
            LIMIT ?
            """,
            (word_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def _list_mistake_patterns(word_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT pattern_type, count, last_seen_at
            FROM mistake_patterns
            WHERE word_id = ?
            ORDER BY count DESC, last_seen_at DESC
            """,
            (word_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def _payload_preview(payload_json: str | None, max_len: int = 60) -> str:
    if not payload_json:
        return ""
    try:
        payload = json.loads(payload_json)
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    except Exception:
        text = payload_json
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def build_word_inspection_text(word: str, *, evidence_limit: int = 8) -> str:
    row = _find_word_row(word)
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if not row:
        return f"# Word Inspection ({generated_at})\n\nNo word matched: `{word}`"

    row["priority_score"] = compute_priority({
        "status": row.get("status") or "NEW",
        "due_at": row.get("due_at"),
        "wrong_streak": row.get("wrong_streak", 0),
        "memory_strength": row.get("memory_strength", 0.0),
    })

    evidence_rows = _list_recent_evidence(int(row["id"]), evidence_limit)
    session_rows = _list_recent_session_items(int(row["id"]), evidence_limit)
    pattern_rows = _list_mistake_patterns(int(row["id"]))

    lines = [
        f"# Word Inspection ({generated_at})",
        "",
        f"Query: `{word}`",
        "",
        "## Summary",
        "",
        f"- Display: {row.get('display_text', '')}",
        f"- Lemma: {row.get('lemma', '')}",
        f"- Type: {row.get('item_type', '')}",
        f"- Active: {row.get('is_active', '')}",
        f"- Status: {row.get('status') or 'NEW'}",
        f"- Priority: {_format_float(float(row.get('priority_score', 0.0)))}",
        f"- Memory: {_format_float(float(row.get('memory_strength', 0.0) or 0.0))}",
        f"- Difficulty: {_format_float(float(row.get('difficulty_score', 0.0) or 0.0))}",
        f"- Stability: {_format_float(float(row.get('stability_score', 0.0) or 0.0))}",
        f"- Correct Streak: {int(row.get('correct_streak', 0) or 0)}",
        f"- Wrong Streak: {int(row.get('wrong_streak', 0) or 0)}",
        f"- Due At: {row.get('due_at') or ''}",
        f"- Last Seen: {row.get('last_seen_at') or ''}",
        f"- Last Reviewed: {row.get('last_reviewed_at') or ''}",
        f"- Created At: {row.get('created_at') or ''}",
        f"- First Seen At: {row.get('first_seen_at') or ''}",
        "",
        "## Recent Evidence",
        "",
        "| Created At | Type | Source | Strength | Session | Payload |",
        "|---|---|---|---:|---|---|",
    ]

    if evidence_rows:
        for ev in evidence_rows:
            lines.append(
                "| {created_at} | {etype} | {source} | {strength} | {session} | {payload} |".format(
                    created_at=_truncate(ev.get("created_at"), 19),
                    etype=_truncate(ev.get("evidence_type"), 20),
                    source=_truncate(ev.get("source"), 14),
                    strength=_format_float(float(ev.get("strength", 0.0))),
                    session=_truncate(ev.get("session_id"), 20),
                    payload=_truncate(_payload_preview(ev.get("payload_json")), 60),
                )
            )
    else:
        lines.append("| _no evidence_ |  |  |  |  |  |")

    lines.extend([
        "",
        "## Recent Session Items",
        "",
        "| Session | Task | Result | Confidence | Notes |",
        "|---|---|---|---:|---|",
    ])

    if session_rows:
        for item in session_rows:
            conf = item.get("confidence")
            conf_text = "" if conf is None else _format_float(float(conf))
            lines.append(
                "| {session} | {task} | {result} | {confidence} | {notes} |".format(
                    session=_truncate(item.get("session_id"), 20),
                    task=_truncate(item.get("task_type"), 12),
                    result=_truncate(item.get("result"), 10),
                    confidence=conf_text,
                    notes=_truncate(item.get("notes"), 50),
                )
            )
    else:
        lines.append("| _no session items_ |  |  |  |  |")

    lines.extend([
        "",
        "## Mistake Patterns",
        "",
        "| Pattern | Count | Last Seen |",
        "|---|---:|---|",
    ])

    if pattern_rows:
        for pattern in pattern_rows:
            lines.append(
                "| {ptype} | {count} | {last_seen} |".format(
                    ptype=_truncate(pattern.get("pattern_type"), 32),
                    count=int(pattern.get("count", 0)),
                    last_seen=_truncate(pattern.get("last_seen_at"), 19),
                )
            )
    else:
        lines.append("| _no patterns_ |  |  |")

    return "\n".join(lines)
