# AGENTS.md

## Repository expectations

### Project status
- This repository is currently in Gen2 stabilization and Gen2.1 planning.
- Prioritize documentation quality, template/interface upgrades, and safe validation.
- Do not expand core learning logic unless explicitly instructed.

### Formal operating model
- Formal CLI entrypoint: `study`
- Formal state layer: `data/study.db`
- Markdown files are interfaces, not the source of truth.

### Frozen modules
Do not modify these files unless the task explicitly authorizes it:
- `domain/policy.py`
- `domain/scheduler.py`
- `services/ingest_service.py`
- `storage/session_repo.py`

### Validation expectations
When making changes, prefer these checks:
- `python -m pytest -q`
- `study run daily`
- `study run review`

For rebuild verification, use the smoke baseline described in:
- `REBUILD_AND_SMOKE.md`

### Current operational baseline
Preserve these behaviors:
- `wrong -> WEAK`
- `correct -> STABLE`
- `partial -> WEAK but with slight progress`
- high-risk `WEAK` items may return early
- recently reviewed `STABLE` items should not immediately return
- repeated ingest with the same `session_id` should be skipped

### Current priority
The next implementation priority is Gen2.1 template/interface work:
1. `review_result_template.md` v2
2. `review_prompt.md` v2
3. `daily_prompt.md` v2
4. optional `daily_result_template.md`

### Change discipline
- Prefer service-layer and template-layer changes over core logic changes.
- Keep diffs minimal.
- If smoke workflow passes but a scheduler test fails, treat it as a test-alignment issue first.
- Update docs when behavior or workflow wording changes.

### Completion format
At the end of each task, report:
- touched files
- summary of changes
- validation commands run
- result of each validation
- risks or follow-up items
