from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ingest.machine_block import extract_machine_block


def parse_review_file(file_path: Path) -> dict:
    markdown = file_path.read_text(encoding="utf-8")

    machine = extract_machine_block(markdown)
    if machine:
        machine.setdefault("session_type", "review")
        machine.setdefault("source_file", str(file_path))
        machine.setdefault("created_at", datetime.utcnow().isoformat(timespec="seconds"))
        return machine

    items = []
    in_table = False
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("| Word") and "Result" in line:
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if "---" in line:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) != 4:
                continue
            word, result, _new_status, _streak = parts
            items.append({
                "word": word.lower(),
                "task_type": "review",
                "result": result.lower(),
            })

    return {
        "session_id": f"{file_path.stem}-review",
        "session_type": "review",
        "source_file": str(file_path),
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "items": items,
        "pattern_notes": [],
    }
