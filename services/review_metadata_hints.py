from __future__ import annotations

import json
import re
from pathlib import Path

from app.config import ROOT


REVIEW_METADATA_RE = re.compile(
    r"<!--\s*STUDY_REVIEW_METADATA\s*(\{.*?\})\s*-->",
    flags=re.DOTALL,
)


def _extract_selected_words(plan_text: str) -> list[str]:
    words: list[str] = []
    in_selected = False

    for raw in plan_text.splitlines():
        line = raw.strip()
        if line == "## Selected Words":
            in_selected = True
            continue
        if in_selected and line.startswith("## "):
            break
        if in_selected and line.startswith("- "):
            item = line[2:].strip()
            word = re.sub(r"\s*\([^)]*\)\s*$", "", item).strip().lower()
            if word:
                words.append(word)

    return words


def _load_latest_review_metadata(review_logs_dir: Path) -> dict | None:
    for path in sorted(review_logs_dir.glob("*_review.md"), reverse=True):
        markdown = path.read_text(encoding="utf-8")
        match = REVIEW_METADATA_RE.search(markdown)
        if not match:
            continue
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
    return None


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [_normalize_text(item) for item in value if _normalize_text(item)]
    text = _normalize_text(value)
    return [text] if text else []


def build_review_metadata_hints(
    plan_text: str,
    *,
    review_logs_dir: Path | None = None,
    max_hints: int = 4,
) -> str:
    selected_words = _extract_selected_words(plan_text)
    if not selected_words:
        return ""

    metadata = _load_latest_review_metadata(review_logs_dir or (ROOT / "logs" / "review"))
    if not metadata:
        return ""

    selected_set = set(selected_words)
    item_map: dict[str, dict] = {}
    for item in metadata.get("items", []):
        if not isinstance(item, dict):
            continue
        word = _normalize_text(item.get("word")).lower()
        if word and word in selected_set:
            item_map[word] = item

    hints: list[str] = []
    seen: set[str] = set()

    for word in selected_words:
        item = item_map.get(word)
        if not item:
            continue

        confusion_with = _as_list(item.get("confusion_with"))
        if confusion_with and len(hints) < max_hints:
            pair = " vs ".join([word, confusion_with[0]])
            hint = f"- Re-test the boundary for **{pair}**."
            if hint not in seen:
                hints.append(hint)
                seen.add(hint)

        support_needed = _normalize_text(item.get("support_needed"))
        best_support_mode = _normalize_text(item.get("best_support_mode"))
        if support_needed and best_support_mode and len(hints) < max_hints:
            hint = (
                f"- If **{word}** stalls, start with **{best_support_mode}** support "
                f"because **{support_needed}** helped last time."
            )
            if hint not in seen:
                hints.append(hint)
                seen.add(hint)
        elif best_support_mode and len(hints) < max_hints:
            hint = f"- For **{word}**, try **{best_support_mode}** support first if recall is weak."
            if hint not in seen:
                hints.append(hint)
                seen.add(hint)

        if len(hints) >= max_hints:
            break

    if len(hints) < max_hints:
        for word in selected_words:
            item = item_map.get(word)
            if not item:
                continue
            vocab_vs_fluency = _normalize_text(item.get("vocab_vs_fluency")).lower()
            if not vocab_vs_fluency:
                continue
            hint = (
                "- Keep awkward delivery separate from vocabulary failure when the learner "
                "shows the right meaning."
            )
            if hint not in seen:
                hints.append(hint)
                seen.add(hint)
            break

    if not hints:
        return ""

    return "\n".join(
        [
            "",
            "## Coach Hints From Recent Review Metadata",
            "- Use these as short advisory hints only.",
            "- Keep vocabulary mastery primary.",
            *hints[:max_hints],
            "",
        ]
    )
