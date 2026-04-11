from __future__ import annotations

from datetime import datetime, timedelta

from domain.enums import Status
from domain.models import WordState


STATUS_ORDER = {
    Status.NEW.value: 0,
    Status.WEAK.value: 1,
    Status.STABLE.value: 2,
    Status.STRONG.value: 3,
    Status.ARCHIVED.value: 4,
}


def _later_due(days: int) -> str:
    return (datetime.utcnow() + timedelta(days=days)).isoformat(timespec="seconds")


def _promote_if_higher(current: str, candidate: str) -> str:
    return candidate if STATUS_ORDER[candidate] > STATUS_ORDER[current] else current


def _clamp_non_negative(value: float) -> float:
    return max(0.0, value)


def apply_daily_signal(
    state: WordState,
    *,
    suggested_status: str | None = None,
    mistake_hit: bool = False,
    seen_at: str,
) -> WordState:
    state.last_seen_at = seen_at

    if suggested_status == Status.WEAK.value:
        if state.status == Status.NEW.value:
            state.status = Status.WEAK.value
        state.difficulty_score += 1.0

    elif suggested_status == Status.STABLE.value:
        state.status = _promote_if_higher(state.status, Status.STABLE.value)
        state.memory_strength += 0.4

    elif suggested_status == Status.NEW.value:
        pass

    if mistake_hit:
        if state.status == Status.NEW.value:
            state.status = Status.WEAK.value
        state.difficulty_score += 1.2
        state.due_at = _later_due(1)

    if not state.due_at:
        state.due_at = _later_due(2)

    return state


def apply_review_result(state: WordState, *, result: str, reviewed_at: str) -> WordState:
    state.last_reviewed_at = reviewed_at
    result = result.strip().lower()

    if result == "wrong":
        state.status = Status.WEAK.value
        state.wrong_streak += 1
        state.correct_streak = 0
        state.difficulty_score += 2.0
        state.memory_strength = _clamp_non_negative(state.memory_strength - 0.8)
        state.stability_score = _clamp_non_negative(state.stability_score - 0.2)
        state.due_at = _later_due(1)
        return state

    if result == "partial":
        # Partial = not a failure, but not a pass.
        # Keep the item in circulation, with small progress and modest delay.

        state.wrong_streak = 0
        state.correct_streak = 0

        if state.status in {Status.NEW.value, Status.WEAK.value}:
            state.status = Status.WEAK.value
            state.memory_strength += 0.2
            state.difficulty_score = _clamp_non_negative(state.difficulty_score - 0.4)
            state.stability_score = _clamp_non_negative(state.stability_score)
            state.due_at = _later_due(2)
            return state

        if state.status == Status.STABLE.value:
            state.memory_strength += 0.1
            state.difficulty_score += 0.2
            state.stability_score = _clamp_non_negative(state.stability_score - 0.1)
            state.due_at = _later_due(2)
            return state

        if state.status == Status.STRONG.value:
            state.status = Status.STABLE.value
            state.memory_strength = _clamp_non_negative(state.memory_strength - 0.1)
            state.difficulty_score += 0.2
            state.stability_score = _clamp_non_negative(state.stability_score - 0.2)
            state.due_at = _later_due(2)
            return state

        if state.status == Status.ARCHIVED.value:
            state.status = Status.STABLE.value
            state.memory_strength = _clamp_non_negative(state.memory_strength - 0.2)
            state.difficulty_score += 0.3
            state.stability_score = _clamp_non_negative(state.stability_score - 0.3)
            state.due_at = _later_due(2)
            return state

        return state

    if result == "correct":
        state.correct_streak += 1
        state.wrong_streak = 0
        state.memory_strength += 1.0
        state.stability_score += 0.8
        state.difficulty_score = _clamp_non_negative(state.difficulty_score - 1.0)

        if state.status in {Status.NEW.value, Status.WEAK.value}:
            state.status = Status.STABLE.value
            state.due_at = _later_due(3)
            return state

        if state.status == Status.STABLE.value:
            if state.correct_streak >= 2:
                state.status = Status.STRONG.value
                state.correct_streak = 0
                state.due_at = _later_due(7)
            else:
                state.due_at = _later_due(4)
            return state

        if state.status == Status.STRONG.value:
            if state.correct_streak >= 2:
                state.status = Status.ARCHIVED.value
                state.correct_streak = 0
                state.due_at = _later_due(21)
            else:
                state.due_at = _later_due(10)
            return state

        if state.status == Status.ARCHIVED.value:
            state.due_at = _later_due(30)
            return state

    return state