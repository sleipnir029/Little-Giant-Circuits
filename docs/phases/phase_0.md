# Phase 0 — Foundation and Constraints

> This file reflects what actually happened, not what was planned.

---

## Overview

**Phase number:** 0
**Phase name:** Foundation and constraints
**Status:** COMPLETE
**Started:** 2026-04-21
**Completed:** 2026-04-21
**Verification:** Opus independent pass — 12/12 criteria PASS (see `review_notes.md §2`)

---

## What Phase 0 Was

Phase 0 installed the rules of the game before any model code was written. Its sole purpose
was to make Phase 1 safe to start. No user-runnable code shipped in Phase 0.

The deliverable was a repository that a new contributor — or a fresh model session with no
chat history — could read in 10 minutes and understand:
- what this project is for,
- what is in scope and out of scope,
- how drift is prevented,
- and how to pick up where the last session left off.

---

## Exit Criteria (all verified by Opus)

- [x] All five `docs/phase_context/*.md` files exist and are non-empty
- [x] `docs/proposals/` exists with its README and `.gitkeep`
- [x] `LICENSE` present and is unmodified Apache-2.0
- [x] `docs/ENVIRONMENT.md` present; declares Apple-Silicon scope; defers package-manager choice
- [x] `docs/WORKFLOW.md` present; describes the Opus↔Sonnet file-based loop operationally
- [x] `docs/architecture/README.md`, `docs/theory/README.md`, `docs/phases/README.md` each exist
- [x] No file exists under `src/`
- [x] No dependency manifest exists at the repo root
- [x] No Streamlit app file exists
- [x] `README.md` repo-tree matches the actual repository name (`little-giant-circuits`)
- [x] `git status` is clean; all Phase 0 changes are committed
- [x] A fresh reader of `CLAUDE.md` + this file can state in one paragraph what Phase 1 will
      and will not do

---

## What Was Built

- `docs/phase_context/review_notes.md` — Opus Phase 0 critique with risks and implementation guidance
- `docs/phase_context/current_phase.md` — active phase declaration + exit criteria checklist
- `docs/phase_context/implementation_status.md` — append-only progress log
- `docs/phase_context/open_questions.md` — 8 seeded unresolved decisions
- `docs/phase_context/next_actions.md` — ordered next-step queue
- `docs/proposals/README.md` and `docs/proposals/.gitkeep` — proposal infrastructure
- `docs/ENVIRONMENT.md` — Apple-Silicon scope statement
- `docs/WORKFLOW.md` — operational description of the Opus↔Sonnet file-based loop
- `docs/architecture/README.md`, `docs/theory/README.md`, `docs/phases/README.md` — stub purpose stmts
- `docs/phases/TEMPLATE.md` — reusable phase documentation template
- `README.md` — repo-tree root name corrected (`glassbox-playground/` → `little-giant-circuits/`)

---

## Key Decisions Made

1. **No `src/` scaffolded in Phase 0** — deferred entirely to Phase 1 per Opus review risk R1.
2. **No dependency manifest** — deferred to Phase 1.
3. **Package manager deferred** — answered in Phase 1 (pip + venv, see Q1 in `open_questions.md`).
4. **`phase_1.md` only created, not phase_2 through phase_8** — doc inflation risk (Opus R3);
   future phase docs created when phases are entered.
5. **Template added** — `docs/phases/TEMPLATE.md` prevents future phases from inventing format.

---

## Open Questions Seeded (see `open_questions.md` for resolutions)

- Q1 Package manager — RESOLVED in Phase 1
- Q2 PyTorch device target — DECIDED in Phase 1
- Q3 Python version floor — RESOLVED in Phase 1
- Q4 Checkpoint format — OPEN (blocks Phase 5)
- Q5 Tracing framework — OPEN (blocks Phase 2)
- Q6 Streamlit suitability — OPEN (informs Phase 3)
- Q7 Repo-name consistency — RESOLVED in Phase 0
- Q8 Phase 0.5 tooling — RESOLVED in Phase 1
