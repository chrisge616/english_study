from pathlib import Path

from domain.enums import EvidenceType
from domain.policy import apply_daily_signal, apply_review_result
from ingest.daily_parser import parse_daily_file
from ingest.review_parser import parse_review_file
from storage.evidence_repo import add_evidence, add_session_item
from storage.session_repo import create_session, session_exists
from storage.state_repo import create_default_state, get_state, save_state
from storage.word_repo import upsert_word


def _ensure_word_and_state(word: str, created_at: str) -> tuple[int, object]:
    word_id = upsert_word(word, word, "word", created_at)
    state = get_state(word_id)
    if state is None:
        state = create_default_state(word_id)
    return word_id, state


def ingest_daily_file(file_path: Path) -> dict:
    payload = parse_daily_file(file_path)

    if session_exists(payload["session_id"]):
        return {
            "session_id": payload["session_id"],
            "processed": 0,
            "skipped": True,
            "reason": "session already exists",
        }

    create_session(
        payload["session_id"],
        payload["session_type"],
        payload["source_file"],
        payload["created_at"],
        payload,
    )

    processed = 0
    for item in payload.get("items", []):
        word = item["word"].lower().strip()
        word_id, state = _ensure_word_and_state(word, payload["created_at"])

        add_evidence(
            word_id,
            payload["session_id"],
            EvidenceType.INTRODUCED.value,
            1.0,
            "daily_log",
            item,
            payload["created_at"],
        )

        suggested = payload.get("suggested_status", {}).get(word)
        if suggested == "WEAK":
            add_evidence(
                word_id,
                payload["session_id"],
                EvidenceType.MARKED_DIFFICULT.value,
                1.0,
                "daily_log",
                {"suggested_status": suggested},
                payload["created_at"],
            )
        elif suggested == "STABLE":
            add_evidence(
                word_id,
                payload["session_id"],
                EvidenceType.MARKED_FAMILIAR.value,
                1.0,
                "daily_log",
                {"suggested_status": suggested},
                payload["created_at"],
            )

        state = apply_daily_signal(
            state,
            suggested_status=suggested,
            mistake_hit=False,
            seen_at=payload["created_at"],
        )
        save_state(state)
        add_session_item(payload["session_id"], word_id, "daily", None)
        processed += 1

    return {"session_id": payload["session_id"], "processed": processed, "skipped": False}


def ingest_review_file(file_path: Path) -> dict:
    payload = parse_review_file(file_path)

    if session_exists(payload["session_id"]):
        return {
            "session_id": payload["session_id"],
            "processed": 0,
            "skipped": True,
            "reason": "session already exists",
        }

    create_session(
        payload["session_id"],
        payload["session_type"],
        payload["source_file"],
        payload["created_at"],
        payload,
    )

    processed = 0
    for item in payload.get("items", []):
        word = item["word"].lower().strip()
        result = item["result"].lower().strip()
        word_id, state = _ensure_word_and_state(word, payload["created_at"])

        evidence_map = {
            "correct": EvidenceType.REVIEW_CORRECT.value,
            "partial": EvidenceType.REVIEW_PARTIAL.value,
            "wrong": EvidenceType.REVIEW_WRONG.value,
        }
        add_evidence(
            word_id,
            payload["session_id"],
            evidence_map.get(result, EvidenceType.REVIEW_PARTIAL.value),
            1.0,
            "review_log",
            item,
            payload["created_at"],
        )
        state = apply_review_result(state, result=result, reviewed_at=payload["created_at"])
        save_state(state)
        add_session_item(payload["session_id"], word_id, item.get("task_type"), result)
        processed += 1

    return {"session_id": payload["session_id"], "processed": processed, "skipped": False}
