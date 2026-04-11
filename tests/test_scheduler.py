from domain.scheduler import select_review_items


def test_scheduler_prefers_weak():
    rows = [
        {"display_text": "a", "status": "STABLE", "wrong_streak": 0, "memory_strength": 2.0, "due_at": None},
        {"display_text": "b", "status": "WEAK", "wrong_streak": 1, "memory_strength": 0.0, "due_at": None},
    ]
    selected = select_review_items(rows)
    assert selected[0]["display_text"] == "b"
