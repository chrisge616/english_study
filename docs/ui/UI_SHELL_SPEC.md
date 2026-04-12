# UI_SHELL_SPEC.md

## 1. Document Status

- Status: Draft for implementation baseline
- Scope: Easy Mode UI shell for the current English Study system
- Intended phase: Post-Gen2 stabilization / early Gen2.1 productization
- Primary goal: make the current system usable with one-click operations for non-technical users

---

## 2. Problem Statement

The current system is functional, but the operating model is still developer-oriented.

Current pain points:

- users must run commands from a terminal
- users must understand WSL vs Windows vs Obsidian paths
- users must know when to generate prompts, where outputs are written, and how to ingest logs
- users must manually sync WSL work back to the Obsidian workspace

This creates a usability gap:

- the engine works
- the workflow exists
- but the product is not yet easy for a non-programmer to use

---

## 3. Product Goal

Build an **Easy Mode UI shell** that allows a non-technical user to operate the current system through a small number of buttons and simple forms, without directly using terminal commands.

The UI shell should:

- expose the most common daily/review workflows as one-click actions
- keep the current engine behavior intact
- hide WSL/CLI complexity from the user
- automatically handle synchronization between the WSL canonical repo and the Obsidian workspace when appropriate

---

## 4. Non-Goals

This phase must **not** do the following:

- do not redesign or expand the learning core
- do not rewrite the scheduler, policy, ingest semantics, or session storage
- do not turn the project into a full desktop app in this phase
- do not build an Obsidian plugin in this phase
- do not replace the current `study` workflow engine
- do not introduce a second competing business-logic path separate from the existing engine

---

## 5. Frozen Boundaries

The following files/modules remain frozen unless explicitly reopened later:

- `domain/policy.py`
- `domain/scheduler.py`
- `services/ingest_service.py`
- `storage/session_repo.py`

The UI shell must be designed to wrap the current workflow, not modify these modules.

---

## 6. Current Operating Baseline

### Canonical execution environment

The current canonical engine lives in WSL:

- WSL canonical repo: `/home/chris/code/english_study`

### Human-facing workspace

The synchronized Obsidian workspace lives on Windows:

- Obsidian workspace: `C:\Users\Chris\Documents\Obsidian Vault\english_study`

### Current formal operating model

- formal CLI entrypoint: `study`
- formal state layer: `data/study.db`
- markdown files are interfaces, not source of truth
- generated files are written under `output/`
- human-completed logs live under `logs/`

### Recently stabilized items

- review result template v2
- review prompt aligned to template v2
- daily prompt upgraded to clearer v2 structure
- minimal repo hygiene completed

---

## 7. Recommended Architecture

### Final recommendation

Use this layered architecture:

1. **Canonical Engine Layer** (existing, in WSL)
2. **Application Facade Layer** (new)
3. **UI Shell Layer** (new)
4. **Sync Bridge Layer** (new)

### 7.1 Canonical Engine Layer

Keep the existing system as the only execution engine.

This includes:

- `app/`
- `domain/`
- `services/`
- `ingest/`
- `storage/`
- `study` CLI behavior

This layer remains the source of actual workflow execution.

### 7.2 Application Facade Layer

Add a thin action layer that exposes higher-level operations for UI and launcher use.

Suggested location:

```text
application/
  facade.py
  actions.py
  dto.py
  results.py
  path_context.py
```

Responsibilities:

- wrap common actions into explicit functions
- return structured success/failure results
- keep UI code from constructing raw shell commands everywhere
- provide one place to manage workflow orchestration

Example actions:

- `generate_daily_prompt()`
- `generate_review_pack()`
- `ingest_daily_log(path)`
- `ingest_review_log(path)`
- `inspect_state_summary()`
- `sync_obsidian_workspace()`

### 7.3 UI Shell Layer

Phase 1 should be a **local Web UI or launcher-style local UI**, not a plugin.

Suggested location:

```text
ui_shell/
  server.py
  routes.py
  viewmodels.py
  templates/
  static/
```

Responsibilities:

- render buttons and simple forms
- call the Application Facade
- show outputs, recent files, and execution results
- show friendly errors instead of terminal traces

### 7.4 Sync Bridge Layer

Suggested location:

```text
infrastructure/
  sync_bridge.py
  path_resolver.py
  wsl_runner.py
```

Responsibilities:

- understand WSL canonical path vs Obsidian workspace path
- perform safe pre-run / post-run syncs
- exclude environment junk (`.venv`, `__pycache__`, etc.)
- keep Windows workspace readable without becoming the canonical engine

---

## 8. Why this Architecture is Preferred

This is the recommended architecture because it:

- preserves the current stable engine
- respects frozen boundaries
- introduces usability without core churn
- reduces risk compared with a plugin or full desktop app
- creates a future path toward plugin or app packaging if needed later

This is explicitly preferred over:

- direct core rewrite
- immediate Obsidian plugin development
- immediate Electron-style desktop app
- trying to make the Windows Obsidian folder the canonical runtime

---

## 9. User Model

Target user:

- understands English-learning workflow
- does **not** understand terminal commands, WSL, Git, or Python environment management

Target experience:

- user clicks one launcher
- user sees a small control panel
- user presses a button
- output is generated and shown
- user opens/edit logs in Obsidian
- user ingests completed logs without writing commands manually

---

## 10. Phase 1 UI Surface

The first version should expose only the most valuable actions.

### 10.1 Daily section

Buttons:

- Generate Daily Prompt
- Open Latest Daily Prompt
- Ingest Daily Log

### 10.2 Review section

Buttons:

- Generate Review Pack
- Open Review Plan
- Open Review Prompt
- Open Review Result Template
- Ingest Review Result

### 10.3 Status section

Buttons / panels:

- Inspect Summary
- Show Recent Generated Files
- Show Last Action Result

### 10.4 Workspace section

Buttons:

- Sync to Obsidian
- Open Obsidian Workspace Folder
- Show Current Paths

---

## 11. Phase 1 UX Rules

### Mandatory UX rules

- one action per button
- each action must report success/failure clearly
- every generated file path must be shown after success
- errors must be translated into simple explanations
- do not expose raw command syntax to the user in the primary UI
- do not require the user to understand WSL paths during normal operation

### Preferred UX language

Use user-facing labels like:

- Generate Daily Prompt
- Review files created successfully
- Daily log imported successfully
- Could not import file because session ID already exists

Avoid exposing technical messages unless the user opens a “details” view.

---

## 12. Action Contracts

### 12.1 Generate Daily Prompt

Input:

- none

Behavior:

- ensure repo context is ready
- generate latest daily prompt
- sync result to Obsidian workspace
- return path of generated file

Output example:

- success: generated `output/daily_prompt.md`
- show a button to open it

### 12.2 Generate Review Pack

Input:

- none

Behavior:

- generate review plan
- generate review prompt
- generate review result template
- sync outputs to Obsidian workspace

Outputs:

- `output/review_plan.md`
- `output/review_prompt.md`
- `output/review_result_template.md`

### 12.3 Ingest Daily Log

Input:

- file picker for a daily log markdown file

Behavior:

- validate path exists
- run daily ingest using current engine/facade
- report result clearly

Output:

- success/failure
- session id
- processed item count if available

### 12.4 Ingest Review Result

Input:

- file picker for review result markdown file

Behavior:

- validate path exists
- run review ingest using current engine/facade
- report result clearly

### 12.5 Inspect Summary

Input:

- optional word query in later phase

Behavior:

- call inspect summary action
- show basic counts and recent status

---

## 13. Sync Strategy

### Canonical rule

- WSL repo is the canonical engine
- Obsidian workspace is the synchronized human workspace

### Pre-run sync

For actions that ingest user-edited logs, the system may need to sync Obsidian-side edits back into WSL before execution.

Suggested pre-run sync targets:

- `logs/daily/`
- `logs/review/`

### Post-run sync

For generation actions, sync updated outputs back to Obsidian.

Suggested post-run sync targets:

- `output/`
- relevant `docs/` when needed

### Sync exclusions

Must exclude:

- `.git/`
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `*.pyo`
- `english_study.egg-info/`
- `.pytest_cache/`

---

## 14. Path Strategy

The UI should display simplified labels, not raw system paths by default.

Example display:

- Engine Workspace: WSL canonical repo
- Notes Workspace: Obsidian vault folder
- Database: `data/study.db`

A secondary “details” panel can reveal exact paths.

---

## 15. Error Handling

The UI shell must normalize common failure cases into plain language.

Examples:

### File not found

Display:

- Could not find the selected markdown file.

### Duplicate ingest / repeated session

Display:

- This log appears to have already been imported.

### Invalid machine block

Display:

- The file contains a machine block, but its JSON is not valid.

### Runtime environment unavailable

Display:

- The study engine could not start correctly. Please reopen Easy Mode or check the engine setup.

---

## 16. Logging / Result Model

Each action should return a normalized result object.

Suggested result shape:

```python
{
  "ok": True,
  "action": "generate_daily_prompt",
  "message": "Daily prompt generated successfully.",
  "files": ["output/daily_prompt.md"],
  "details": None,
}
```

This does not need to be implemented exactly as above, but the design should aim for consistent result reporting.

---

## 17. Implementation Constraints

### Allowed focus areas

Phase 1 may add or modify:

- new UI shell files
- new façade / orchestration files
- safe path/sync infrastructure
- launcher files
- small documentation additions related to Easy Mode

### Avoid in Phase 1

- direct changes to frozen modules
- parser redesign
- scheduler redesign
- policy redesign
- database schema redesign
- major changes to ingest semantics

---

## 18. Recommended Phase Breakdown

### Phase 1 — Spec and skeleton

Deliverables:

- `UI_SHELL_SPEC.md`
- tentative folder layout
- action list
- execution path decisions

### Phase 2 — Minimum usable shell

Deliverables:

- launcher
- local UI server or local app shell
- buttons for daily/review generate + ingest
- path display
- status/result display

### Phase 3 — Usability polish

Deliverables:

- recent files panel
- open file buttons
- last action status
- cleaner error explanations

### Phase 4 — Optional future expansion

Potential directions:

- Obsidian command integration
- plugin layer
- desktop packaging
- richer inspect views

---

## 19. Acceptance Criteria for Phase 2

The first real UI shell should be considered acceptable if a non-technical user can do the following without touching terminal commands:

1. generate a daily prompt
2. generate a review pack
3. open the generated files in the Obsidian workspace
4. choose a finished daily/review log file for ingest
5. run ingest successfully
6. see a simple success/failure result
7. not need to know WSL paths or activate Python venv manually

---

## 20. Best Current Implementation Direction

The recommended next implementation move is:

1. create this spec in the canonical repo
2. commit and sync it
3. open a fresh conversation
4. begin Phase 1 implementation planning for:
   - façade layer
   - launcher design
   - minimum UI shell

---

## 21. Final Recommendation

The best architecture for the current operating model is:

**WSL Canonical Engine + Application Facade + Easy Mode UI Shell + Automatic Obsidian Sync**

This architecture is recommended because it best balances:

- current system stability
- low implementation risk
- user-facing simplicity
- future extensibility
