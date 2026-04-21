# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Visual inspection of Phase 3 app

Run the app and visually verify key views:

```bash
source .venv/bin/activate
streamlit run app/streamlit_app.py
```

Check:
- Induction task, Attention view, Layer 0 Heads 1-3: offset diagonal expected
- Induction task, Logit Evolution: induction positions (second half) should light up early
- Sorting task, Logit Evolution: output positions should show near-100% confidence
- Bracket match, Logit Evolution: partial confidence expected (~68% overall accuracy)

### 2. Commit Phase 3 source files

Files added/modified in Phase 3:
- `src/viz/__init__.py`, `src/viz/loading.py`, `src/viz/plotting.py` — new module
- `app/streamlit_app.py` — new entry point
- `app/views/` — all 6 view files
- `scripts/generate_demo_traces.py` — new utility
- `docs/phases/phase_3.md` — phase writeup
- `docs/phase_context/` — all context files updated
- `requirements.txt` — streamlit + plotly added

Add `traces/` to `.gitignore` if not already there (trace artifacts are large).

### 3. Request Phase 4 planning / implementation prompt

Phase 3 is COMPLETE. When ready: ask for the Phase 4 planning and implementation prompt.

Phase 4 will build on Phase 3's views by adding:
- Zero ablation (zero out a head/neuron and re-run)
- Mean ablation (replace with dataset mean activation)
- Activation patching (patch clean run activation into corrupted run)
- Before/after comparison UI (reuse `app/views/comparison.py`)

Key question for Phase 4 planning: does MLX support clean intervention without
re-running the full forward pass, or does each ablation require a separate trace call?
This determines the architecture of the intervention runner.

---

## Completed

- [x] Phase 0 — COMPLETE (Opus verified 12/12, 2026-04-21)
- [x] Phase 1 — COMPLETE (§12 waived, all 6 tasks trained, 2026-04-21)
- [x] Phase 2 — COMPLETE (tracing foundation, anti-drift + round-trip verified, 2026-04-21)
- [x] Phase 3 — COMPLETE (Streamlit app, 6 views, demo traces for all tasks, 2026-04-21)
- [x] Q1 resolved: pip + venv (2026-04-21)
- [x] Q2 decided: CPU-only PyTorch for Phase 4 bridge if needed (2026-04-21)
- [x] Q3 resolved: Python 3.12 in practice (2026-04-21)
- [x] Q5 resolved: `return_cache` flag, MLX-native, no PyTorch bridge (2026-04-21)
- [x] Q6 resolved: Streamlit committed for Phase 3; fallback noted if Phase 5/6 traces grow large (2026-04-21)
- [x] Q7 resolved: `little-giant-circuits` canonical (Phase 0)
- [x] Q8 resolved: Phase 1 opener (ruff + pyright) (2026-04-21)
- [x] Q9 resolved: safetensors + meta JSON, TransformerLens naming (2026-04-21)
