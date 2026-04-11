from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.config import REVIEW_PLAN_PATH
from domain.scheduler import select_review_items
from storage.state_repo import list_state_rows


def build_review_plan_text() -> str:
    rows = list_state_rows()
    selected = select_review_items(rows)
    today = datetime.utcnow().date().isoformat()

    recall = selected[:4]
    usage = selected[4:8]
    concept = selected[8:12]

    lines = [
        f"# Review Plan ({today})",
        "",
        "## Focus",
        "- Due-based review",
        "- Prioritize weak and overdue items",
        "- Keep total size controlled",
        "",
        "## Test Set",
        "",
        "### Recall",
    ]
    for row in recall:
        lines.append(f"- Define: **{row['display_text']}**")

    lines.extend(["", "### Usage"])
    for row in usage:
        lines.append(f"- Make a sentence with: **{row['display_text']}**")

    lines.extend(["", "### Concept"])
    for row in concept:
        lines.append(f"- Explain nuance / difference / deeper use of: **{row['display_text']}**")

    lines.extend(["", "## Selected Words"])
    for row in selected:
        lines.append(f"- {row['display_text']} ({row['status']})")

    return "\n".join(lines)


def write_review_plan_file(text: str, path: Path | None = None) -> Path:
    target = path or REVIEW_PLAN_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
