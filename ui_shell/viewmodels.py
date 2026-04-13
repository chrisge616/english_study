from __future__ import annotations

import json
from html import escape

from application.results import ActionResult


def build_result_viewmodel(result: ActionResult | None) -> dict[str, str | list[str]]:
    if result is None:
        return {
            "ok_label": "",
            "action": "",
            "message": "",
            "files": [],
            "details": "",
            "path_items": [],
            "recent_daily_logs": [],
            "daily_prompt_text": "",
            "review_prompt_text": "",
        }

    details = ""
    if result.details is not None:
        details = json.dumps(result.details, ensure_ascii=False, indent=2, sort_keys=True)

    path_items: list[dict[str, str]] = []
    if result.action == "get_current_paths" and isinstance(result.details, dict):
        path_items = [
            {"label": "Engine Workspace", "value": str(result.details.get("canonical_engine_repo", ""))},
            {"label": "Notes Workspace", "value": str(result.details.get("notes_workspace", ""))},
            {"label": "Database", "value": str(result.details.get("database_path", ""))},
        ]

    recent_daily_logs: list[str] = []
    daily_prompt_text = ""
    review_prompt_text = ""
    if isinstance(result.details, dict):
        raw_recent_daily_logs = result.details.get("recent_daily_logs", [])
        if isinstance(raw_recent_daily_logs, list):
            recent_daily_logs = [str(item) for item in raw_recent_daily_logs]
        raw_daily_prompt_text = result.details.get("prompt_text", "")
        if isinstance(raw_daily_prompt_text, str):
            daily_prompt_text = raw_daily_prompt_text
        raw_review_prompt_text = result.details.get("review_prompt_text", "")
        if isinstance(raw_review_prompt_text, str):
            review_prompt_text = raw_review_prompt_text

    return {
        "ok_label": "success" if result.ok else "failure",
        "action": result.action,
        "message": result.message,
        "files": result.files,
        "details": details,
        "path_items": path_items,
        "recent_daily_logs": recent_daily_logs,
        "daily_prompt_text": daily_prompt_text,
        "review_prompt_text": review_prompt_text,
    }


def render_result_html(result: ActionResult | None) -> str:
    vm = build_result_viewmodel(result)
    parts = [
        "<section>",
        "<h2>Last Result</h2>",
        f"<p><strong>Status:</strong> {escape(str(vm['ok_label'])) or 'none'}</p>",
        f"<p><strong>Action:</strong> {escape(str(vm['action'])) or 'none'}</p>",
        f"<p><strong>Message:</strong> {escape(str(vm['message'])) or 'none'}</p>",
    ]

    path_items = vm["path_items"]
    if path_items:
        parts.append("<p><strong>Paths:</strong></p>")
        parts.append("<ul>")
        for item in path_items:
            parts.append(
                f"<li><strong>{escape(item['label'])}:</strong> <code>{escape(item['value'])}</code></li>"
            )
        parts.append("</ul>")

    files = vm["files"]
    if files:
        parts.append("<p><strong>Files:</strong></p>")
        parts.append("<ul>")
        for file_path in files:
            parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
        parts.append("</ul>")

    recent_daily_logs = vm["recent_daily_logs"]
    if recent_daily_logs:
        parts.append("<p><strong>Recent Daily Logs:</strong></p>")
        parts.append("<ul>")
        for file_path in recent_daily_logs:
            parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
        parts.append("</ul>")

    daily_prompt_text = str(vm["daily_prompt_text"])
    if daily_prompt_text:
        parts.append("<p><strong>Daily Prompt:</strong></p>")
        parts.append('<textarea id="daily-prompt-text" rows="16" readonly>{}</textarea>'.format(escape(daily_prompt_text)))
        parts.append('<p><button type="button" class="copy-to-clipboard" data-copy-target="daily-prompt-text" data-copy-success="Copied daily prompt to clipboard.">Copy to Clipboard</button> <span id="copy-status" aria-live="polite"></span></p>')

    review_prompt_text = str(vm["review_prompt_text"])
    if review_prompt_text:
        parts.append("<p><strong>Review Prompt:</strong></p>")
        parts.append('<textarea id="review-prompt-text" rows="16" readonly>{}</textarea>'.format(escape(review_prompt_text)))
        parts.append('<p><button type="button" class="copy-to-clipboard" data-copy-target="review-prompt-text" data-copy-success="Copied review prompt to clipboard.">Copy to Clipboard</button> <span id="copy-status" aria-live="polite"></span></p>')

    details = str(vm["details"])
    if details:
        parts.append("<p><strong>Details:</strong></p>")
        parts.append(f"<pre>{escape(details)}</pre>")

    parts.append("</section>")
    return "\n".join(parts)
