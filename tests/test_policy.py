from domain.models import WordState
from domain.policy import apply_review_result


def test_new_correct_becomes_stable():
    state = WordState(word_id=1, status="NEW")
    state = apply_review_result(state, result="correct", reviewed_at="2026-04-10T00:00:00")
    assert state.status == "STABLE"
