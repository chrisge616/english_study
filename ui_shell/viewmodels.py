from __future__ import annotations

import json
from html import escape

from application.results import ActionResult


ACTION_LABELS = {
    "generate_daily_prompt": "Generate Daily Prompt",
    "generate_review_pack": "Generate Review Materials",
    "get_current_paths": "Show Current Paths",
    "sync_to_obsidian": "Sync to Obsidian",
    "sync_daily_logs": "Sync Daily Logs from Obsidian",
    "show_recent_daily_logs": "Show Recent Daily Logs",
    "ingest_most_recent_daily_log": "Ingest Most Recent Daily Log",
    "show_recent_review_logs": "Show Recent Review Files",
    "ingest_most_recent_review_log": "Ingest Most Recent Review Result",
    "ingest_pasted_review_markdown": "Paste and Ingest Review Result",
    "ingest_daily_log": "Ingest Daily Log",
    "ingest_review_log": "Ingest Review Result",
}


def _action_label(action: str) -> str:
    return ACTION_LABELS.get(action, action.replace("_", " ").strip()) if action else ""


def build_result_viewmodel(result: ActionResult | None) -> dict[str, str | list[str]]:
    if result is None:
        return {
            "ok_label": "",
            "action": "",
            "action_label": "",
            "message": "",
            "files": [],
            "details": "",
            "path_items": [],
            "recent_daily_logs": [],
            "recent_review_logs": [],
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
    recent_review_logs: list[str] = []
    daily_prompt_text = ""
    review_prompt_text = ""
    if isinstance(result.details, dict):
        raw_recent_daily_logs = result.details.get("recent_daily_logs", [])
        if isinstance(raw_recent_daily_logs, list):
            recent_daily_logs = [str(item) for item in raw_recent_daily_logs]
        raw_recent_review_logs = result.details.get("recent_review_logs", [])
        if isinstance(raw_recent_review_logs, list):
            recent_review_logs = [str(item) for item in raw_recent_review_logs]
        raw_daily_prompt_text = result.details.get("prompt_text", "")
        if isinstance(raw_daily_prompt_text, str):
            daily_prompt_text = raw_daily_prompt_text
        raw_review_prompt_text = result.details.get("review_prompt_text", "")
        if isinstance(raw_review_prompt_text, str):
            review_prompt_text = raw_review_prompt_text

    return {
        "ok_label": "success" if result.ok else "failure",
        "action": result.action,
        "action_label": _action_label(result.action),
        "message": result.message,
        "files": result.files,
        "details": details,
        "path_items": path_items,
        "recent_daily_logs": recent_daily_logs,
        "recent_review_logs": recent_review_logs,
        "daily_prompt_text": daily_prompt_text,
        "review_prompt_text": review_prompt_text,
    }



def render_result_html(result: ActionResult | None) -> str:
    vm = build_result_viewmodel(result)
    parts = [
        '<section aria-labelledby="result-feedback">',
        '<h2 id="result-feedback">Result / Feedback</h2>',
    ]

    if result is None:
        parts.append('<p>No action yet. Generate a prompt or ingest a log to see the latest result here.</p>')
        parts.append('</section>')
        return "\n".join(parts)

    parts.extend([
        '<section aria-labelledby="result-summary">',
        '<h3 id="result-summary">What just happened</h3>',
        f"<p><strong>Status:</strong> {escape(str(vm['ok_label']))}</p>",
        f"<p><strong>Action:</strong> {escape(str(vm['action_label'])) or 'none'}</p>",
        f"<p><strong>Message:</strong> {escape(str(vm['message'])) or 'none'}</p>",
        '</section>',
    ])

    files = vm['files']
    recent_daily_logs = vm['recent_daily_logs']
    recent_review_logs = vm['recent_review_logs']
    daily_prompt_text = str(vm['daily_prompt_text'])
    review_prompt_text = str(vm['review_prompt_text'])

    if files or recent_daily_logs or recent_review_logs or daily_prompt_text or review_prompt_text:
        parts.append('<section aria-labelledby="result-next">')
        parts.append('<h3 id="result-next">Use this next</h3>')

        if files:
            parts.append('<p><strong>Files:</strong></p>')
            parts.append('<ul>')
            for file_path in files:
                parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
            parts.append('</ul>')

        if recent_daily_logs:
            parts.append('<p><strong>Recent Daily Logs:</strong></p>')
            parts.append('<ul>')
            for file_path in recent_daily_logs:
                parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
            parts.append('</ul>')

        if recent_review_logs:
            parts.append('<p><strong>Recent Review Files:</strong></p>')
            parts.append('<ul>')
            for file_path in recent_review_logs:
                parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
            parts.append('</ul>')

        if daily_prompt_text:
            parts.append('<p><strong>Daily Prompt:</strong></p>')
            parts.append('<textarea id="daily-prompt-text" rows="16" readonly>{}</textarea>'.format(escape(daily_prompt_text)))
            parts.append('<p><button type="button" class="copy-to-clipboard" data-copy-target="daily-prompt-text" data-copy-success="Copied daily prompt to clipboard.">Copy Daily Prompt</button> <span aria-live="polite"></span></p>')

        if review_prompt_text:
            parts.append('<p><strong>Review Prompt:</strong></p>')
            parts.append('<textarea id="review-prompt-text" rows="16" readonly>{}</textarea>'.format(escape(review_prompt_text)))
            parts.append('<p><button type="button" class="copy-to-clipboard" data-copy-target="review-prompt-text" data-copy-success="Copied review prompt to clipboard.">Copy Review Prompt</button> <span aria-live="polite"></span></p>')

        parts.append('</section>')

    path_items = vm['path_items']
    details = str(vm['details'])
    if path_items or details:
        parts.append('<section aria-labelledby="result-technical">')
        parts.append('<h3 id="result-technical">Technical details</h3>')

        if path_items:
            parts.append('<p><strong>Paths:</strong></p>')
            parts.append('<ul>')
            for item in path_items:
                parts.append(
                    f"<li><strong>{escape(item['label'])}:</strong> <code>{escape(item['value'])}</code></li>"
                )
            parts.append('</ul>')

        if details:
            parts.append('<p><strong>Details:</strong></p>')
            parts.append(f"<pre>{escape(details)}</pre>")

        parts.append('</section>')

    parts.append('</section>')
    return "\n".join(parts)
