# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Commit Phase 2 source files

Files added/modified in Phase 2:
- `src/models/transformer.py` — `return_cache` flag added
- `src/tracing/__init__.py`, `cache.py`, `tracer.py`, `export.py` — new module
- `scripts/trace_prompt.py` — new CLI demo script
- `docs/phases/phase_2.md` — phase writeup
- `docs/phase_context/` — all context files updated
- `docs/phase_context/review_notes.md` — §16 Phase 2 advisory added

Add `traces/` to `.gitignore` (trace artifacts are large and task-specific; not source).

### 2. Request Phase 3 planning / implementation prompt

Phase 2 is COMPLETE. When ready: ask for the Phase 3 planning and implementation prompt.
The session should open by resolving Q6 (Streamlit suitability — consider a quick spike
before committing to Streamlit-first Phase 3 design).

Phase 3 will consume `ActivationCache` directly via the dot-key accessor. Key views to build:
- Attention heatmap browser (`blocks.{i}.attn.pattern`)
- Layerwise residual stream view
- MLP neuron activation explorer
- Logit evolution across layers

---

## Completed

- [x] Phase 0 — COMPLETE (Opus verified 12/12, 2026-04-21)
- [x] Phase 1 — COMPLETE (§12 waived, all 6 tasks trained, 2026-04-21)
- [x] Phase 2 — COMPLETE (tracing foundation, anti-drift + round-trip verified, 2026-04-21)
- [x] Q1 resolved: pip + venv (2026-04-21)
- [x] Q2 decided: CPU-only PyTorch for Phase 4 bridge if needed (2026-04-21)
- [x] Q3 resolved: Python 3.12 in practice (2026-04-21)
- [x] Q5 resolved: `return_cache` flag, MLX-native, no PyTorch bridge (2026-04-21)
- [x] Q7 resolved: `little-giant-circuits` canonical (Phase 0)
- [x] Q8 resolved: Phase 1 opener (ruff + pyright) (2026-04-21)
- [x] Q9 resolved: safetensors + meta JSON, TransformerLens naming (2026-04-21)
