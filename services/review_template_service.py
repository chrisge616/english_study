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
        f"| {word} |  |  |  |  |" for word in words
    )

    item_rows = ",\n    ".join(
        f'{{"word": "{word}", "task_type": "", "result": ""}}' for word in words
    )

    return f"""# 📅 {review_date} Review

#tags: #english #review

---

Session Date: {review_date}
Session ID: {review_date}-review-template
Generated From: `output/review_plan.md`

This file records the outcome of a review session.

Please fill the human-editable sections normally.
Keep the machine section at the bottom structurally valid.

---

## HUMAN-EDITABLE SECTION

### 1. Recall Summary

- What was recalled well?
- Which words were remembered only vaguely?
- Which words were missed?

### 2. Usage Summary

- Which words were used correctly in examples?
- Which words showed weak usage control?
- Which words were recognized but not actively usable?

---

### 3. Concept / Nuance Summary

- Which words were conceptually clear?
- Which words were confused with nearby meanings?
- Which nuance gaps appeared during review?

---

### 4. Weak Words

- [word]
- [word]
- [word]

---

### 5. Pattern Mistakes

#### Pattern 1
- Pattern:
- Affected words:
- What went wrong:
- Suggested fix:

#### Pattern 2
- Pattern:
- Affected words:
- What went wrong:
- Suggested fix:

---

### 6. Next Action

- What should be reinforced next?
- Which words need early review?
- Which words may be stable enough to leave alone for now?

---

## STATUS UPDATE TABLE

| Word | Result | Confidence | Notes | Suggested Follow-up |
|------|--------|------------|-------|---------------------|
{status_rows}

Rules:
- `Result` should stay one of: `correct`, `partial`, `wrong`
- Keep notes short and concrete
- Use follow-up only for actionable next steps

---

## MACHINE SECTION - DO NOT EDIT STRUCTURE

You may update result values if needed.
Do not delete keys.
Do not add prose inside the JSON.
Do not change quote style.
Do not convert this block into rich formatting.

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

---

## FINAL CHECK BEFORE INGEST

Confirm the following:

- the human-editable section is complete enough to keep as a review record
- the status table uses valid `Result` values
- the machine block is still valid JSON
- the session id is correct
- the file is saved under `logs/review/`

Example ingest command:

```powershell
study ingest review ".\\logs\\review\\YYYY-MM-DD_review.md"
```
"""


def write_review_result_template_file(text: str, path: Path | None = None) -> Path:
    target = path or REVIEW_RESULT_TEMPLATE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
