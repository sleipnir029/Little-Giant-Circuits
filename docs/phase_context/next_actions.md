# Next Actions

Ordered list of immediate next steps. Remove items as completed.
This is a short-term queue, not a roadmap — keep it under 10 items.

---

## Current Queue

### 1. Commit Phase 3B source files (PRIORITY)

Files added/modified in Phase 3B:
- `src/viz/export_stages.py` — new (core exporter)
- `scripts/export_learn_stages.py` — new (CLI runner)
- `docs/architecture/react_learn_mode.md` — new (design doc)
- `docs/phases/phase_3.md` — Phase 3B section appended
- `docs/phase_context/review_notes.md` — §19 appended
- `docs/phase_context/implementation_status.md` — Phase 3B entry prepended
- `docs/phase_context/current_phase.md` — updated to Phase 3B COMPLETE
- `docs/phase_context/next_actions.md` — this file

Note: `learn_data/` is generated data — add to `.gitignore` or commit intentionally.

### 2. Visual inspection of the Streamlit app (still pending from Phase 3 Refinement)

Run the app and verify BOTH modes still work after Phase 3B changes (no regressions):

```bash
source .venv/bin/activate
streamlit run app/streamlit_app.py
```

**Learn Mode checks:**
- Mode toggle visible at top (Learn Mode / Investigate Mode)
- Default loads to Learn Mode, Step 1: Input Tokens
- "Next →" advances through all 9 stages without error
- "← Previous" correctly goes back
- Each stage shows explanation text + Plotly figure (not blank)
- Step 9 shows the logit lens heatmap

**Investigate Mode checks (must not regress):**
- All 6 views render correctly
- Induction task, Attention view, Layer 0 Heads 1-3: offset diagonal expected

### 3. OPEN QUESTION: Demo trace quality improvement

The induction demo trace (`traces/induction/demo/`) uses a 7-token sequence that
doesn't strongly exhibit the induction circuit at the final stage. The logit lens
shows <1% confidence on the correct next token at position 5.

**Fix:** Regenerate the induction demo trace with a longer sequence (T=16) that
clearly exhibits the pattern. Update `scripts/generate_demo_traces.py` to use
`[A, B, ..., A, B, ..., A, B]` with enough repetitions for the circuit to fire.
Then re-run `python scripts/export_learn_stages.py`.

This is a Python-side fix that requires no React changes.

### 4. Decide: Phase 4 causal interventions

Phase 3B is complete. Two paths forward:

Phase 3C (React Learn Mode) is COMPLETE. Next phase is:

**Phase 4: Causal Interventions (ablation/patching)**
- Zero ablation, mean ablation, activation patching in Streamlit first
- Before/after UI showing intervention effect
- Key question: does MLX support clean intervention without re-running full forward pass?
  (Answer: each ablation requires a separate trace call — MLX is functional/stateless)
- Start with zero-ablation of individual attention heads; verify on induction task

---

## Completed

- [x] Phase 0 — COMPLETE (Opus verified 12/12, 2026-04-21)
- [x] Phase 1 — COMPLETE (§12 waived, all 6 tasks trained, 2026-04-21)
- [x] Phase 2 — COMPLETE (tracing foundation, anti-drift + round-trip verified, 2026-04-21)
- [x] Phase 3 — COMPLETE (Streamlit app, 6 views, demo traces for all tasks, 2026-04-21)
- [x] Phase 3 Refinement — COMPLETE (Streamlit Learn Mode, 9 stages, playback, 2026-04-21)
- [x] Phase 3B — COMPLETE (React data bridge, export pipeline, JSON contract, 2026-04-21)
- [x] Phase 3C — COMPLETE (React Learn Mode UI, all 6 viz kinds, browser-verified, 2026-04-21)
- [x] Q1 resolved: pip + venv (2026-04-21)
- [x] Q2 decided: CPU-only PyTorch for Phase 4 bridge if needed (2026-04-21)
- [x] Q3 resolved: Python 3.12 in practice (2026-04-21)
- [x] Q5 resolved: `return_cache` flag, MLX-native, no PyTorch bridge (2026-04-21)
- [x] Q6 resolved: Streamlit committed for Phase 3; React bridge added in Phase 3B (2026-04-21)
- [x] Q7 resolved: `little-giant-circuits` canonical (Phase 0)
- [x] Q8 resolved: Phase 1 opener (ruff + pyright) (2026-04-21)
- [x] Q9 resolved: safetensors + meta JSON, TransformerLens naming (2026-04-21)
