from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.config import DAILY_PROMPT_PATH


def build_daily_prompt_text() -> str:
    today = datetime.utcnow().date().isoformat()
    return f"""請根據今天的英文學習內容，生成一份清楚、結構一致、方便後續整理的 Daily Learning Log。\n\n請輸出 Markdown。整體風格以 human-readable 為主，但文末 machine block 必須保留，且在完成日誌內容後同步填好。\n\n## Generation Rules\n\n- 保持 section 順序與標題結構清楚。\n- Vocabulary 請依 High / Medium / Low Priority 分組；如果某組沒有內容，也保留標題。\n- Vocabulary entry 請盡量使用一致格式，不要有的條目很簡略、有的條目很冗長。\n- 若有錯誤句子，優先寫 learner 的實際錯誤，再給自然修正。\n- 若沒有某 section 的內容，可保留標題並寫 1 行簡短說明，避免整段省略。\n\n## Required Vocabulary Entry Format\n\n每個單字或片語都請使用這個格式：\n- Word: <word or phrase>\n  - Meaning (simple English): <short, simple definition>\n  - Example: <natural example sentence>\n  - Suggested Status: <❌ or △ or ○>\n\n可選補充欄位只有在真的有幫助時再加，例如：\n- Part of speech:\n- Chinese note:\n- Confusion note:\n- Source context:\n\n狀態定義：\n- ❌ = New\n- △ = Difficult / weak\n- ○ = Familiar / mostly understood\n\n## Required Output\n\n# 📅 [{today}] Learning Log\n\n#tags: #english #dailylog\n\n---\n\n## 🔑 Vocabulary\n\n### High Priority\n### Medium Priority\n### Low Priority\n\n---\n\n## ⚠️ Mistakes & Corrections\n\n建議格式：\n❌ <learner sentence / misunderstanding>\n✅ <better sentence / correction / explanation>\n\n---\n\n## 🧠 Key Concepts\n\n用簡短條列整理今天最重要的 distinction、usage boundary、concept pair 或 nuance。\n\n---\n\n## 🧪 Test Bank\n\n### Recall\n### Usage\n### Concept\n\n每個小節放幾題簡短、可直接複習的題目。\n\n---\n\n## 🔁 Suggested Review Timing\n\n- D1\n- D3\n- D7\n- D14\n\n---\n\n## 🎯 Notes (Optional)\n\n用 1 到 3 點簡短說明今天的收穫、主要困難或下次重點。\n\n---\n\n## 🏷 Suggested Status Summary\n\n在這一節再次用每行一個的格式列出所有詞條，格式固定為：\n- <word> -> <❌ / △ / ○>\n\n## Machine Block Rules\n\n- 保留最下方 `<!-- STUDY_SESSION_DATA ... -->` block。\n- 下方空白 JSON 是 starter scaffold；請在完成上方內容後再補齊，不要直接保留空白值去 ingest。\n- JSON 必須有效，不要使用 smart quotes。\n- machine block 完成後要反映上面的 vocabulary 與 mistakes。\n- 如果有 vocabulary，`items` 內也要有對應項目。\n- 如果有 status summary，`suggested_status` 內也要填入對應內容。\n- 如果有 mistakes，`mistakes` 內也要填入對應內容。\n\n<!-- STUDY_SESSION_DATA\n{{\n  \"session_type\": \"daily\",\n  \"date\": \"{today}\",\n  \"items\": [],\n  \"suggested_status\": {{}},\n  \"mistakes\": []\n}}\n-->"""


def write_daily_prompt_file(text: str, path: Path | None = None) -> Path:
    target = path or DAILY_PROMPT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target
