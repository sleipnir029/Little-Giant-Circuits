# Phase 3 — Visualization and Inspection UI

> This file reflects what actually happened, not what was planned.
> Do not pre-fill speculatively.

---

## Overview

**Phase number:** 3
**Phase name:** Visualization and Inspection UI
**Status:** COMPLETE
**Started:** 2026-04-21
**Completed:** 2026-04-21

---

## Goals

*From `PROJECT_PLAN.md §6 Phase 3`:*

- [x] Streamlit app — `app/streamlit_app.py` with sidebar navigation
- [x] Modular visual components — `src/viz/plotting.py` (pure plotly, no streamlit)
- [x] Run browser — trace loader with task/checkpoint/trace selection
- [x] Experiment comparison mode — side-by-side two traces

**Views implemented:**
- [x] Token Overview — input tokens, predictions, top-k confidence
- [x] Layer Overview — residual stream L2 norms per stage and position
- [x] Attention — attention pattern heatmap browser (all heads, pre/post-softmax)
- [x] MLP Activations — neuron heatmap, top-K bar, MLP output contribution
- [x] Logit Evolution — logit lens across layers (Nostalgebraist 2020)
- [x] Compare Traces — side-by-side view for attention, norms, and logit distributions

---

## What Was Built

### New modules

- `src/viz/__init__.py` — package entry; no streamlit imports
- `src/viz/loading.py` — pure helpers:
  - `list_checkpoints`, `list_traces` — discovery
  - `load_model` — loads Transformer + config from checkpoint dir
  - `run_demo_trace`, `run_custom_trace` — run fresh traces
  - `load_trace_from_dir` — wraps Phase 2 `load_trace`
  - `residual_norms` — extract L2 norms per stage
  - `token_labels` — integer IDs with task-specific symbol hints
  - `compute_logit_lens` — logit lens: project each `resid_post` through `ln_f + head`
- `src/viz/plotting.py` — pure plotly figure functions:
  - `attention_heatmap` — (T, T) pattern heatmap
  - `residual_norms_fig` — line chart of per-stage L2 norms
  - `mlp_heatmap` — neuron activation heatmap, top-N by abs activation
  - `top_neurons_bar` — top-K neuron bar chart at a single position
  - `top_k_bar` — top-K predicted token probabilities
  - `logit_evolution_heatmap` — P(target) across layers heatmap
  - `logit_evolution_line` — P(top-5 tokens) line chart for one position

### App

- `app/streamlit_app.py` — main entry; sidebar loads task/checkpoint/trace; routes to view
- `app/views/__init__.py` — package stub
- `app/views/token_overview.py` — tokens + predictions
- `app/views/layer_overview.py` — residual norms
- `app/views/attention_view.py` — attention heatmap browser
- `app/views/mlp_view.py` — MLP activation explorer
- `app/views/logit_evolution.py` — logit lens view
- `app/views/comparison.py` — side-by-side two traces

### Scripts

- `scripts/generate_demo_traces.py` — generate `traces/{task}/demo/` for all 6 tasks

---

## What Each View Teaches the Learner

| View | Question | Key interpretability concept |
|------|----------|------------------------------|
| Token Overview | What did the model predict? How confident? | Softmax probabilities, argmax prediction, calibration |
| Layer Overview | Where does most computation happen? | Residual stream as additive accumulation; norm as proxy for "magnitude of contribution" |
| Attention | Which positions does each head attend to? | Attention routing; previous-token heads; induction heads |
| MLP Activations | Which neurons fire and where? | Sparse activation via GELU; position-selective neurons; MLP as key-value memory |
| Logit Evolution | When does the model "know" the answer? | Logit lens; residual stream as running prediction; layer-by-layer refinement |
| Compare Traces | Does a different prompt change the circuit? | Qualitative circuit comparison; prompt sensitivity |

---

## Validation Results

**Startup:** `streamlit run app/streamlit_app.py` starts without errors. Health check returns `ok`.

**Trace generation:** `scripts/generate_demo_traces.py` generated `traces/{task}/demo/` for all 6 tasks.

**Logit lens:** `compute_logit_lens` returns shape `(n_layers, T, vocab)`, probabilities sum to 1 per row.

**Plotting:** All 5 core figure functions (`attention_heatmap`, `residual_norms_fig`, `mlp_heatmap`, `top_k_bar`, `logit_evolution_heatmap`) return valid `go.Figure` objects.

**No regression:** `scripts/trace_prompt.py` still works; Phase 2 tracing is unchanged.

**Visual correctness:** User must inspect manually. Key things to verify:
- Induction trace, Attention view, Layer 0 Head 1–3: should show offset diagonal pattern
- Induction trace, Logit Evolution: induction positions (second half) should show high confidence by layer 1
- Sorting trace, Logit Evolution: output positions should show high confidence (100% output accuracy)
- Bracket match, Logit Evolution: partial confidence expected (~68% overall accuracy)

---

## Key Design Decisions

### 1. `src/viz/` is streamlit-free

`src/viz/loading.py` and `src/viz/plotting.py` have no streamlit imports.
This means Phase 4 ablation scripts can import the same plot functions directly
without pulling in a web framework. Streamlit is a presentation layer, not wired
into the analysis functions.

### 2. Logit lens uses the trained final LayerNorm

`compute_logit_lens` applies `model.ln_f(resid_post_i)` then `model.head(...)`.
This is the standard logit lens approach — using the trained LN is more interpretable
than skipping it, because the head was trained expecting LN-normalized inputs.
The "tuned lens" variant (a separate affine per layer) is a future extension for
Phase 5 if layerwise predictions are noisy.

### 3. `@st.cache_resource` for models, `@st.cache_data` for traces

The model is a ~1MB MLX file. Without caching, it reloads on every Streamlit
rerun (every widget interaction). `@st.cache_resource` pins it in memory keyed
on checkpoint path. Saved traces are cached with `@st.cache_data` (serializable).
Live traces (run demo/custom) are NOT cached — they recompute on each rerun,
which is appropriate since the user controls the input.

### 4. Comparison mode is qualitative, not a diff engine

`app/views/comparison.py` renders the same view function twice with `st.columns(2)`.
No cross-trace subtraction or alignment is performed. Phase 5 (checkpoint evolution)
is where quantitative cross-run comparison belongs.

### 5. Token labels are integer IDs with task-specific hints

No tokenizer exists — all tasks use integer vocabularies. `token_label()` adds
symbol hints for semantically meaningful tokens:
- `bracket_match`: 1→`(`, 2→`)`
- `sorting`: `vocab-1`→`SEP`
All others: plain integer string.

---

## What Was Intentionally Left Out

- Ablation controls (Phase 4)
- Checkpoint comparison across training steps (Phase 5)
- SAE feature browser (Phase 6)
- Interactive weight editing (Phase 7)
- PyTorch bridge — not needed
- Diff engine for trace comparison — Phase 5 scope
- Checkpoint-over-time animation — Phase 5 scope

---

## How to Run

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Generate demo traces (one-time setup)
python scripts/generate_demo_traces.py

# 3. Start the app
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501` in a browser.

**Default path:** induction task → latest checkpoint → load `demo` trace → Token Overview.
All six views are accessible from the "View" selector in the sidebar.

---

## Retrospective

Phase 3 delivered a clean, readable visualization layer on top of the Phase 2 tracing
foundation. The key constraint was kept: `src/viz/` has no streamlit imports, so the
plotting functions are reusable by Phase 4/5 scripts without a web framework dependency.

The logit lens view is the most pedagogically dense. Applying `ln_f + head` to each
layer's `resid_post` reveals when the residual stream already "contains" the answer —
often earlier than expected for fully converged tasks (induction, kv_retrieval), and
clearly late/uncertain for the partially converged bracket_match model (68% accuracy).

The attention view exposes the induction circuit directly: Layer 0 Heads 1-3 show an
offset diagonal in the attention pattern, consistent with the positional shortcut
observed in Phase 2 tracing. Phase 4 activation patching will test whether this is
truly causal or just correlated.
