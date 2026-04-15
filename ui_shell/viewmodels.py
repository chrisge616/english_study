from __future__ import annotations

import json
from html import escape
from pathlib import Path

from application.results import ActionResult


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTION_LABELS = {
    "generate_daily_prompt": "Generate Daily Prompt",
    "generate_review_pack": "Generate Review Prompt",
    "get_current_paths": "Show Current Paths",
    "sync_to_obsidian": "Sync to Obsidian",
    "sync_daily_logs": "Sync Daily Logs from Obsidian",
    "show_recent_daily_logs": "Show Recent Daily Logs",
    "ingest_most_recent_daily_log": "Ingest Latest Daily Log",
    "show_recent_review_logs": "Show Recent Review Files",
    "ingest_most_recent_review_log": "Ingest Most Recent Review Result",
    "ingest_pasted_review_markdown": "Paste and Ingest Review Result",
    "ingest_daily_log": "Ingest Daily Log",
    "ingest_review_log": "Ingest Review Result from Path",
}
REVIEW_ACTIONS = {
    "generate_review_pack",
    "ingest_pasted_review_markdown",
    "show_recent_review_logs",
    "ingest_most_recent_review_log",
    "ingest_review_log",
}


def _action_label(action: str) -> str:
    return ACTION_LABELS.get(action, action.replace("_", " ").strip()) if action else ""


def _snippet(text: str, *, limit: int = 240) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _resolve_repo_path(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else REPO_ROOT / path


def _read_output_file(files: list[str], target_name: str) -> str:
    for raw_path in files:
        path = _resolve_repo_path(str(raw_path))
        if path.name != target_name:
            continue
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""
    return ""


def _is_review_workspace(vm: dict[str, object]) -> bool:
    return bool(
        str(vm.get("review_prompt_text", ""))
        or str(vm.get("review_plan_text", ""))
        or str(vm.get("review_result_template_text", ""))
        or str(vm.get("action", "")) in REVIEW_ACTIONS
    )


def _review_tab_checked(active_kind: str) -> tuple[str, str]:
    if active_kind == "review_paste":
        return "", " checked"
    return " checked", ""


def _active_kind(vm: dict[str, object]) -> str:
    action = str(vm.get("action", ""))
    if action == "generate_daily_prompt" and str(vm.get("daily_prompt_text", "")):
        return "daily_prompt"
    if action == "ingest_pasted_review_markdown":
        return "review_paste"
    if action == "generate_review_pack" and str(vm.get("review_prompt_text", "")):
        return "review_prompt"
    if _is_review_workspace(vm):
        return "review_prompt" if str(vm.get("review_prompt_text", "")) else "review_paste"
    return "latest"


def _status_line(vm: dict[str, object]) -> str:
    action = str(vm.get("action", ""))
    ok = str(vm.get("ok_label", "")) == "success"
    message = str(vm.get("message", "")).strip()
    if action == "generate_daily_prompt":
        return "Daily prompt generated successfully. Copy it, then use it in ChatGPT." if ok else message or "Daily prompt generation failed."
    if action == "generate_review_pack":
        return "Review prompt generated successfully. Copy it, then complete the review on the right." if ok else message or "Review prompt generation failed."
    if action == "ingest_pasted_review_markdown":
        return message or ("Review result ingested successfully." if ok else "Review ingest failed.")
    if action == "ingest_most_recent_daily_log":
        return message or ("Latest daily log ingested successfully." if ok else "Daily ingest failed.")
    return message or "Ready."


def _next_step(vm: dict[str, object]) -> str:
    action = str(vm.get("action", ""))
    if action == "generate_daily_prompt":
        return "Copy the prompt, then use it in ChatGPT."
    if action == "generate_review_pack":
        return "Complete the review on the right, then use Paste and Ingest Review Result on the left."
    if action == "ingest_pasted_review_markdown":
        return "Review the ingest result, then continue with the next study step if needed."
    if action == "ingest_most_recent_daily_log":
        return "Check the result, then continue with the next daily step if needed."
    return "Use the controls on the left to continue the workflow."


def build_result_viewmodel(result: ActionResult | None) -> dict[str, object]:
    if result is None:
        vm: dict[str, object] = {
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
            "review_plan_text": "",
            "review_prompt_text": "",
            "review_result_template_text": "",
        }
        vm["active_kind"] = "latest"
        vm["status_line"] = "Choose Daily or Review on the left to start."
        vm["next_step"] = "Generate a prompt or ingest a result."
        vm["review_workspace"] = False
        return vm

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

    files = [str(item) for item in result.files]
    if not daily_prompt_text:
        daily_prompt_text = _read_output_file(files, "daily_prompt.md")

    review_plan_text = _read_output_file(files, "review_plan.md")
    if not review_prompt_text:
        review_prompt_text = _read_output_file(files, "review_prompt.md")
    review_result_template_text = _read_output_file(files, "review_result_template.md")

    vm = {
        "ok_label": "success" if result.ok else "failure",
        "action": result.action,
        "action_label": _action_label(result.action),
        "message": result.message,
        "files": files,
        "details": details,
        "path_items": path_items,
        "recent_daily_logs": recent_daily_logs,
        "recent_review_logs": recent_review_logs,
        "daily_prompt_text": daily_prompt_text,
        "review_plan_text": review_plan_text,
        "review_prompt_text": review_prompt_text,
        "review_result_template_text": review_result_template_text,
    }
    vm["review_workspace"] = _is_review_workspace(vm)
    vm["active_kind"] = _active_kind(vm)
    vm["status_line"] = _status_line(vm)
    vm["next_step"] = _next_step(vm)
    return vm


def render_result_html(result: ActionResult | None) -> str:
    vm = build_result_viewmodel(result)
    active_kind = str(vm["active_kind"])
    daily_prompt_text = str(vm["daily_prompt_text"])
    review_prompt_text = str(vm["review_prompt_text"])
    review_plan_text = str(vm["review_plan_text"])
    review_result_template_text = str(vm["review_result_template_text"])
    recent_daily_logs = vm["recent_daily_logs"]
    recent_review_logs = vm["recent_review_logs"]
    path_items = vm["path_items"]
    details = str(vm["details"])
    files = vm["files"]
    review_workspace = bool(vm["review_workspace"])

    parts = ['<section class="shell-card work-panel" aria-labelledby="work-panel-title">']
    if review_workspace:
        prompt_checked, paste_checked = _review_tab_checked(active_kind)
        parts.append(f'<input class="review-workspace-tab" type="radio" name="review-workspace-tab" id="review-workspace-prompt"{prompt_checked}>')
        parts.append(f'<input class="review-workspace-tab" type="radio" name="review-workspace-tab" id="review-workspace-paste"{paste_checked}>')

    parts.extend([
        '<header class="work-panel__header">',
        '<div class="work-panel__title-wrap">',
        '<p class="work-panel__eyebrow">Active workspace</p>',
    ])

    if result is None:
        parts.append('<h2 id="work-panel-title">Ready</h2>')
        parts.append(f'<p>{escape(str(vm["status_line"]))}</p>')
        parts.append('</div>')
        parts.append('</header>')
        parts.append('<div class="work-panel__body">')
        parts.append('<article class="output-card output-card--highlight" id="latest-panel">')
        parts.append('<div class="output-card__header"><h3>Latest</h3><p>Generated prompts and review output will appear here.</p></div>')
        parts.append('<p class="preview-snippet">Daily Prompt and Review Workspace use this panel as the active work surface.</p>')
        parts.append('</article>')
        parts.append('</div>')
        parts.append('</section>')
        return "\n".join(parts)

    if active_kind == "daily_prompt":
        parts.append('<h2 id="work-panel-title">Daily Prompt</h2>')
    elif active_kind == "review_paste":
        parts.append('<h2 id="work-panel-title">Paste Final Review Result</h2>')
    elif active_kind == "review_prompt":
        parts.append('<h2 id="work-panel-title">Review Prompt</h2>')
    else:
        parts.append('<h2 id="work-panel-title">Latest</h2>')
    parts.append(f'<p>{escape(str(vm["status_line"]))}</p>')
    parts.append('</div>')

    if active_kind == "daily_prompt" and daily_prompt_text:
        parts.append('<div class="work-toolbar" aria-label="Output actions">')
        parts.append('<div class="work-toolbar__item"><button type="button" class="copy-to-clipboard" data-copy-target="daily-prompt-text" data-copy-success="Copied daily prompt to clipboard.">Copy Daily Prompt</button><a class="work-link" href="#active-output-panel">Show Full Preview</a><span aria-live="polite"></span></div>')
        parts.append('</div>')
    elif review_workspace:
        parts.append('<div class="review-switch" aria-label="Review workspace views">')
        parts.append('<label class="review-switch__link" for="review-workspace-prompt">Review Prompt</label>')
        parts.append('<label class="review-switch__link" for="review-workspace-paste">Paste Final Review Result</label>')
        parts.append('</div>')
        parts.append('<div class="work-toolbar review-toolbar review-toolbar--prompt" aria-label="Review prompt actions">')
        if review_prompt_text:
            parts.append('<div class="work-toolbar__item"><button type="button" class="copy-to-clipboard" data-copy-target="review-prompt-text" data-copy-success="Copied review prompt to clipboard.">Copy Review Prompt</button><a class="work-link" href="#review-prompt-panel">Show Full Preview</a><span aria-live="polite"></span></div>')
        else:
            parts.append('<p>Generate a review prompt on the left to load it here.</p>')
        parts.append('</div>')
        parts.append('<div class="work-toolbar review-toolbar review-toolbar--paste" aria-label="Review paste actions">')
        parts.append('<div class="work-toolbar__item"><a class="work-link" href="#review-paste-panel">Jump to Paste Workspace</a></div>')
        parts.append('<p>Paste the completed review markdown below, then use Paste and Ingest Review Result on the left.</p>')
        parts.append('</div>')

    parts.append('</header>')
    parts.append('<div class="work-panel__body">')

    if active_kind == "daily_prompt" and daily_prompt_text:
        parts.append('<article class="output-card output-card--highlight" id="active-output-panel">')
        parts.append('<div class="output-card__header"><h3>Daily Prompt</h3><p>Snippet first, full prompt below in a bounded preview.</p></div>')
        parts.append(f'<p class="preview-snippet">{escape(_snippet(daily_prompt_text))}</p>')
        parts.append('<div class="output-preview">')
        parts.append(f'<textarea id="daily-prompt-text" class="result-preview" rows="10" readonly>{escape(daily_prompt_text)}</textarea>')
        parts.append('</div>')
        parts.append('</article>')
    elif review_workspace:
        parts.append('<article class="output-card output-card--highlight review-surface review-surface--prompt" id="review-prompt-panel">')
        parts.append('<div class="output-card__header"><h3>Review Prompt</h3><p>Use this as the main review prompt. The paste workspace is the second review surface.</p></div>')
        if review_prompt_text:
            parts.append(f'<p class="preview-snippet">{escape(_snippet(review_prompt_text))}</p>')
            parts.append('<div class="output-preview">')
            parts.append(f'<textarea id="review-prompt-text" class="result-preview" rows="10" readonly>{escape(review_prompt_text)}</textarea>')
            parts.append('</div>')
        else:
            parts.append('<p class="preview-snippet">Generate Review Prompt on the left to load it here.</p>')
        parts.append('</article>')

        parts.append('<article class="output-card output-card--highlight review-surface review-surface--paste" id="review-paste-panel">')
        parts.append('<div class="output-card__header"><h3>Paste Final Review Result</h3><p>This is the large paste workspace for the completed markdown from ChatGPT.</p></div>')
        parts.append('<p class="preview-snippet">Paste the completed review result here, then use Paste and Ingest Review Result on the left.</p>')
        parts.append('<div class="output-preview">')
        parts.append('<textarea id="workspace-review-markdown" class="result-preview workspace-paste-input" name="review_markdown" form="review-ingest-form" rows="16" placeholder="# 2026-04-14 Review"></textarea>')
        parts.append('</div>')
        parts.append('</article>')
    else:
        parts.append('<article class="output-card output-card--highlight" id="active-output-panel">')
        parts.append('<div class="output-card__header"><h3>Latest</h3><p>Plain-language status for the most recent action.</p></div>')
        parts.append(f'<p><strong>Status:</strong> {escape(str(vm["ok_label"]))}</p>')
        parts.append(f'<p><strong>Action:</strong> {escape(str(vm["action_label"])) or "none"}</p>')
        parts.append(f'<p><strong>Next step:</strong> {escape(str(vm["next_step"]))}</p>')
        parts.append('</article>')

    has_more = bool(review_plan_text or review_result_template_text or files or recent_daily_logs or recent_review_logs or path_items or details)
    if has_more:
        parts.append('<details class="work-more">')
        parts.append('<summary>More</summary>')

        if review_plan_text:
            parts.append('<article class="output-card">')
            parts.append('<div class="output-card__header"><h3>Review Plan</h3><p>Secondary support for the review prompt.</p></div>')
            parts.append(f'<p class="preview-snippet">{escape(_snippet(review_plan_text))}</p>')
            parts.append(f'<textarea id="review-plan-text" class="result-preview" rows="8" readonly>{escape(review_plan_text)}</textarea>')
            parts.append('</article>')

        if review_result_template_text:
            parts.append('<article class="output-card">')
            parts.append('<div class="output-card__header"><h3>Result Template</h3><p>Fallback/manual recovery tool.</p></div>')
            parts.append(f'<p class="preview-snippet">{escape(_snippet(review_result_template_text))}</p>')
            parts.append(f'<textarea id="result-template-text" class="result-preview" rows="8" readonly>{escape(review_result_template_text)}</textarea>')
            parts.append('</article>')

        if files:
            parts.append('<article class="output-card">')
            parts.append('<div class="output-card__header"><h3>Generated Files</h3><p>Available here without adding default clutter.</p></div>')
            parts.append('<ul class="output-list">')
            for file_path in files:
                parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
            parts.append('</ul>')
            parts.append('</article>')

        if recent_daily_logs or recent_review_logs:
            parts.append('<article class="output-card">')
            parts.append('<div class="output-card__header"><h3>Recent Files</h3><p>Secondary file history.</p></div>')
            if recent_daily_logs:
                parts.append('<p><strong>Daily</strong></p>')
                parts.append('<ul class="output-list">')
                for file_path in recent_daily_logs:
                    parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
                parts.append('</ul>')
            if recent_review_logs:
                parts.append('<p><strong>Review</strong></p>')
                parts.append('<ul class="output-list">')
                for file_path in recent_review_logs:
                    parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
                parts.append('</ul>')
            parts.append('</article>')

        if path_items or details:
            parts.append('<article class="output-card">')
            parts.append('<div class="output-card__header"><h3>Technical Details</h3><p>Hidden by default to keep the main UI clean.</p></div>')
            if path_items:
                parts.append('<ul class="path-list">')
                for item in path_items:
                    parts.append(f"<li><strong>{escape(item['label'])}:</strong> <code>{escape(item['value'])}</code></li>")
                parts.append('</ul>')
            if details:
                parts.append(f'<pre class="result-pre">{escape(details)}</pre>')
            parts.append('</article>')

        parts.append('</details>')

    parts.append('</div>')
    parts.append('</section>')
    return "\n".join(parts)
