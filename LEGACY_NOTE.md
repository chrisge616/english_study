# Legacy / Transition Files Note

The repository still contains earlier Gen1 / transition-era files such as:

- `prepare_review_chat.py`
- `prepare_daily_chat.py`
- `pipeline.py`
- `auto_pipeline.py`
- older dashboard files

These are not the formal entrypoint for the current Gen2 workflow.

Current official entrypoint:
- `study` CLI

Recommended action:
- move old scripts to a `legacy/` folder, or
- add a clear `DEPRECATED` header at the top of each old file
