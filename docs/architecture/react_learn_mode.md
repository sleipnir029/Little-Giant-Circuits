# React Learn Mode — Architecture Design

**Status:** APPROVED (Phase 3B implementation)
**Date:** 2026-04-21
**Author:** Sonnet (Phase 3B implementation advisory)

---

## 1. Problem Statement

The Streamlit Learn Mode (Phase 3 Refinement) walks a learner through a transformer forward
pass using `go.Figure` objects rendered via `st.plotly_chart()`. This works within a single
Python process but cannot be consumed by a React frontend because:

1. `go.Figure` objects are Python runtime objects — not serializable to a clean React data contract
2. `fig.to_dict()` produces a Plotly **renderer spec** (~100KB per stage), not semantic data
3. React would need `plotly.js` to render specs, making the migration pointless
4. Raw safetensors parsing in React is infeasible (binary format, requires numpy-style ops)

The goal of Phase 3B is to define and implement a clean **data bridge** between Python (where
all computation happens) and React (where Learn Mode rendering will happen).

---

## 2. Options Considered

### Option A: Plotly spec serialization (`fig.to_dict()`)

Export each stage's `go.Figure` as a JSON Plotly spec.

**Pros:** Trivial to generate (one call per figure), preserves all existing plot styling.

**Cons:**
- Couples React to Plotly.js rendering model
- Produces 50–200KB per stage for tiny tensors (axes, traces, layout config overhead)
- React cannot programmatically highlight specific cells (e.g., induction diagonal) without re-parsing the spec
- Violates the user's explicit constraint: "do not serialize Python Plotly figure objects as the final contract"

**Verdict:** Rejected.

### Option B: Live Python API server

Run a Flask/FastAPI server that React calls to get stage data on demand.

**Pros:** Always fresh data, no pre-generation step.

**Cons:**
- Requires running a server process alongside the React app
- Adds latency on every stage transition
- Overkill for a static educational tool with infrequently-changing traces
- "Do not over-engineer a backend" constraint

**Verdict:** Rejected.

### Option C: Static JSON export with semantic array contract (CHOSEN)

Python pre-generates `learn_data/{task}/{trace_id}.json` files. React reads at load time.
Each stage carries raw numeric arrays with a `viz.kind` discriminant.

**Pros:**
- No server required — fully static, can be served from any web host
- Semantic arrays let React render flexibly (custom highlights, animations, tooltips)
- Regeneration is explicit and intentional (matches project's static-file discipline)
- React components are simple: receive arrays, render chart

**Cons:**
- JSON files must be regenerated when traces change (one CLI command)
- Slightly larger file size than binary (acceptable: induction demo ≈ 80KB total)

**Verdict:** Chosen.

---

## 3. Recommended Architecture

```
Python side                          React side
─────────────────────────────────    ──────────────────────────────────
src/viz/stages.py                    app/react_learn/
  Stage dataclass                      src/
  build_stages() → Stage[]               components/
                    │                      StagePlayer.tsx
src/viz/export_stages.py                   PlaybackControls.tsx
  export_stages()                          StageExplanation.tsx
  _viz_for_stage()                         StageViz.tsx
          │                                  TokensViz.tsx
          ▼                                  EmbedNormsViz.tsx
learn_data/                                  AttentionGridViz.tsx
  manifest.json                              MlpHeatmapViz.tsx
  induction/                                 ResidNormsViz.tsx
    demo.json                                LogitLensViz.tsx
  kv_retrieval/                          data/
    demo.json                              manifest.json (symlink or copy)
  ...                                      induction/demo.json
                                           ...
scripts/
  export_learn_stages.py
  (CLI: generates all learn_data/)
```

---

## 4. Data Flow

```
1. GENERATE (Python, one-time per trace)
   load_trace(trace_dir) → (cache, meta)
   load_model(ckpt_dir) → (model, cfg)
   build_stages(cache, model, cfg, meta) → stages[]   # text fields
   _viz_for_stage(stage_type, cache, meta, cfg) → viz  # raw arrays
   combine → LearnPackage JSON
   write → learn_data/{task}/{trace_id}.json

2. LOAD (React, on app start)
   fetch manifest.json → available packages list
   user selects task + trace
   fetch learn_data/{task}/{trace_id}.json → LearnPackage

3. RENDER (React, on stage navigation)
   StagePlayer reads stages[currentIndex]
   StageExplanation renders text fields
   StageViz dispatches on stage.viz.kind → renders arrays
   PlaybackControls manages currentIndex state
```

---

## 5. JSON Schema

### Top-level package

```json
{
  "task": "induction",
  "trace_id": "demo",
  "n_tokens": 7,
  "n_layers": 2,
  "n_heads": 4,
  "d_model": 64,
  "vocab_size": 32,
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"],
  "stages": [ ...Stage objects... ]
}
```

### Stage object

```json
{
  "index": 0,
  "name": "Step 1: Input Tokens",
  "explanation": "The input is a sequence of 7 integer tokens...",
  "what_changed": "Nothing has been computed yet. This is the raw input.",
  "what_to_notice": "Look at the sequence structure...",
  "next_technical_view": "Token Overview",
  "viz": {
    "kind": "tokens",
    "data": { ... }
  }
}
```

### Viz data by kind

**`tokens`** — Stage 0: Input Tokens
```json
{
  "positions": [0, 1, 2, 3, 4, 5, 6],
  "tokens": [3, 7, 1, 5, 3, 7, 1],
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"]
}
```

**`embed_norms`** — Stage 1: Embeddings
```json
{
  "positions": [0, 1, 2, 3, 4, 5, 6],
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"],
  "tok_norms": [1.23, 1.45, ...],
  "pos_norms": [0.89, 0.92, ...],
  "combined_norms": [1.56, 1.78, ...]
}
```

**`attention_grid`** — Layer N Attention stages
```json
{
  "layer": 0,
  "n_heads": 4,
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"],
  "patterns": [
    [[0.1, 0.9, ...], ...],
    ...
  ]
}
```
Shape of `patterns`: `[n_heads][T][T]`

**`mlp_heatmap`** — Layer N MLP stages
```json
{
  "layer": 0,
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"],
  "top_neuron_indices": [12, 47, 3, ...],
  "activations": [[0.23, -0.1, ...], ...]
}
```
Shape: `top_neuron_indices`: `[k]`, `activations`: `[T][k]` where k=32 (top neurons by max abs activation).

**`resid_norms`** — After Layer N Residual stages
```json
{
  "highlight_layer": 0,
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"],
  "stage_names": ["embed", "L0.resid_pre", "L0.resid_mid", "L0.resid_post", ...],
  "norms": {
    "embed": [1.56, 1.78, ...],
    "L0.resid_pre": [1.56, 1.78, ...],
    "L0.resid_mid": [1.89, 2.01, ...],
    "L0.resid_post": [2.12, 2.34, ...],
    ...
  }
}
```

**`logit_lens`** — Stage N: Final Prediction
```json
{
  "layer_labels": ["after L0", "after L1"],
  "token_labels": ["3", "7", "1", "5", "3", "7", "1"],
  "actual_nexts": [7, 1, 5, 3, 7, 1, 1],
  "actual_next_labels": ["7", "1", "5", "3", "7", "1", "1"],
  "prob_of_actual_next": [
    [0.12, 0.34, ...],
    [0.89, 0.95, ...]
  ],
  "top_k_final": {
    "position": 5,
    "k": 5,
    "token_ids": [1, 7, 3, 5, 2],
    "token_labels": ["1", "7", "3", "5", "2"],
    "probs": [0.95, 0.03, 0.01, 0.005, 0.002]
  }
}
```
Shape of `prob_of_actual_next`: `[n_layers][T]`.

### Manifest

```json
{
  "generated_at": "2026-04-21T...",
  "packages": [
    {
      "task": "induction",
      "trace_id": "demo",
      "path": "induction/demo.json",
      "n_tokens": 7,
      "n_layers": 2
    },
    ...
  ]
}
```

---

## 6. React Components

The React app is Phase 3C scope. This section defines the component contract so that
the JSON schema and the component design are agreed before React is built.

### `StagePlayer`
Top-level component. Owns playback state (`currentIndex`). Renders:
- `PlaybackControls` (top)
- `StageExplanation` (left column)
- `StageViz` (right column)
- `PlaybackControls` (bottom, duplicate for long pages)

Props: `{ package: LearnPackage }`

### `PlaybackControls`
Props: `{ current: number, total: number, stageName: string, onPrev, onNext, onGoto }`
Renders: ← button, progress indicator, stage name, → button, jump selector.

### `StageExplanation`
Props: `{ stage: Stage }`
Renders: `explanation`, `what_changed`, `what_to_notice` (blockquote), `next_technical_view` link.

### `StageViz`
Props: `{ viz: VizPayload }`
Dispatches on `viz.kind`:
- `"tokens"` → `TokensViz`
- `"embed_norms"` → `EmbedNormsViz`
- `"attention_grid"` → `AttentionGridViz`
- `"mlp_heatmap"` → `MlpHeatmapViz`
- `"resid_norms"` → `ResidNormsViz`
- `"logit_lens"` → `LogitLensViz`

Each `*Viz` component receives `viz.data` directly and renders using a charting library
(Recharts, Nivo, or Plotly.js — to be decided in Phase 3C).

---

## 7. What Stays in Streamlit

Streamlit is **retained** as the Investigate Mode frontend. No migration.

- `app/streamlit_app.py` — main entry with mode toggle (unchanged)
- `app/views/` — all 6 Investigate Mode views (unchanged)
- `app/learn/learn_mode.py` — Streamlit Learn Mode (retained as reference and fallback)
- `src/viz/stages.py` — `Stage.figure` field kept for Streamlit rendering

The React Learn Mode adds a new frontend; it does not replace the existing one.
Both frontends read the same underlying data (traces, checkpoints).

---

## 8. Risks and Non-Goals

### Risks

**R1 — JSON file staleness.** If a new trace is generated but the export script is not
re-run, React will show stale data. Mitigation: document the "generate traces → export →
serve" workflow clearly. The manifest's `generated_at` timestamp helps detect staleness.

**R2 — MLP truncation loses neuron context.** Top-32 neurons are selected by max abs
activation across positions. If the pedagogically interesting neurons rank 33–64,
they won't appear. Mitigation: k=32 is generous for a d_model=64 model (256 neurons);
the most active neurons are almost always the interpretable ones.

**R3 — logit_lens `top_k_final` position choice.** The exporter picks `T-2`
(second-to-last position) as the most interesting prediction. For some tasks
(e.g., `factual_lookup` with T=1), this needs special-casing.

**R4 — React charting library not yet chosen.** Phase 3C decision. The semantic array
contract is library-agnostic; all standard React charting libraries (Recharts, Nivo,
Plotly.js, D3) can render heatmaps and line charts from raw arrays.

### Non-Goals (Phase 3B)

- React app scaffolding, components, package.json, bundler config
- Ablation controls, patching UI (Phase 4)
- Checkpoint comparison across training steps (Phase 5)
- SAE feature browser (Phase 6)
- Animation-quality smooth playback
- Custom task sequence entry in React UI
- Server-side rendering or SSR
- Authentication or multi-user support

---

## Files Created by Phase 3B

| File | Purpose |
|------|---------|
| `docs/architecture/react_learn_mode.md` | This document |
| `src/viz/export_stages.py` | Core exporter: trace → JSON package |
| `scripts/export_learn_stages.py` | CLI: generates all learn_data/ packages |
| `learn_data/manifest.json` | Index of available packages |
| `learn_data/induction/demo.json` | Example exported package |
| `learn_data/{task}/demo.json` | Packages for all 6 tasks |
