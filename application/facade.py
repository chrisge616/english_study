from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.config import ROOT
from app.paths import ensure_runtime_dirs
from application.path_context import PathContext
from application.results import ActionResult
from infrastructure.path_resolver import build_sync_paths, is_excluded
from infrastructure.sync_bridge import OutputSyncBridge
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

        prompt_text = build_daily_prompt_text()
        output_path = write_daily_prompt_file(prompt_text)
        relative_path = self._to_relative_path(output_path)

        return ActionResult(
            ok=True,
            action="generate_daily_prompt",
            message="Daily prompt generated successfully.",
            files=[relative_path],
            details={
                "path_context": self.path_context.to_dict(),
                "prompt_text": prompt_text,
            },
        )

    def generate_review_pack(self) -> ActionResult:
        ensure_runtime_dirs()

        plan_path = write_review_plan_file(build_review_plan_text())
        prompt_text = build_review_prompt_text()
        prompt_path = write_review_prompt_file(prompt_text)
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
            details={
                "path_context": self.path_context.to_dict(),
                "review_prompt_text": prompt_text,
            },
        )

    def get_current_paths(self) -> ActionResult:
        return ActionResult(
            ok=True,
            action="get_current_paths",
            message="Current paths loaded successfully.",
            files=[],
            details=self.path_context.to_dict(),
        )

    def sync_to_obsidian(self) -> ActionResult:
        ensure_runtime_dirs()

        try:
            sync_paths = build_sync_paths(self.path_context)
            result = OutputSyncBridge(sync_paths).sync_output_to_obsidian()
        except OSError as exc:
            return ActionResult(
                ok=False,
                action="sync_to_obsidian",
                message="Could not sync output files to the notes workspace.",
                files=[],
                details={"error": str(exc)},
            )

        return ActionResult(
            ok=True,
            action="sync_to_obsidian",
            message="Output files synced successfully.",
            files=result["copied_files"],
            details={"destination_root": result["destination_root"]},
        )

    def sync_daily_logs(self) -> ActionResult:
        ensure_runtime_dirs()

        try:
            sync_paths = build_sync_paths(self.path_context)
            result = OutputSyncBridge(sync_paths).sync_daily_logs_from_obsidian()
        except OSError as exc:
            return ActionResult(
                ok=False,
                action="sync_daily_logs",
                message="Could not sync daily logs from the notes workspace.",
                files=[],
                details={"error": str(exc)},
            )

        if result["conflicts"]:
            return ActionResult(
                ok=False,
                action="sync_daily_logs",
                message="Sync conflict on existing WSL log.",
                files=result["conflicts"],
                details=result,
            )

        all_files = result["copied_files"] + result["skipped_files"]
        if not all_files:
            return ActionResult(
                ok=False,
                action="sync_daily_logs",
                message="No daily logs found.",
                files=[],
                details=result,
            )

        return ActionResult(
            ok=True,
            action="sync_daily_logs",
            message="Daily logs synced successfully.",
            files=result["copied_files"] or result["skipped_files"],
            details=result,
        )

    def show_recent_daily_logs(self) -> ActionResult:
        sync_result = self._sync_daily_logs_before_ingest()
        if sync_result is not None:
            return sync_result

        recent_logs = self._get_recent_daily_logs()
        if not recent_logs:
            return ActionResult(
                ok=False,
                action="show_recent_daily_logs",
                message="No daily logs found.",
                files=[],
                details={"recent_daily_logs": []},
            )

        return ActionResult(
            ok=True,
            action="show_recent_daily_logs",
            message="Recent daily logs loaded successfully.",
            files=recent_logs,
            details={"recent_daily_logs": recent_logs},
        )

    def ingest_most_recent_daily_log(self) -> ActionResult:
        sync_result = self._sync_daily_logs_before_ingest()
        if sync_result is not None:
            return sync_result

        recent_logs = self._get_recent_daily_logs(limit=1)
        if not recent_logs:
            return ActionResult(
                ok=False,
                action="ingest_most_recent_daily_log",
                message="No daily logs found.",
                files=[],
                details={"recent_daily_logs": []},
            )

        target = ROOT / recent_logs[0]
        return self._ingest_log(
            path=str(target),
            action="ingest_daily_log",
            ingest_fn=ingest_daily_file,
            pre_synced=True,
        )

    def show_recent_review_logs(self) -> ActionResult:
        recent_logs = self._get_recent_review_logs()
        if not recent_logs:
            return ActionResult(
                ok=False,
                action="show_recent_review_logs",
                message="No review results found.",
                files=[],
                details={"recent_review_logs": []},
            )

        return ActionResult(
            ok=True,
            action="show_recent_review_logs",
            message="Recent review results loaded successfully.",
            files=recent_logs,
            details={"recent_review_logs": recent_logs},
        )

    def ingest_most_recent_review_log(self) -> ActionResult:
        recent_logs = self._get_recent_review_logs(limit=1)
        if not recent_logs:
            return ActionResult(
                ok=False,
                action="ingest_most_recent_review_log",
                message="No review results found.",
                files=[],
                details={"recent_review_logs": []},
            )

        target = ROOT / recent_logs[0]
        return self._ingest_log(
            path=str(target),
            action="ingest_review_log",
            ingest_fn=ingest_review_file,
            pre_synced=True,
        )

    def ingest_daily_log(self, path: str) -> ActionResult:
        return self._ingest_log(path=path, action="ingest_daily_log", ingest_fn=ingest_daily_file)

    def ingest_review_log(self, path: str) -> ActionResult:
        return self._ingest_log(path=path, action="ingest_review_log", ingest_fn=ingest_review_file)

    def ingest_pasted_review_markdown(self, markdown: str) -> ActionResult:
        ensure_runtime_dirs()

        raw_markdown = (markdown or "").strip()
        if not raw_markdown:
            return ActionResult(
                ok=False,
                action="ingest_pasted_review_markdown",
                message="Paste a completed review result before ingesting.",
                files=[],
                details={"review_markdown": ""},
            )

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix="_review.md",
            prefix="easy_mode_",
            dir=ROOT,
            encoding="utf-8",
            delete=False,
        ) as handle:
            handle.write(raw_markdown)
            temp_path = Path(handle.name)

        try:
            result = ingest_review_file(temp_path)
        except json.JSONDecodeError as exc:
            return ActionResult(
                ok=False,
                action="ingest_pasted_review_markdown",
                message="The pasted review result contains a machine block, but its JSON is not valid.",
                files=[],
                details={"error": str(exc)},
            )
        except FileNotFoundError:
            return ActionResult(
                ok=False,
                action="ingest_pasted_review_markdown",
                message="The pasted review result could not be prepared for ingest.",
                files=[],
                details=None,
            )
        finally:
            temp_path.unlink(missing_ok=True)

        if result.get("skipped") and result.get("reason") == "session already exists":
            return ActionResult(
                ok=False,
                action="ingest_pasted_review_markdown",
                message="This review result appears to have already been imported.",
                files=[],
                details={"session_id": result.get("session_id")},
            )

        return ActionResult(
            ok=True,
            action="ingest_pasted_review_markdown",
            message="Pasted review result imported successfully.",
            files=[],
            details={
                "session_id": result.get("session_id"),
                "processed": result.get("processed"),
            },
        )

    def _ingest_log(self, *, path: str, action: str, ingest_fn, pre_synced: bool = False) -> ActionResult:
        ensure_runtime_dirs()

        if action == "ingest_daily_log" and not pre_synced:
            sync_result = self._sync_daily_logs_before_ingest()
            if sync_result is not None:
                return sync_result

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

    def _sync_daily_logs_before_ingest(self) -> ActionResult | None:
        sync_result = self.sync_daily_logs()
        if sync_result.ok:
            return None
        return sync_result

    def _get_recent_daily_logs(self, *, limit: int = 5) -> list[str]:
        sync_paths = build_sync_paths(self.path_context)
        return self._get_recent_markdown_files(sync_paths.canonical_daily_logs_dir, limit=limit)

    def _get_recent_review_logs(self, *, limit: int = 5) -> list[str]:
        return self._get_recent_markdown_files(ROOT / "logs" / "review", limit=limit)

    def _get_recent_markdown_files(self, directory: Path, *, limit: int = 5) -> list[str]:
        if not directory.exists():
            return []

        candidates = [
            path
            for path in directory.glob("*.md")
            if path.is_file() and not is_excluded(path.relative_to(ROOT))
        ]
        recent_paths = sorted(candidates, key=lambda item: (item.stat().st_mtime, item.name), reverse=True)
        return [self._to_relative_path(path) for path in recent_paths[:limit]]

    def _to_relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
