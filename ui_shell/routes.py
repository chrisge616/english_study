from __future__ import annotations

from application.facade import EasyModeFacade
from application.results import ActionResult


def dispatch_action(facade: EasyModeFacade, action_name: str, *, path: str = "") -> ActionResult:
    actions = {
        "generate_daily_prompt": facade.generate_daily_prompt,
        "generate_review_pack": facade.generate_review_pack,
        "get_current_paths": facade.get_current_paths,
        "sync_to_obsidian": facade.sync_to_obsidian,
        "sync_daily_logs": facade.sync_daily_logs,
        "show_recent_daily_logs": facade.show_recent_daily_logs,
        "ingest_most_recent_daily_log": facade.ingest_most_recent_daily_log,
        "ingest_daily_log": lambda: facade.ingest_daily_log(path),
        "ingest_review_log": lambda: facade.ingest_review_log(path),
    }

    action = actions.get(action_name)
    if action is None:
        return ActionResult(
            ok=False,
            action=action_name or "unknown",
            message="Unknown action.",
            files=[],
            details=None,
        )

    try:
        return action()
    except Exception as exc:
        return ActionResult(
            ok=False,
            action=action_name,
            message="The study engine could not complete the action.",
            files=[],
            details={"error": str(exc)},
        )
