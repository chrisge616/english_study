from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from ingest.machine_block import extract_machine_block
from ingest.normalizer import normalize_status


def parse_daily_file(file_path: Path) -> dict:
    markdown = file_path.read_text(encoding="utf-8")

    machine = extract_machine_block(markdown)
    if machine:
        machine.setdefault("session_type", "daily")
        machine.setdefault("source_file", str(file_path))
        machine.setdefault("created_at", datetime.utcnow().isoformat(timespec="seconds"))
        return machine

    words = []
    suggested_status = {}
    mistakes = []

    for raw in markdown.splitlines():
        line = raw.strip()
        word_match = re.match(r"^-\s*Word:\s*(.+?)\s*$", line, flags=re.IGNORECASE)
        if word_match:
            words.append({"word": word_match.group(1).strip().lower(), "priority": "medium"})
            continue

        status_match = re.match(r"^-\s*(.+?)\s*(?:→|->|=>|:)\s*(❌|△|○|✅|🧊|NEW|WEAK|STABLE|STRONG|ARCHIVED)\s*$", line, flags=re.IGNORECASE)
        if status_match:
            suggested_status[status_match.group(1).strip().lower()] = normalize_status(status_match.group(2))
            continue

    vocab_set = {item["word"] for item in words}
    lower_markdown = markdown.lower()
    for word in vocab_set:
        if word in lower_markdown and "## ⚠️ mistakes" in lower_markdown:
            # lightweight fallback; replace later with section-bound parsing if needed
            pass

    session_id = f"{file_path.stem}-daily"

    return {
        "session_id": session_id,
        "session_type": "daily",
        "source_file": str(file_path),
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "items": words,
        "suggested_status": suggested_status,
        "mistakes": mistakes,
        "concepts": [],
    }
