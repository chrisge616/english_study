from __future__ import annotations

import json
from pathlib import Path

from app.config import ROOT
from app.paths import ensure_runtime_dirs
from application.path_context import PathContext
from application.results import ActionResult
from services.daily_prompt_service import build_daily_prompt_text, write_daily_prompt_file
from services.ingest_service import ingest_daily_file, ingest_review_file
from services.review_plan_service import build_review_plan_text, write_review_plan_file
from services.review_prompt_service import build_review_prompt_text, write_review_prompt_file
from services.review_template_service import (
    build_review_result_template_text,
    write_review_result_template_file,
)


class EasyModeFacade:
    def __init__(self, *, path_context: PathContext | None = None) -> None:
        self.path_context = path_context or PathContext.from_defaults()

    def generate_daily_prompt(self) -> ActionResult:
        ensure_runtime_dirs()

        output_path = write_daily_prompt_file(build_daily_prompt_text())
        relative_path = self._to_relative_path(output_path)

        return ActionResult(
            ok=True,
            action="generate_daily_prompt",
            message="Daily prompt generated successfully.",
            files=[relative_path],
            details={"path_context": self.path_context.to_dict()},
        )

    def generate_review_pack(self) -> ActionResult:
        ensure_runtime_dirs()

        plan_path = write_review_plan_file(build_review_plan_text())
        prompt_path = write_review_prompt_file(build_review_prompt_text())
        template_path = write_review_result_template_file(build_review_result_template_text())

        files = [
            self._to_relative_path(plan_path),
            self._to_relative_path(prompt_path),
            self._to_relative_path(template_path),
        ]

        return ActionResult(
            ok=True,
            action="generate_review_pack",
            message="Review files created successfully.",
            files=files,
            details={"path_context": self.path_context.to_dict()},
        )

    def get_current_paths(self) -> ActionResult:
        return ActionResult(
            ok=True,
            action="get_current_paths",
            message="Current paths loaded successfully.",
            files=[],
            details=self.path_context.to_dict(),
        )

    def ingest_daily_log(self, path: str) -> ActionResult:
        return self._ingest_log(path=path, action="ingest_daily_log", ingest_fn=ingest_daily_file)

    def ingest_review_log(self, path: str) -> ActionResult:
        return self._ingest_log(path=path, action="ingest_review_log", ingest_fn=ingest_review_file)

    def _ingest_log(self, *, path: str, action: str, ingest_fn) -> ActionResult:
        ensure_runtime_dirs()

        raw_path = (path or "").strip()
        if not raw_path:
            return ActionResult(
                ok=False,
                action=action,
                message="Could not find the selected markdown file.",
                files=[],
                details={"path": raw_path},
            )

        target = Path(raw_path).expanduser()
        if not target.exists():
            return ActionResult(
                ok=False,
                action=action,
                message="Could not find the selected markdown file.",
                files=[raw_path],
                details={"path": raw_path},
            )

        try:
            result = ingest_fn(target)
        except json.JSONDecodeError as exc:
            return ActionResult(
                ok=False,
                action=action,
                message="The file contains a machine block, but its JSON is not valid.",
                files=[self._to_relative_path(target)],
                details={"path": str(target), "error": str(exc)},
            )
        except FileNotFoundError:
            return ActionResult(
                ok=False,
                action=action,
                message="Could not find the selected markdown file.",
                files=[raw_path],
                details={"path": raw_path},
            )

        return self._build_ingest_result(action=action, path=target, result=result)

    def _build_ingest_result(self, *, action: str, path: Path, result: dict) -> ActionResult:
        if result.get("skipped") and result.get("reason") == "session already exists":
            return ActionResult(
                ok=False,
                action=action,
                message="This log appears to have already been imported.",
                files=[self._to_relative_path(path)],
                details={"session_id": result.get("session_id")},
            )

        label = "Daily log imported successfully." if action == "ingest_daily_log" else "Review result imported successfully."
        details = {
            "session_id": result.get("session_id"),
            "processed": result.get("processed"),
        }

        return ActionResult(
            ok=True,
            action=action,
            message=label,
            files=[self._to_relative_path(path)],
            details=details,
        )

    def _to_relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
