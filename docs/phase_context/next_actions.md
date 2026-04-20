# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Commit Phase 0 closure files [NEXT]

Stage and commit the following:
- `docs/phase_context/review_notes.md` — §10 verification appendix (Opus, 2026-04-21)
- `docs/phase_context/current_phase.md` — status updated to COMPLETE, all checkboxes checked
- `docs/phases/TEMPLATE.md` — reusable phase doc template
- `docs/phases/phase_1.md` — Phase 1 placeholder
- `docs/phase_context/implementation_status.md` — closure entry appended
- `docs/phase_context/next_actions.md` — this update

Suggested commit message: `docs: close Phase 0 — add verification pass, phase template, Phase 1 placeholder`

### 2. Answer Q1, Q2, Q3, Q8 with Opus [Phase 1 planning session]

These four open questions block Phase 1 start. Resolve them in the next Opus planning session before any code is written.
- Q1: package manager (uv / poetry / pip + venv)
- Q2: PyTorch device target (MPS / CPU-only / both)
- Q3: Python version floor (3.11 / 3.12)
- Q8: Phase 0.5 tooling decision (separate phase or Phase 1 opener)

### 3. Opus writes Phase 1 review notes [start of Phase 1]

Trigger: human prompts Opus with the Phase 1 advisor role.
Opus reads `PROJECT_PLAN.md §6 Phase 1` and appends a clearly-labeled Phase 1 section to `docs/phase_context/review_notes.md`.
Then update `docs/phase_context/current_phase.md` to reflect Phase 1 as active.

### 4. Fill in `docs/phases/phase_1.md` prerequisites [after Q answers + Opus review]

Once Q1–Q8 decisions are recorded and Opus Phase 1 notes are written, update `docs/phases/phase_1.md`:
- Check off the prerequisites
- Add the chosen package manager, Python version, and tooling decisions

---

## Completed

- [x] `docs/phase_context/review_notes.md` — Opus pre-impl critique written (2026-04-21)
- [x] `docs/phase_context/review_notes.md §10` — Opus verification pass appended, 12/12 PASS (2026-04-21)
- [x] `docs/phase_context/current_phase.md` — active phase + exit criteria (2026-04-21)
- [x] `docs/phase_context/current_phase.md` — status updated to COMPLETE (2026-04-21)
- [x] `docs/phase_context/implementation_status.md` — progress log started (2026-04-21)
- [x] `docs/phase_context/open_questions.md` — seeded with 8 questions (2026-04-21)
- [x] `docs/proposals/` — directory + README created (2026-04-21)
- [x] `docs/ENVIRONMENT.md` — Apple-Silicon scope, Python rec, PM deferred (2026-04-21)
- [x] `docs/WORKFLOW.md` — operational Opus↔Sonnet loop description (2026-04-21)
- [x] `docs/architecture/README.md`, `docs/theory/README.md`, `docs/phases/README.md` — stubs created (2026-04-21)
- [x] `docs/phases/TEMPLATE.md` — reusable phase doc template (2026-04-21)
- [x] `docs/phases/phase_1.md` — Phase 1 placeholder with prerequisites (2026-04-21)
- [x] `README.md` repo-tree — corrected `glassbox-playground/` → `little-giant-circuits/` (2026-04-21)
- [x] Phase 0 — COMPLETE (Opus verified 12/12, 2026-04-21)
