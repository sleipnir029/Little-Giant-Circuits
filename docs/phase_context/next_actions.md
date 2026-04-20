# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Commit Phase 1 implementation files [NEXT]

Stage and commit all Phase 1 work:
- `README.md`, `pyproject.toml`, `requirements.txt`, `ruff.toml`, `pyrightconfig.json`
- `src/` — full source tree (all 6 datasets + transformer + training + utils)
- `docs/phase_context/` — all updated context files
- `docs/phases/phase_1.md` — training results for induction + factual_lookup

Suggested commit message: `feat: Phase 1 complete — transformer, training loop, 6 datasets, 2 tasks trained`

### 2. Opus verification pass for Phase 1 [AFTER COMMIT]

All 8 Phase 1 exit criteria now satisfied (see implementation_status.md top entry).
Opus reads `implementation_status.md` and `docs/phases/phase_1.md` and independently
verifies all 8 exit criteria from `review_notes.md §10.7`. Write result into
`review_notes.md §12`.

---

## Completed

- [x] Phase 0 — COMPLETE (Opus verified 12/12, 2026-04-21)
- [x] Q1, Q3, Q8 resolved by Opus Phase 1 advisory (2026-04-21)
- [x] Q3 updated for Python 3.12 reality (MLX 0.31.1 confirmed compatible, 2026-04-21)
- [x] `README.md` repo-tree — fixed (CLAUDE_BOOTSTRAP.md at root; added WORKFLOW.md, ENVIRONMENT.md, proposals/, Phase 1 files) (2026-04-21)
- [x] Tooling: `pyproject.toml`, `requirements.txt`, `ruff.toml`, `pyrightconfig.json` (2026-04-21)
- [x] `src/models/transformer.py` — from-scratch MLX transformer (2026-04-21)
- [x] `src/utils/config.py` + `src/utils/checkpoint.py` (2026-04-21)
- [x] `src/training/loop.py` + `src/training/train.py` (2026-04-21)
- [x] All 6 dataset modules with generator + evaluator + SAMPLE_DATA (2026-04-21)
- [x] Induction task trained: 100% induction accuracy in 2000 steps (2026-04-21)
- [x] Checkpoint round-trip verified: save → load → re-evaluate → same accuracy (2026-04-21)
- [x] factual_lookup task trained: 100% lookup_acc in 2000 steps (2026-04-21)
- [x] All 8 Phase 1 exit criteria satisfied (2026-04-21)
