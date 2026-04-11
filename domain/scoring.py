from __future__ import annotations

from datetime import datetime


STATUS_WEIGHT = {
    "NEW": 4.0,
    "WEAK": 5.0,
    "STABLE": 3.0,
    "STRONG": 1.5,
    "ARCHIVED": 0.5,
}


def safe_parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def compute_priority(row: dict) -> float:
    now = datetime.utcnow()
    status_weight = STATUS_WEIGHT.get(row["status"], 0.0)

    due_at = safe_parse_iso(row.get("due_at"))
    overdue_bonus = 0.0
    if due_at and now > due_at:
        overdue_bonus = min(5.0, (now - due_at).days + 1)

    recent_failure_bonus = float(row.get("wrong_streak", 0)) * 0.8
    memory_penalty = min(2.5, float(row.get("memory_strength", 0.0)) * 0.2)

    return status_weight + overdue_bonus + recent_failure_bonus - memory_penalty
