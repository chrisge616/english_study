# BETTER_TEMPLATES_SPEC — Gen2.1 Design Spec

This document defines the **better templates** track for Gen2.1.

It is intentionally scoped as a **documentation and interface upgrade**, not a core learning-logic redesign.

The goal is to make the current Gen2 workflows:

- easier to use
- harder to break
- more consistent across daily and review sessions
- more reliable for ingest

This spec assumes the current frozen Gen2 baseline remains unchanged.

---

## 1. Why This Is First in Gen2.1

Among the current Gen2.1 candidates, better templates should come first because it has the best tradeoff:

- high user-facing value
- low architectural risk
- low likelihood of touching frozen core logic
- immediate improvement to daily operation quality

It also improves the quality of later features such as:

- weekly summary
- mistake pattern tracking

because cleaner, more consistent logs produce cleaner downstream signals.

---

## 2. Scope

This spec covers template/interface upgrades for:

1. daily prompt
2. review prompt
3. review result template
4. optional daily result template

It does **not** redesign:

- policy behavior
- scheduler behavior
- session dedup logic
- storage schema
- scoring semantics

---

## 3. Current Problems to Solve

The current templates are workable, but still have several friction points:

### 3.1 Mixed audience
Some template sections are written partly for the human user and partly for the parser, which makes them easy to misunderstand.

### 3.2 Format fragility
Review ingest is more reliable when the machine block remains intact, but the current workflow still leaves room for accidental breakage.

### 3.3 Inconsistent structure
Daily and review artifacts do not yet feel like one coherent operating system. They work, but the structure is not fully unified.

### 3.4 Weak guidance for output quality
The templates generate usable content, but they can do more to encourage:

- concise answers
- better examples
- clearer mistake capture
- stronger status reasoning
- more consistent wording

### 3.5 Missing daily result contract
Daily flow has a prompt, but not a fully standardized result template in the same way review does.

---

## 4. Goals

Better templates should achieve the following:

1. make the workflows easier to follow without re-reading old context
2. reduce accidental template damage
3. make generated files more readable
4. make ingest inputs more consistent
5. preserve current Gen2 semantics
6. improve future extensibility for Gen2.1 reporting

---

## 5. Non-Goals

Better templates should **not**:

- change word-state transitions
- change due logic
- change evidence semantics
- introduce a new learning model
- require migration of historical data
- require redesign of frozen modules

---

## 6. Frozen Boundary to Respect

During this work, do not redesign or casually modify:

- `domain/policy.py`
- `domain/scheduler.py`
- `services/ingest_service.py`
- `storage/session_repo.py`

This spec should be implemented primarily through template and service-layer output improvements.

---

## 7. Design Principles

### 7.1 Human-first surface, machine-safe structure
Templates should remain pleasant to read, but the parser-critical parts should be clearly isolated.

### 7.2 One workflow, one contract
Each generated artifact should have a clear purpose:

- prompt files tell ChatGPT what to do
- result templates tell the user what to fill in
- machine blocks support reliable ingest

### 7.3 Explicit editable zones
Human-editable sections and non-editable machine sections should be visually and conceptually separated.

### 7.4 Graceful future extension
New summary and mistake-pattern features should be able to reuse the improved outputs later.

---

## 8. Template Inventory

Current Gen2 files:

- `output/daily_prompt.md`
- `output/review_plan.md`
- `output/review_prompt.md`
- `output/review_result_template.md`

Proposed Gen2.1 template surface:

- keep `daily_prompt.md`
- keep `review_prompt.md`
- keep `review_result_template.md`
- keep `review_plan.md`
- optionally add `daily_result_template.md`

---

## 9. Proposed Improvements by Artifact

## 9.1 `daily_prompt.md` v2

### Current role
Used to prompt ChatGPT to generate a daily learning log.

### Main improvement goals
- make the requested output structure clearer
- reduce ambiguity around required sections
- improve consistency of vocabulary entries
- make downstream ingest safer

### Recommended structure
1. purpose header
2. generation rules
3. required output format
4. vocabulary item structure
5. optional mistakes/concepts/tests section
6. naming/storage hint

### Recommended output constraints
For each vocabulary item, strongly standardize:

- Word
- Meaning (simple English)
- Example
- Suggested Status

Optional but useful additions:

- Part of speech
- Chinese note
- confusion note
- source context

### Important design choice
Keep the daily log **human-readable first**. Do not over-machine-encode it unless needed for actual ingest reliability.

---

## 9.2 `review_prompt.md` v2

### Current role
Used to run the actual review session in ChatGPT.

### Main improvement goals
- make the session flow clearer
- separate review execution from result formatting
- encourage stronger mistake capture
- improve consistency across different review sessions

### Recommended structure
1. session purpose
2. review word list
3. answer rules
4. expected answer style
5. review dimensions
6. result handoff reminder

### Recommended review dimensions
For each word, the prompt should guide ChatGPT to test:

- recall
- usage
- concept/nuance
- confidence or certainty
- common confusion if relevant

### Recommended tone constraint
The prompt should encourage direct, structured evaluation rather than overly conversational review output.

---

## 9.3 `review_result_template.md` v2

### Current role
Human-filled result template that later feeds review ingest.

### Main improvement goals
- make editable sections clearer
- reduce accidental machine block breakage
- standardize result capture
- make mistakes more reusable later

### Recommended structure
1. session metadata
2. human summary sections
3. per-word status update table
4. pattern mistakes section
5. next action section
6. protected machine block

### Strong recommendation
Add a visible divider such as:

```text
HUMAN-EDITABLE SECTION
```

and later:

```text
MACHINE SECTION — DO NOT EDIT STRUCTURE
```

This is a low-cost, high-value change.

### Status update table recommendations
Standardize the columns. Suggested columns:

- Word
- Result
- Confidence
- Notes
- Suggested Follow-up

Keep `Result` values constrained to:

- `correct`
- `partial`
- `wrong`

### Pattern mistakes section
Add a more structured section to capture reusable review mistakes, such as:

- confusion type
- affected words
- short explanation
- recommended next action

This helps future `mistake pattern tracking` without changing core policy now.

### Machine block recommendations
Preserve a single authoritative machine block at the bottom.

Requirements:

- valid JSON
- stable keys
- no smart quotes
- no manual prose inserted inside the JSON
- one item entry per review word

---

## 9.4 `daily_result_template.md` v0 (optional)

This is the most optional part of the better templates track, but also potentially very useful.

### Why add it
Daily generation currently relies more on a prompt than on a fully formalized result template.

A daily result template would help:
- unify output shape
- reduce formatting drift
- improve ingest consistency
- make daily logs easier to compare over time

### Minimal recommended structure
1. date/session metadata
2. vocabulary section
3. mistakes & corrections
4. key concepts
5. test bank
6. suggested review timing
7. suggested status

### Recommendation
Treat this as **v0 optional**, not mandatory for the first implementation pass.

---

## 10. Minimal Implementation Plan

The safest implementation order is:

### Phase 1 — tighten existing review artifacts
- improve `review_prompt.md`
- improve `review_result_template.md`
- make the machine section more explicit
- keep ingest compatibility

### Phase 2 — improve daily prompt
- tighten `daily_prompt.md`
- standardize output wording
- reduce ambiguity in generated daily logs

### Phase 3 — optionally introduce daily result template
- add `daily_result_template.md`
- only if it does not complicate the current daily flow too much

---

## 11. Likely Files to Touch

Safe likely touch points:

- `services/daily_prompt_service.py`
- `services/review_prompt_service.py`
- `services/review_template_service.py`
- optionally a new service for `daily_result_template`
- supporting docs such as `USER_GUIDE.md`

Touch only with explicit need:

- parser files in `ingest/`
- only when format compatibility truly requires adjustment

Do not treat frozen modules as the place to solve template-quality problems.

---

## 12. CLI Surface Recommendations

Existing commands should remain valid.

Current commands to preserve:

- `study prepare daily`
- `study prepare review-prompt`
- `study prepare review-template`
- `study run daily`
- `study run review`

Optional future additions:

- `study prepare daily-template`

This should be added only if the daily result template is introduced.

---

## 13. Compatibility Rules

Better templates should preserve the following compatibility expectations:

1. old review result files should remain ingestable where possible
2. existing smoke sample files should remain valid historical references
3. new templates should not require policy/schema changes
4. new templates should not force a rebuild of existing data

If compatibility is threatened, prefer a smaller template upgrade.

---

## 14. Acceptance Criteria

The better templates track should be considered successful when:

1. generated prompt files are clearer and more consistent
2. review result templates make editable vs machine sections obvious
3. ingest reliability does not regress
4. normal daily/review use feels simpler
5. the docs can describe the workflow with fewer warnings and caveats
6. no frozen core behavior needs redesign

---

## 15. Nice-to-Have Enhancements

These are useful, but should not block the first better-templates pass:

- section checklists
- stronger naming hints inside templates
- examples embedded inside prompt files
- clearer status guidance in daily output
- confidence field in review results
- template version header such as `Template Version: Gen2.1-v1`

---

## 16. Risks to Avoid

### Risk A — over-structuring
If templates become too rigid, they may become unpleasant to use and encourage manual drift.

### Risk B — hidden ingest breakage
A “cleaner-looking” template is not automatically safer. Compatibility with current ingest matters more than aesthetics.

### Risk C — scope creep
Better templates should not become a disguised rewrite of the learning engine.

### Risk D — mixed contracts
Do not create multiple competing machine-readable sections for the same workflow.

---

## 17. Recommended Deliverables

The first concrete deliverables for this track should be:

1. `BETTER_TEMPLATES_SPEC.md`
2. revised `daily_prompt.md` generation spec
3. revised `review_prompt.md` generation spec
4. revised `review_result_template.md` generation spec
5. optional `daily_result_template.md` draft
6. small `USER_GUIDE.md` updates if workflow wording changes

---

## 18. Bottom Line

The better templates track is the best first move for Gen2.1 because it:

- improves real usage immediately
- strengthens current documentation
- reduces ingest fragility
- prepares the system for weekly summary and mistake-pattern features
- stays inside the safe stabilization boundary

Implement it as a **workflow and interface upgrade**, not as a core logic rewrite.
