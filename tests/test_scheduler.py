from datetime import datetime, timedelta, timezone

from domain.scheduler import select_review_items


def test_scheduler_backfills_non_due_weak_items():
    future_due = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    rows = [
        {"display_text": "a", "status": "STABLE", "due_at": None},
        {"display_text": "b", "status": "WEAK", "due_at": future_due},
    ]

    selected = select_review_items(rows)

    assert selected[0]["display_text"] == "a"
    assert any(item["display_text"] == "b" for item in selected)
