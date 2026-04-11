from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


RECENT_REVIEW_HOURS = 24
WEAK_REINFORCEMENT_QUOTA = 3


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    text = str(value).strip()
    if not text:
        return None

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _row_word(row: dict[str, Any]) -> str:
    candidates = [
        row.get("word"),
        row.get("lemma"),
        row.get("display_text"),
        row.get("item"),
        row.get("text"),
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate).strip()
    return ""


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)

    normalized["word"] = _row_word(row)
    normalized["status"] = str(
        row.get("status")
        or row.get("state")
        or "NEW"
    ).strip().upper()

    normalized["priority"] = _safe_float(
        row.get("priority", row.get("priority_score", 0.0))
    )
    normalized["memory_strength"] = _safe_float(
        row.get("memory_strength", row.get("memory", 0.0))
    )
    normalized["difficulty_score"] = _safe_float(
        row.get("difficulty_score", row.get("difficulty", row.get("diff", 0.0)))
    )
    normalized["stability_score"] = _safe_float(
        row.get("stability_score", row.get("stability", 0.0))
    )
    normalized["correct_streak"] = _safe_int(
        row.get("correct_streak", row.get("correct", 0))
    )
    normalized["wrong_streak"] = _safe_int(
        row.get("wrong_streak", row.get("wrong", 0))
    )

    normalized["due_at"] = row.get("due_at", row.get("due"))
    normalized["last_reviewed_at"] = row.get(
        "last_reviewed_at",
        row.get("last_review"),
    )

    return normalized


def _is_recently_reviewed(row: dict[str, Any], now: datetime) -> bool:
    last_reviewed = _parse_dt(row.get("last_reviewed_at"))
    if last_reviewed is None:
        return False
    return (now - last_reviewed) < timedelta(hours=RECENT_REVIEW_HOURS)


def _is_due(row: dict[str, Any], now: datetime) -> bool:
    due_at = _parse_dt(row.get("due_at"))
    if due_at is None:
        return True
    return due_at <= now


def _sort_key_due_first(row: dict[str, Any]) -> tuple:
    due_at = _parse_dt(row.get("due_at"))
    due_sort = due_at or datetime.max.replace(tzinfo=timezone.utc)

    return (
        -_safe_float(row.get("priority", 0.0)),
        due_sort,
        row.get("word", "").lower(),
    )


def _sort_key_new_first(row: dict[str, Any]) -> tuple:
    due_at = _parse_dt(row.get("due_at"))
    due_sort = due_at or datetime.max.replace(tzinfo=timezone.utc)

    return (
        0 if row.get("status") == "NEW" else 1,
        due_sort,
        row.get("word", "").lower(),
    )


def select_review_items(
    rows: list[dict[str, Any]],
    max_items: int = 12,
) -> list[dict[str, Any]]:
    """
    v2.2 selection policy

    Pass 1: all due items
    Pass 2: small WEAK reinforcement quota, even if not due
    Pass 3: unseen NEW items
    Pass 4: fallback pool, but avoid recently reviewed non-WEAK items
    """
    now = _now_utc()

    normalized_rows = [_normalize_row(row) for row in rows]
    normalized_rows = [row for row in normalized_rows if row.get("word")]

    selected: list[dict[str, Any]] = []
    seen_words: set[str] = set()

    def try_add(row: dict[str, Any]) -> None:
        word = row["word"]
        if not word:
            return
        if word in seen_words:
            return
        if len(selected) >= max_items:
            return

        selected.append(row)
        seen_words.add(word)

    # Pass 1: due items only
    due_pool = [row for row in normalized_rows if _is_due(row, now)]
    due_pool.sort(key=_sort_key_due_first)

    for row in due_pool:
        try_add(row)

    # Pass 2: small weak reinforcement quota
    # Important: do NOT apply recent cooldown to WEAK reinforcement.
    if len(selected) < max_items:
        weak_backfill_pool = [
            row for row in normalized_rows
            if row["word"] not in seen_words
            and row.get("status") == "WEAK"
            and not _is_due(row, now)
        ]
        weak_backfill_pool.sort(key=_sort_key_due_first)

        for row in weak_backfill_pool[:WEAK_REINFORCEMENT_QUOTA]:
            try_add(row)

    # Pass 3: unseen NEW items
    if len(selected) < max_items:
        unseen_new_pool = [
            row for row in normalized_rows
            if row["word"] not in seen_words
            and row.get("status") == "NEW"
            and not row.get("last_reviewed_at")
            and not _is_recently_reviewed(row, now)
        ]
        unseen_new_pool.sort(key=_sort_key_new_first)

        for row in unseen_new_pool:
            try_add(row)

    # Pass 4: fallback pool
    # Keep cooldown for non-WEAK items, but allow WEAK items if needed.
    if len(selected) < max_items:
        fallback_pool = [
            row for row in normalized_rows
            if row["word"] not in seen_words
            and (
                row.get("status") == "WEAK"
                or not _is_recently_reviewed(row, now)
            )
        ]
        fallback_pool.sort(key=_sort_key_due_first)

        for row in fallback_pool:
            try_add(row)

    return selected[:max_items]