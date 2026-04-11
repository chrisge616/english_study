from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from app.config import REVIEW_RESULT_TEMPLATE_PATH
from services.review_plan_service import build_review_plan_text


def _extract_review_date(plan_text: str) -> str:
    match = re.search(r"# Review Plan \((\d{4}-\d{2}-\d{2})\)", plan_text)
    if match:
        return match.group(1)
    return datetime.now(timezone.utc).date().isoformat()


def _extract_selected_words(plan_text: str) -> list[str]:
    lines = plan_text.splitlines()
    words: list[str] = []
    in_selected = False

    for line in lines:
        stripped = line.strip()

        if stripped == "## Selected Words":
            in_selected = True
            continue

        if in_selected:
            if stripped.startswith("## ") and stripped != "## Selected Words":
                break
            if stripped.startswith("- "):
                item = stripped[2:].strip()
                word = re.sub(r"\s*\([^)]*\)\s*$", "", item).strip()
                if word:
                    words.append(word)

    return words


def build_review_result_template_text() -> str:
    plan_text = build_review_plan_text()
    review_date = _extract_review_date(plan_text)
    words = _extract_selected_words(plan_text)

    status_rows = "\n".join(
        f"| {word} |  |  |  |" for word in words
    )

    item_rows = ",\n    ".join(
        f'{{"word": "{word}", "task_type": "", "result": ""}}' for word in words
    )

    return f"""# 📅 {review_date} Review

#tags: #english #review

---

## 🔥 Today Focus

- Fill in results after your review session
- Use: correct / partial / wrong
- Keep notes brief and concrete

---

## 🧪 Test Summary

### Recall

### Usage

### Concept

---

## ❗ Weak Words

- mark with WEAK or STABLE when appropriate

---

## 📊 Recall Status

|Word|Status|
|---|---|
{"".join(f"| {word} |  |\n" for word in words[:4])}

---

## 🧠 Pattern Mistakes

---

## 🎯 Next Action

---

## 📊 Status Update

| Word | Result | New Status | Streak |
|------|--------|------------|--------|
{status_rows}

<!-- STUDY_SESSION_DATA
{{
  "session_id": "{review_date}-review-template",
  "session_type": "review",
  "source_file": "logs/review/{review_date}_review.md",
  "created_at": "{review_date}T21:00:00",
  "items": [
    {item_rows}
  ],
  "pattern_notes": []
}}
-->
"""


def write_review_result_template_file(text: str, path: Path | None = None) -> Path:
    target = path or REVIEW_RESULT_TEMPLATE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
