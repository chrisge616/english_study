# GEN2.1 PLAN — Stabilization-First Upgrades for English Study System

This document defines the recommended **Gen2.1** upgrade path for the current repository baseline.

It is intentionally constrained.

Gen2.1 is **not** a new core generation.
It is a small, practical upgrade layer on top of the current frozen Gen2 Core v0.1.

The goal is to improve:

- visibility
- usability
- reporting quality
- operator confidence

without reopening the frozen core logic.

---

## 1. Why Gen2.1 Exists

Gen2 Core already has the essential loop:

- daily ingest
- review ingest
- centralized state update policy
- due-based scheduler
- state inspection
- generated prompts/templates

That means the current bottleneck is no longer “can the system run?”

The current bottleneck is:

- limited operational visibility
- limited mistake reporting
- templates that still rely on careful manual handling
- a gap between internal state and user-facing summaries

Gen2.1 should solve these practical issues **without changing the frozen learning engine**.

---

## 2. Gen2.1 Design Rule

### Main rule

**Do not redesign the core. Add a thin operational layer around it.**

### Frozen modules that should remain untouched by default

- `domain/policy.py`
- `domain/scheduler.py`
- `services/ingest_service.py`
- `storage/session_repo.py`

### Allowed upgrade surface

Gen2.1 should mainly work through:

- new services
- new read-side repository helpers
- new CLI subcommands
- new output markdown files
- small parser/template improvements that do not alter frozen behavior
- optional new storage tables or columns only when clearly justified

---

## 3. Gen2.1 Scope

Gen2.1 should focus on exactly three upgrade tracks:

1. `weekly summary`
2. `mistake pattern tracking`
3. `better templates`

This is the correct scope because all three:

- directly improve daily usage
- increase visibility into the current state
- do not require redesigning the core review policy
- do not require changing scheduler semantics
- can reuse the current database and services

---

## 4. Current Repository Facts That Matter

These facts shape the Gen2.1 design:

### 4.1 Existing formal CLI

The current formal entrypoint is already in place:

- `study init-db`
- `study ingest daily <file>`
- `study ingest review <file>`
- `study inspect state`
- `study inspect word <word>`
- `study prepare daily`
- `study prepare review`
- `study prepare review-prompt`
- `study prepare review-template`
- `study run daily`
- `study run review`

### 4.2 Existing read-side inspection ability

The project already has:

- `build_state_inspection_text()`
- `build_word_inspection_text()`
- access to `evidence`, `session_items`, and `mistake_patterns`

This means Gen2.1 can be built by extending the **reporting layer**, not by replacing the state engine.

### 4.3 Existing schema hook for mistake patterns

The schema already includes:

- `mistake_patterns`

This is important.

It means Gen2.1 does **not** need to invent the idea of mistake tracking from scratch. It only needs to operationalize it.

### 4.4 Existing template generation services

The project already has:

- `daily_prompt_service.py`
- `review_prompt_service.py`
- `review_template_service.py`

This makes “better templates” a natural Gen2.1 track.

---

## 5. Goals and Non-Goals

## 5.1 Goals

Gen2.1 should:

- make current learning state easier to interpret
- expose weekly learning movement
- expose recurring mistake patterns
- reduce template-related operator mistakes
- preserve the current frozen behavior as the source of truth

## 5.2 Non-Goals

Gen2.1 should **not** try to:

- redesign status transitions
- redesign scheduler priorities
- rebuild the ingest engine
- introduce a full learner model
- implement a skill graph
- convert Gen2 into Gen3 early

If a proposed change requires touching frozen learning logic, it is probably outside Gen2.1.

---

## 6. Track A — Weekly Summary

## 6.1 Problem

Right now the system can inspect current state and individual words, but it does not yet produce a concise operational summary of what happened over a learning period.

This makes it harder to answer practical questions such as:

- what changed this week?
- which words improved?
- which words got stuck?
- which review outcomes dominated?
- where is effort being spent?

## 6.2 Gen2.1 objective

Add a weekly reporting layer that turns current DB records into a simple markdown summary.

## 6.3 Minimum viable output

Recommended file:

- `output/weekly_summary.md`

Recommended sections:

1. week range
2. total sessions
3. daily sessions count
4. review sessions count
5. new words introduced
6. review result counts
   - correct
   - partial
   - wrong
7. current status distribution
   - NEW
   - WEAK
   - STABLE
   - STRONG
   - ARCHIVED
8. words that improved this week
9. words repeatedly wrong or partial
10. due / risky words worth attention next week

## 6.4 Minimal CLI surface

Recommended commands:

```powershell
study prepare weekly-summary
study run weekly-summary
```

Alternative acceptable naming:

```powershell
study prepare weekly
study run weekly
```

The first naming is clearer.

## 6.5 Likely implementation shape

Recommended new pieces:

- `services/weekly_summary_service.py`
- small read helpers in `storage/` if needed

Prefer read-only queries against:

- `sessions`
- `session_items`
- `word_state`
- `words`
- `evidence`

## 6.6 What not to do

Do not add new scheduler logic just to generate the weekly summary.

Do not re-interpret the learning policy.

The weekly summary should **report** state, not redefine it.

## 6.7 Acceptance criteria

A weekly summary feature is good enough when:

- it can be generated from current DB state with one CLI command
- it gives a human-readable weekly snapshot
- it surfaces repeated trouble spots without changing state
- it uses existing data, not ad hoc manual notes

---

## 7. Track B — Mistake Pattern Tracking

## 7.1 Problem

The schema already has a `mistake_patterns` table, and review workflows already ask for “Pattern Mistakes”, but the current system does not fully turn those patterns into a stable reporting or inspection layer.

Right now there is partial structure, but not a completed operating feature.

## 7.2 Gen2.1 objective

Turn “pattern mistakes” from a loose review note into a usable system feature.

## 7.3 Recommended operating idea

Start with a deliberately small taxonomy.

Recommended initial pattern types:

- `meaning_confusion`
- `usage_confusion`
- `register_or_nuance`
- `form_or_spelling`
- `retrieval_failure`
- `false_familiarity`

This is intentionally small.

The goal is not linguistic perfection. The goal is a useful first reporting layer.

## 7.4 Minimum viable behavior

When a review log includes pattern notes, the system should be able to:

- associate one or more pattern types with affected words
- increment pattern counts
- keep `last_seen_at`
- expose the result in `inspect word`
- optionally expose top patterns in weekly summary

## 7.5 Recommended implementation path

Prefer a **thin new helper layer** over reworking ingest core.

Recommended path:

1. parse pattern notes more explicitly from review logs
2. add a small repository helper such as:
   - `storage/mistake_pattern_repo.py`
3. add a lightweight service for post-review pattern recording, for example:
   - `services/mistake_pattern_service.py`
4. call that thin layer from the non-frozen edge if possible

If needed, a very small change in the review-side processing path may be acceptable, but the default intention should still be:

- preserve `services/ingest_service.py` as the frozen backbone
- add pattern tracking around it, not through a redesign of it

## 7.6 Recommended CLI surface

At minimum, existing `inspect word` should surface patterns clearly.

Optional Gen2.1 additions:

```powershell
study inspect patterns
study inspect patterns --top 20
```

This is useful, but not required for the first pass.

## 7.7 Acceptance criteria

Mistake pattern tracking is good enough when:

- repeated pattern types accumulate over time
- `inspect word` can show pattern counts clearly
- weekly summary can mention top patterns
- the feature works without changing frozen policy behavior

---

## 8. Track C — Better Templates

## 8.1 Problem

The current templates work, but they still require care from the operator.

Current risks include:

- breaking the review machine block
- unclear result entry
- weak guidance on how to classify `correct / partial / wrong`
- missing daily result standardization

## 8.2 Gen2.1 objective

Make daily and review templates easier to fill correctly and harder to break.

## 8.3 Minimum viable improvements

### Review template improvements

Recommended upgrades:

- clearer instructions near the machine block
- explicit allowed values for `result`
- short examples for `correct`, `partial`, `wrong`
- optional per-word notes field in the human section
- clearer warning not to delete the machine block

### Review prompt improvements

Recommended upgrades:

- clearer instructions for how the final markdown should map to the template
- explicit mention that final status classification must stay concise and machine-friendly
- tighter wording around “Pattern Mistakes” output

### Daily prompt improvements

Recommended upgrades:

- more explicit distinction between vocabulary, mistakes, concepts
- clearer guidance on suggested status use
- optional machine-readable fields for mistake tagging

## 8.4 Nice-to-have but not first-pass

These are useful but should not block Gen2.1:

- clipboard helpers for copying prompts
- daily result template symmetry
- auto-filled examples in template outputs
- stricter parser validation with richer error messages

## 8.5 Recommended implementation path

This track fits naturally into:

- `services/daily_prompt_service.py`
- `services/review_prompt_service.py`
- `services/review_template_service.py`
- optional parser-side validation helpers in `ingest/`

This makes it a strong Gen2.1 candidate because it improves usability without reopening the core state engine.

## 8.6 Acceptance criteria

Template improvements are good enough when:

- fewer manual formatting mistakes happen
- result values are easier to enter consistently
- review logs are easier to ingest reliably
- templates remain simple enough for daily use

---

## 9. Recommended Implementation Order

The best order is:

### Phase 1 — Better Templates

Why first:

- lowest risk
- highest immediate usability gain
- directly improves daily operation
- reduces future ingest friction

### Phase 2 — Weekly Summary

Why second:

- read-only feature
- low risk to core behavior
- increases operator visibility
- gives immediate value from existing data

### Phase 3 — Mistake Pattern Tracking

Why third:

- highest ambiguity among the three
- needs taxonomy decisions
- may need thin new read/write helpers
- should build on clearer templates first

This order minimizes risk while still producing visible progress.

---

## 10. Recommended File and Module Additions

A reasonable Gen2.1 layout would be:

```text
services/
  weekly_summary_service.py
  mistake_pattern_service.py

storage/
  mistake_pattern_repo.py
  summary_repo.py        # optional

tests/
  test_weekly_summary.py
  test_mistake_patterns.py
  test_templates_gen2_1.py
```

And CLI additions inside `app/cli.py`:

- `study prepare weekly-summary`
- `study run weekly-summary`
- optional `study inspect patterns`

This keeps Gen2.1 as an additive layer instead of a rewrite.

---

## 11. Data Model Guidance

Gen2.1 should prefer **reusing existing tables first**.

### Use existing data before adding schema

Existing useful tables:

- `sessions`
- `session_items`
- `evidence`
- `word_state`
- `mistake_patterns`

### Add schema only if clearly justified

Acceptable additions might include:

- a normalized pattern note payload helper table
- optional summary snapshot table for caching

But the default preference should be:

- derive summaries from current data
- avoid schema sprawl during Gen2 stabilization

---

## 12. Risks and Mitigations

## 12.1 Risk — Scope drift into core redesign

Mitigation:

- treat the freeze boundary as real
- reject changes that require rewriting policy/scheduler

## 12.2 Risk — Overcomplicated mistake taxonomy

Mitigation:

- start with a small pattern type set
- optimize for usefulness, not theory completeness

## 12.3 Risk — Reporting logic becomes too coupled to templates

Mitigation:

- keep reporting derived from DB state whenever possible
- do not make weekly reporting depend on fragile markdown parsing alone

## 12.4 Risk — Template improvements accidentally break ingest

Mitigation:

- preserve the existing machine block format unless explicitly versioned
- validate with smoke rebuild after template changes

---

## 13. Definition of Done for Gen2.1

Gen2.1 should be treated as complete when all of the following are true:

1. a weekly summary markdown file can be generated from current DB state
2. repeated mistake patterns can accumulate and be inspected
3. daily/review templates are materially clearer and safer to use
4. smoke rebuild still passes after the changes
5. frozen core modules remain behaviorally unchanged
6. documentation is updated to reflect the new commands and outputs

---

## 14. What Should Happen After Gen2.1

Only after Gen2.1 is stable should the project move toward the first Gen3 design layer.

The most sensible Gen3 entry remains:

- skill graph v0
- thin learner model
- lightweight diagnostics layer

That is a separate step.

Gen2.1 should not be stretched into early Gen3.

---

## 15. Bottom Line

Gen2.1 should be a **small, additive, stabilization-friendly upgrade**.

The best path is:

1. improve templates
2. add weekly summary
3. operationalize mistake pattern tracking

This produces the highest practical value while preserving the current frozen Gen2 baseline.
