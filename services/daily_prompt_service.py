from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.config import DAILY_PROMPT_PATH


def build_daily_prompt_text() -> str:
    today = datetime.utcnow().date().isoformat()
    return f"""請根據今天的英文學習內容，生成一份結構化的 Daily Learning Log。\n\n請輸出 Markdown，並在文末保留 machine block。\n\n# 📅 [{today}] Learning Log\n\n#tags: #english #dailylog\n\n---\n\n## 🔑 Vocabulary\n\n### High Priority\n### Medium Priority\n### Low Priority\n\nFor each word:\n- Word:\n- Meaning (simple English):\n- Example:\n\n---\n\n## ⚠️ Mistakes & Corrections\n\n---\n\n## 🧠 Key Concepts\n\n---\n\n## 🧪 Test Bank\n\n### Recall\n### Usage\n### Concept\n\n---\n\n## 🔁 Suggested Review Timing\n\n- D1\n- D3\n- D7\n- D14\n\n---\n\n## 🎯 Notes (Optional)\n\n---\n\n## 🏷 Suggested Status\n\nMark each word:\n- ❌ New\n- △ Difficult\n- ○ Familiar\n\n<!-- STUDY_SESSION_DATA\n{{\n  \"session_type\": \"daily\",\n  \"date\": \"{today}\",\n  \"words\": [],\n  \"mistakes\": []\n}}\n-->"""


def write_daily_prompt_file(text: str, path: Path | None = None) -> Path:
    target = path or DAILY_PROMPT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
