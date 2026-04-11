# USER GUIDE — English Study System (Gen2 Core v0.1)

This guide explains how to operate the current Gen2 system in normal daily use.

It is written for the current project layout and the current formal CLI entrypoint: `study`.

---

## 1. Project Root

Current Windows project root:

`C:\Users\Chris\Documents\Obsidian Vault\english_study`

Recommended working assumption:

- source code lives inside the repository
- generated files go into `output/`
- daily logs go into `logs/daily/`
- review logs go into `logs/review/`
- SQLite state lives in `data/study.db`

---

## 2. Before You Start

### 2.1 Activate the environment

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
```

If the environment is not set up yet:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### 2.2 Confirm the CLI is available

```powershell
study --help
```

If this works, the formal CLI entrypoint is ready.

---

## 3. Runtime Folders and Main Files

### 3.1 Generated output files

The system writes these files into `output/`:

- `daily_prompt.md`
- `review_plan.md`
- `review_prompt.md`
- `review_result_template.md`

### 3.2 Input log folders

Store your logs here:

- daily logs -> `logs/daily/`
- review logs -> `logs/review/`

### 3.3 Database file

Persistent state is stored in:

- `data/study.db`

Do not treat generated files as the source of truth. SQLite is the formal state layer.

---

## 4. First-Time Initialization

If you are starting from a fresh local state, initialize the database first:

```powershell
study init-db
```

Expected result:

- database file created at `data/study.db`
- runtime folders created if missing

You do **not** need to run `study init-db` every day. It is mainly for first setup or a fresh rebuild.

---

## 5. Daily Workflow

Use this workflow when you finish a daily learning session and want to add new material into the system.

### Step 1 — Generate the daily prompt

```powershell
study prepare daily
```

This writes:

- `output/daily_prompt.md`

### Step 2 — Use the prompt in ChatGPT

Open `output/daily_prompt.md` and use it in ChatGPT to generate the daily learning log.

### Step 3 — Save the generated daily log

Save the generated markdown file into:

- `logs/daily/`

Recommended naming style:

- `YYYY-MM-DD_gen2.md`
- `YYYY-MM-DD_daily.md`

Example:

- `logs/daily/2026-04-11_gen2.md`

### Step 4 — Ingest the daily log

```powershell
study ingest daily "C:\Users\Chris\Documents\Obsidian Vault\english_study\logs\daily\2026-04-11_gen2.md"
```

Expected result:

- words are added or updated in SQLite
- evidence is created
- word state is updated based on suggested status signals

### Step 5 — Sanity-check if needed

```powershell
study inspect state --limit 15
```

Or inspect one word:

```powershell
study inspect word <word>
```

---

## 6. Review Workflow

Use this workflow when you want to review due or risky words.

### Step 1 — Generate review materials

```powershell
study run review
```

This writes:

- `output/review_plan.md`
- `output/review_prompt.md`
- `output/review_result_template.md`

### Step 2 — Run the review session in ChatGPT

Use `output/review_prompt.md` as the prompt for the review session.

### Step 3 — Fill in the review result template

Open:

- `output/review_result_template.md`

Fill in the human-readable sections such as:

- recall summary
- usage summary
- concept summary
- weak words
- pattern mistakes
- next action
- status update table

The generated review result template now separates:

- `HUMAN-EDITABLE SECTION`
- `STATUS UPDATE TABLE`
- `MACHINE SECTION - DO NOT EDIT STRUCTURE`

Treat the human-editable section and the status update table as your normal notes area.
The machine section remains the ingest-critical structure.

### Step 4 — Keep the machine block valid

At the bottom of the review result template there is a machine-readable block inside:

```text
<!-- STUDY_SESSION_DATA ... -->
```

This block is important.

Rules:

- do not remove it
- do not break its JSON structure
- do not change quote marks into smart quotes
- keep each item result in valid lower-case values such as `correct`, `partial`, or `wrong`

If the machine block remains valid, review ingest is more reliable.

### Step 5 — Save the filled review log

Save the completed file into:

- `logs/review/`

Recommended naming style:

- `YYYY-MM-DD_review.md`

Example:

- `logs/review/2026-04-11_review.md`

### Step 6 — Ingest the review log

```powershell
study ingest review "C:\Users\Chris\Documents\Obsidian Vault\english_study\logs\review\2026-04-11_review.md"
```

Expected result:

- review evidence is added
- state transitions are applied
- streaks and due timing are updated

### Step 7 — Inspect the result

Useful checks:

```powershell
study inspect state --status WEAK --limit 15
study inspect word nuance
study inspect word advance
study inspect word reconstitute
```

---

## 7. Inspection Commands

### 7.1 Inspect the overall state

```powershell
study inspect state
```

Useful options:

```powershell
study inspect state --status WEAK --limit 15
study inspect state --status STABLE --sort alpha
study inspect state --sort status
```

Use this when you want to:

- see current status distribution
- spot weak words
- check whether ingest worked
- quickly inspect priorities

### 7.2 Inspect one word

```powershell
study inspect word nuance
study inspect word advance
study inspect word reconstitute
```

Optional evidence limit:

```powershell
study inspect word nuance --evidence-limit 12
```

Use this when you want to confirm:

- current status
- review result history
- evidence trail
- current streak behavior

---

## 8. Fresh Rebuild / Smoke Workflow

Use this when you want to rebuild a clean local baseline and verify that Gen2 still behaves as expected.

### Step 1 — Remove the local database

```powershell
Remove-Item "C:\Users\Chris\Documents\Obsidian Vault\english_study\data\study.db"
```

If the file does not exist yet, that is fine.

### Step 2 — Recreate the database

```powershell
study init-db
```

### Step 3 — Re-ingest the smoke sample daily logs

```powershell
study ingest daily "C:\Users\Chris\Documents\Obsidian Vault\english_study\logs\daily\2026-04-07_gen2.md"
study ingest daily "C:\Users\Chris\Documents\Obsidian Vault\english_study\logs\daily\2026-04-08_gen2.md"
study ingest daily "C:\Users\Chris\Documents\Obsidian Vault\english_study\logs\daily\2026-04-10_gen2.md"
```

### Step 4 — Re-ingest the smoke sample review log

```powershell
study ingest review "C:\Users\Chris\Documents\Obsidian Vault\english_study\logs\review\2026-04-10_review.md"
```

### Step 5 — Check the expected spot results

```powershell
study inspect word nuance
study inspect word advance
study inspect word reconstitute
```

Current expected baseline:

- `nuance` -> `WEAK`
- `advance` -> `STABLE`
- `reconstitute` -> `WEAK` with slight progress retained

---

## 9. What “Normal” Behavior Looks Like

These are the current expected behaviors for Gen2 stabilization:

- `wrong -> WEAK`
- `correct -> STABLE`
- `partial -> WEAK but with slight progress`
- some risky `WEAK` items may return before full due
- recently reviewed `STABLE` items should not immediately come back
- repeated ingest with the same `session_id` should be skipped

If your results differ materially from these, inspect the input log and the database state before changing core logic.

---

## 10. Common Issues and What to Check

### Issue 1 — `study` command not found

Check:

- virtual environment is activated
- `pip install -e .` was run successfully
- you are in the project root

### Issue 2 — Daily ingest processed 0 items

Check:

- the daily markdown actually contains `- Word:` lines
- the file path points to the intended log
- the same file was not already ingested under the same session id

Remember:

- daily ingest uses the filename stem to form the fallback `session_id`
- repeated ingest of the same session is intentionally skipped

### Issue 3 — Review ingest processed 0 items or missed results

Check:

- the `<!-- STUDY_SESSION_DATA ... -->` block still exists
- the JSON inside the machine block is valid
- each review item has a valid `result`
- the file is the completed review result, not just the prompt

Fallback behavior exists for the status update table, but keeping the machine block valid is the safer path.

### Issue 4 — A session was skipped unexpectedly

Expected skip result looks like this:

- `processed: 0`
- `skipped: True`
- `reason: session already exists`

This usually means the same `session_id` was already ingested.

### Issue 5 — Output files were not generated

Check:

- you ran the correct `prepare` or `run` command
- the runtime folders exist
- the CLI started successfully

The CLI should create required runtime folders automatically.

### Issue 6 — Word state looks wrong after review

Check:

- whether the review result was entered as `correct`, `partial`, or `wrong`
- whether you inspected the correct word
- whether the review file was ingested only once
- whether you are comparing against the current frozen Gen2 policy, not an older expectation

---

## 11. Safe Operating Rules During Stabilization

During Gen2 stabilization:

- prefer the `study` CLI over older scripts
- do not treat markdown outputs as the database
- do not manually edit `study.db`
- do not casually change frozen modules
- do not redesign scheduler or policy while validating the current baseline
- verify behavior with smoke samples before concluding there is a bug

Frozen modules:

- `domain/policy.py`
- `domain/scheduler.py`
- `services/ingest_service.py`
- `storage/session_repo.py`

---

## 12. Current Non-Goals

Do not prioritize these right now:

- redesigning policy
- redesigning the scheduler
- rewriting ingest dedup logic
- adding major new core behavior
- implementing Gen3
- implementing Gen4

The current correct focus is:

- stable operation
- documentation quality
- real usage
- evidence accumulation
- later Gen2.1 planning

---

## 13. Recommended Practical Routine

A simple working routine is:

### Daily

1. run `study prepare daily`
2. generate the daily log with ChatGPT
3. save it under `logs/daily/`
4. run `study ingest daily <file>`

### Review

1. run `study run review`
2. do the review with `output/review_prompt.md`
3. fill `output/review_result_template.md`
4. save it under `logs/review/`
5. run `study ingest review <file>`
6. inspect important words when needed

---

## 14. Related Documents

- `README.md` — project overview and architecture-level summary
- `REBUILD_AND_SMOKE.md` — clean rebuild and validation procedure
- `LEGACY_NOTE.md` — notes about older tooling and historical context

---

## 15. Final Rule of Thumb

If something looks off, do this order first:

1. check the input file
2. check whether the session was already ingested
3. inspect the affected word
4. compare against the current verified Gen2 baseline
5. only then decide whether this is a real bug
