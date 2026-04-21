# Current Phase

## Active Phase
Phase 3 — Visualization and Inspection UI

**Status:** COMPLETE
**Started:** 2026-04-21
**Completed:** 2026-04-21
**Note:** Phase 2 closed complete (2026-04-21). All 29 trace tensors verified.
          Phase 3 activated here.

---

## Phase 3 Objective

Build a clean, lightweight Streamlit interface for inspecting activation traces from the
tiny trained MLX transformer. A learner should be able to load any task's checkpoint,
run or load a trace, and see exactly what the model computed — attention patterns,
residual stream norms, MLP activations, and logit evolution — without prior setup.

Understanding is the deliverable. The UI serves interpretability, not production use.

---

## Phase 3 Exit Criteria

- [ ] `streamlit run app/streamlit_app.py` starts without errors
- [ ] Six views render cleanly: Token Overview, Layer Overview, Attention,
      MLP Activations, Logit Evolution, Compare Traces
- [ ] Induction demo trace loads and all views display correctly
- [ ] "Run demo prompt" path generates a fresh trace and views update
- [ ] Comparison mode renders two traces side-by-side
- [ ] `scripts/generate_demo_traces.py` generates traces for all 6 tasks
- [ ] `streamlit` and `plotly` added to `requirements.txt`
- [ ] `src/viz/` contains no streamlit imports (pure plotly helpers only)
- [ ] `docs/phases/phase_3.md` written and accurate
- [ ] Q6 marked RESOLVED in `open_questions.md`

---

## Phase 3 In-Scope

- `src/viz/loading.py` — pure helpers: list checkpoints/traces, load model, run trace
- `src/viz/plotting.py` — pure plotly figure functions (no streamlit imports)
- `app/streamlit_app.py` — main Streamlit entry point with sidebar navigation
- `app/views/` — one view file per visualization (streamlit wiring only)
- `scripts/generate_demo_traces.py` — batch trace generation for all 6 tasks
- `docs/phases/phase_3.md` — phase writeup
- Context file updates: `implementation_status.md`, `next_actions.md`, `open_questions.md`

---

## Phase 3 Out-of-Scope

- Ablation controls or patching UI (Phase 4)
- Checkpoint comparison across training steps (Phase 5)
- SAE feature browser (Phase 6)
- Interactive weight editing (Phase 7)
- PyTorch bridge (not needed for Phase 3)
- Pretrained model work (Phase 8)
- New training code or dataset changes

---

## Predecessor State

Phase 2 COMPLETE (2026-04-21). All 6 task checkpoints exist under `checkpoints/`.
One saved demo trace: `traces/induction/demo/`. ActivationCache with 29 tensors, dot-key
access, safetensors on-disk format. `scripts/trace_prompt.py` runs end-to-end.

---

## How to Use This File

- Update Status when phase transitions: `IN PROGRESS` → `COMPLETE`.
- Do not use this file as a scratch pad. Progress goes in `implementation_status.md`.
- Unresolved decisions go in `open_questions.md`.
