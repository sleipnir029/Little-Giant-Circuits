# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Commit Phase 1 source files [BEFORE PHASE 2 IMPLEMENTATION]

Five modified source files are uncommitted:
- `src/datasets/bracket_match.py`
- `src/datasets/kv_retrieval.py`
- `src/datasets/modular_arith.py`
- `src/training/train.py`
- Phase 1 context files (this finalization pass)

Also decide: add `checkpoints/` and `runs/` to `.gitignore` (strongly recommended —
checkpoint artifacts are large binary files and belong outside a source repo).

### 2. Request Phase 2 planning / implementation prompt

Phase 1 is COMPLETE. When ready: ask for the Phase 2 planning and implementation prompt.
The session should open by resolving Q5 (tracing framework) and Q9 (activation cache format)
before any code is written.

---

## Completed

- [x] Phase 0 — COMPLETE (Opus verified 12/12, 2026-04-21)
- [x] Q1 resolved: pip + venv (2026-04-21)
- [x] Q2 decided: CPU-only PyTorch for Phase 2 bridge (2026-04-21)
- [x] Q3 resolved: Python 3.12 in practice, requires-python >= 3.11 (2026-04-21)
- [x] Q7 resolved: `little-giant-circuits` is canonical (Phase 0)
- [x] Q8 resolved: Phase 1 opener (ruff + pyright, no CI) (2026-04-21)
- [x] README.md repo-tree fixed (2026-04-21)
- [x] Tooling: pyproject.toml, requirements.txt, ruff.toml, pyrightconfig.json (2026-04-21)
- [x] src/models/transformer.py — from-scratch MLX transformer (2026-04-21)
- [x] src/utils/config.py + src/utils/checkpoint.py (2026-04-21)
- [x] src/training/loop.py + src/training/train.py (2026-04-21)
- [x] All 6 dataset modules with generator + evaluator + SAMPLE_DATA (2026-04-21)
- [x] All 6 tasks trained; 5/6 above 90% primary metric; bracket_match capacity limit documented (2026-04-21)
- [x] Checkpoint round-trip verified (2026-04-21)
- [x] Phase 1 exit criteria (§10.7) all green — self-declared complete (§12 waived, see review_notes.md §15)
- [x] Phase 1 finalization pass — Phase 2 activation rescinded; §12 waiver formalized (2026-04-21)
- [x] Phase 1 COMPLETE — user confirmed closure; §12 waived (2026-04-21)
- [x] docs/phases/phase_0.md created (Phase 0 history extracted from current_phase.md) (2026-04-21)
