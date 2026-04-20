# Current Phase: Phase 0 — Foundation and Constraints

**Status:** IN PROGRESS
**Started:** 2026-04-21
**Target completion:** Phase 0 exit criteria all green (see checklist below)

---

## What Phase 0 Is

Phase 0 installs the **rules of the game** before any model code is written. Its sole purpose is to make Phase 1 safe to start. No user-runnable code ships in Phase 0.

The deliverable is a repository that a new contributor — or a fresh model session with no chat history — can read in 10 minutes and understand:
- what this project is for,
- what is in scope and out of scope,
- how drift is prevented,
- and how to pick up where the last session left off.

---

## Phase 0 Exit Criteria

This is the acceptance gate. All items must be green before Phase 1 begins.

- [ ] All five `docs/phase_context/*.md` files exist and are non-empty
- [ ] `docs/proposals/` exists with its README and `.gitkeep`
- [ ] `LICENSE` present and is unmodified Apache-2.0 ✅ (already done)
- [ ] `docs/ENVIRONMENT.md` present; declares Apple-Silicon scope; defers package-manager choice
- [ ] `docs/WORKFLOW.md` present; describes the Opus↔Sonnet file-based loop operationally
- [ ] `docs/architecture/README.md`, `docs/theory/README.md`, `docs/phases/README.md` each exist
- [ ] No file exists under `src/`
- [ ] No dependency manifest exists at the repo root
- [ ] No Streamlit app file exists
- [ ] `README.md` repo-tree matches the actual repository name (`little-giant-circuits`)
- [ ] `git status` is clean; all Phase 0 changes are committed
- [ ] A fresh reader of `CLAUDE.md` + this file can state in one paragraph what Phase 1 will and will not do

---

## Next Phase

**Phase 1 — Tiny transformer training** (not yet started)

Phase 1 trains tiny transformers from scratch on six synthetic tasks. It introduces `src/`, a dependency manifest, and the training loop. It does not begin until this phase's checklist is complete and Opus has done an independent verification pass.

---

## How to Use This File

- Update `Status` field when this phase is complete: change `IN PROGRESS` → `COMPLETE`.
- Add a `Completed:` date field below `Started:`.
- Copy exit criteria with all boxes checked into `implementation_status.md` as the final entry.
- Then update this file to reflect Phase 1 as the active phase.

Do not use this file as a scratch pad. It is a pointer, not a log.
