import argparse
from pathlib import Path

from app.paths import ensure_runtime_dirs
from services.ingest_service import ingest_daily_file, ingest_review_file
from services.review_plan_service import build_review_plan_text, write_review_plan_file
from services.daily_prompt_service import build_daily_prompt_text, write_daily_prompt_file
from services.review_prompt_service import build_review_prompt_text, write_review_prompt_file
from services.review_template_service import build_review_result_template_text, write_review_result_template_file
from services.inspect_service import build_state_inspection_text, build_word_inspection_text
from storage.migrations import init_db


def main() -> None:
    parser = argparse.ArgumentParser(prog="study")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db")

    ingest_parser = subparsers.add_parser("ingest")
    ingest_sub = ingest_parser.add_subparsers(dest="ingest_type", required=True)

    ingest_daily = ingest_sub.add_parser("daily")
    ingest_daily.add_argument("file_path")

    ingest_review = ingest_sub.add_parser("review")
    ingest_review.add_argument("file_path")

    prepare_parser = subparsers.add_parser("prepare")
    prepare_sub = prepare_parser.add_subparsers(dest="prepare_type", required=True)
    prepare_sub.add_parser("review")
    prepare_sub.add_parser("daily")
    prepare_sub.add_parser("review-prompt")
    prepare_sub.add_parser("review-template")

    run_parser = subparsers.add_parser("run")
    run_sub = run_parser.add_subparsers(dest="run_type", required=True)
    run_sub.add_parser("review")
    run_sub.add_parser("daily")

    inspect_parser = subparsers.add_parser("inspect")
    inspect_sub = inspect_parser.add_subparsers(dest="inspect_type", required=True)

    inspect_state = inspect_sub.add_parser("state")
    inspect_state.add_argument("--status", default=None)
    inspect_state.add_argument("--limit", type=int, default=None)
    inspect_state.add_argument("--sort", choices=["priority", "alpha", "status"], default="priority")

    inspect_word = inspect_sub.add_parser("word")
    inspect_word.add_argument("word")
    inspect_word.add_argument("--evidence-limit", type=int, default=8)

    args = parser.parse_args()
    ensure_runtime_dirs()

    if args.command == "init-db":
        init_db()
        print("[study] database initialized")
        return

    if args.command == "ingest":
        path = Path(args.file_path)
        if args.ingest_type == "daily":
            result = ingest_daily_file(path)
            print(f"[study] daily ingested: {result}")
            return
        if args.ingest_type == "review":
            result = ingest_review_file(path)
            print(f"[study] review ingested: {result}")
            return

    if args.command == "prepare":
        if args.prepare_type == "review":
            text = build_review_plan_text()
            output_path = write_review_plan_file(text)
            print(text)
            print(f"\n[study] review plan written: {output_path}")
            return
        if args.prepare_type == "daily":
            text = build_daily_prompt_text()
            output_path = write_daily_prompt_file(text)
            print(text)
            print(f"\n[study] daily prompt written: {output_path}")
            return
        if args.prepare_type == "review-prompt":
            text = build_review_prompt_text()
            output_path = write_review_prompt_file(text)
            print(text)
            print(f"\n[study] review prompt written: {output_path}")
            return
        if args.prepare_type == "review-template":
            text = build_review_result_template_text()
            output_path = write_review_result_template_file(text)
            print(text)
            print(f"\n[study] review result template written: {output_path}")
            return

    if args.command == "run":
        if args.run_type == "review":
            plan_text = build_review_plan_text()
            plan_path = write_review_plan_file(plan_text)

            prompt_text = build_review_prompt_text()
            prompt_path = write_review_prompt_file(prompt_text)

            template_text = build_review_result_template_text()
            template_path = write_review_result_template_file(template_text)

            print(plan_text)
            print(f"\n[study] review plan written: {plan_path}")
            print(f"[study] review prompt written: {prompt_path}")
            print(f"[study] review result template written: {template_path}")
            return

        if args.run_type == "daily":
            prompt_text = build_daily_prompt_text()
            prompt_path = write_daily_prompt_file(prompt_text)

            print(prompt_text)
            print(f"\n[study] daily prompt written: {prompt_path}")
            return

    if args.command == "inspect":
        if args.inspect_type == "state":
            print(build_state_inspection_text(status=args.status, limit=args.limit, sort_by=args.sort))
            return
        if args.inspect_type == "word":
            print(build_word_inspection_text(args.word, evidence_limit=args.evidence_limit))
            return


if __name__ == "__main__":
    main()
