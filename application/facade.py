from __future__ import annotations

from pathlib import Path

from app.config import ROOT
from app.paths import ensure_runtime_dirs
from application.path_context import PathContext
from application.results import ActionResult
from services.daily_prompt_service import build_daily_prompt_text, write_daily_prompt_file
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

    def _to_relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
