# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Visual inspection of the refined app (PRIORITY)

Run the app and verify BOTH modes:

```bash
source .venv/bin/activate
streamlit run app/streamlit_app.py
```

**Learn Mode checks:**
- Mode toggle visible at top (Learn Mode / Investigate Mode)
- Default loads to Learn Mode, Step 1: Input Tokens
- "Next →" advances through all 9 stages without error
- "← Previous" correctly goes back
- Quick-jump selectbox jumps to any stage
- Each stage shows: explanation text, what changed, what to notice
- Each stage shows a Plotly figure (not blank)
- "Investigate Mode → [view name]" cross-link visible at each stage
- Step 9 shows the logit lens heatmap with actual next targets highlighted

**Investigate Mode checks (existing, must not regress):**
- All 6 views render correctly
- Induction task, Attention view, Layer 0 Heads 1-3: offset diagonal expected
- Induction task, Logit Evolution: induction positions (second half) light up early

### 2. Commit Phase 3 Refinement source files

Files added/modified in Phase 3 Refinement:
- `src/viz/stages.py` — new
- `src/viz/playback.py` — new
- `app/learn/__init__.py` — new
- `app/learn/learn_mode.py` — new
- `app/streamlit_app.py` — updated (mode toggle + Learn Mode routing)
- `docs/phases/phase_3.md` — refinement section appended
- `docs/phase_context/` — all context files updated

### 3. Request Phase 4 planning / implementation prompt

Phase 3 Refinement is complete when visual inspection passes.
Phase 4 adds causal interventions: zero/mean ablation, activation patching, before/after UI.

Key question for Phase 4 planning: does MLX support clean intervention without
re-running the full forward pass, or does each ablation require a separate trace call?

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
