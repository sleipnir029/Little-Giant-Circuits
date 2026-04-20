# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Opus verification pass on Phase 0 [NEXT]

Ask Opus to read `docs/phase_context/current_phase.md` exit criteria and check each item. The pass should be independent — Opus should not trust that the implementation is correct, but should read the files and confirm.

If any item fails: Sonnet fixes it, then Opus re-checks that item only.

### 2. Commit all Phase 0 files [after verification]

Once Opus gives the green light:
- Stage all new files in `docs/`
- Write a commit message that references Phase 0 deliverables
- Confirm `git status` is clean

### 3. Update `current_phase.md` to COMPLETE [after commit]

- Change `Status: IN PROGRESS` → `Status: COMPLETE`
- Add `Completed: <date>` field
- This closes Phase 0 formally

### 4. Answer Q1, Q2, Q3, Q8 before Phase 1 kickoff [next planning session]

These four open questions in `open_questions.md` block Phase 1. They should be answered in the Phase 1 planning conversation (with Opus), not implemented speculatively.

### 5. Ask Opus to write Phase 1 review notes [start of Phase 1]

Trigger: human prompts Opus with the Phase 1 advisor role.
Opus should read `PROJECT_PLAN.md §6 Phase 1` and write a new review session into `docs/phase_context/review_notes.md` (overwrite or append clearly — decide then).

---

## Completed

- [x] `docs/phase_context/review_notes.md` — Opus critique written (2026-04-21)
- [x] `docs/phase_context/current_phase.md` — active phase + exit criteria (2026-04-21)
- [x] `docs/phase_context/implementation_status.md` — progress log started (2026-04-21)
- [x] `docs/phase_context/open_questions.md` — seeded with 8 questions (2026-04-21)
- [x] `docs/proposals/` — directory + README created (2026-04-21)
- [x] `docs/ENVIRONMENT.md` — Apple-Silicon scope, Python rec, PM deferred (2026-04-21)
- [x] `docs/WORKFLOW.md` — operational Opus↔Sonnet loop description (2026-04-21)
- [x] `docs/architecture/README.md`, `docs/theory/README.md`, `docs/phases/README.md` — stubs created (2026-04-21)
- [x] `README.md` repo-tree — corrected `glassbox-playground/` → `little-giant-circuits/` (2026-04-21)
