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
        }

    details = ""
    if result.details is not None:
        details = json.dumps(result.details, ensure_ascii=False, indent=2, sort_keys=True)

    return {
        "ok_label": "success" if result.ok else "failure",
        "action": result.action,
        "message": result.message,
        "files": result.files,
        "details": details,
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

    files = vm["files"]
    if files:
        parts.append("<p><strong>Files:</strong></p>")
        parts.append("<ul>")
        for file_path in files:
            parts.append(f"<li><code>{escape(str(file_path))}</code></li>")
        parts.append("</ul>")

    details = str(vm["details"])
    if details:
        parts.append("<p><strong>Details:</strong></p>")
        parts.append(f"<pre>{escape(details)}</pre>")

    parts.append("</section>")
    return "\n".join(parts)
