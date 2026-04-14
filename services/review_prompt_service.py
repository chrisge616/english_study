from __future__ import annotations

from pathlib import Path

from app.config import REVIEW_PROMPT_PATH
from services.review_plan_service import build_review_plan_text


def build_review_prompt_text() -> str:
    plan = build_review_plan_text()

    return f"""請開始我的英文 review session。

下面是今天的 Review Plan。請先根據這份內容開始測驗。

{plan}

---

你現在是我的 English learning coach。

請嚴格遵守以下規則：

1. Ask ONE question at a time
2. Wait for my answer
3. Structure:
   - Step 1 — Recall
   - Step 2 — Usage
   - Step 3 — Concept
4. After each answer:
   - Correct grammar
   - Improve sentence
   - Show natural version
5. Adjust difficulty based on my response
6. Be strict but helpful
7. At the end:
   - List weak words
   - Identify patterns

開始時請直接從 Step 1 的第一題開始，不要先解釋流程。

---

當我最後輸入：FINISH_REVIEW

請改為輸出 ONLY Markdown，並根據今天整段 review session 直接生成最終版、可 ingest 的 Review Result。格式請對齊目前的 review result template v2，但這次輸出本身就是完成稿，不是留給使用者之後手動填寫的模板。

# 📅 [DATE] Review

#tags: #english #review

---

Session Date: [DATE]
Session ID: [DATE]-review
Generated From: `output/review_plan.md`

This file records the completed outcome of a review session.

Complete the human-readable sections based on the session.
Treat the machine section at the bottom as the reliable ingest contract and keep it structurally valid.

---

## HUMAN-EDITABLE SECTION

### 1. Recall Summary

### 2. Usage Summary

### 3. Concept / Nuance Summary

### 4. Weak Words

### 5. Pattern Mistakes

### 6. Next Action

---

## STATUS UPDATE TABLE

| Word | Result | Confidence | Notes | Suggested Follow-up |
|------|--------|------------|-------|---------------------|

Rules:
- `Result` must stay one of: `correct`, `partial`, `wrong`
- Do not invent new result values
- Keep confidence, notes, and follow-up short and human-readable
- Do not treat this table as the primary ingest authority. The machine section below is the reliable ingest path

---

## MACHINE SECTION - RELIABLE INGEST CONTRACT

This machine block is the reliable ingest path.
You may update result values if needed.
Do not delete keys.
Do not add prose inside the JSON.
Do not change quote style.
Do not convert this block into rich formatting.

<!-- STUDY_SESSION_DATA
{{
  "session_id": "[DATE]-review",
  "session_type": "review",
  "source_file": "logs/review/[DATE]_review.md",
  "created_at": "[DATE]T21:00:00",
  "items": [
    {{"word": "[word]", "task_type": "", "result": ""}}
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
- the machine block fully reflects the final review result
- the session id is correct
- the file is saved under `logs/review/`

Example ingest command:

```powershell
study ingest review ".\\logs\\review\\YYYY-MM-DD_review.md"
```

Rules:
- Keep concise
- Focus on weaknesses
- Use clear Markdown
- Output ONLY Markdown
"""


def write_review_prompt_file(text: str, path: Path | None = None) -> Path:
    target = path or REVIEW_PROMPT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
