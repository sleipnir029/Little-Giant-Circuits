# React Learn Mode

A guided, stage-by-stage walkthrough of a transformer forward pass.
Consumes pre-exported JSON packages from `learn_data/` — no server required.

## Setup

```bash
cd app/react_learn
npm install
```

## Run

```bash
npm run dev
# → http://localhost:5173
```

The `learn_data/` packages are served as static assets via the Vite `publicDir` config
(set to the project root). No symlink or copy needed.

If you see "Learn data not found", regenerate the packages:

```bash
# From project root:
source .venv/bin/activate
python scripts/export_learn_stages.py
```

If traces are also missing:

```bash
python scripts/generate_demo_traces.py
python scripts/export_learn_stages.py
```

## What this is

**Learn Mode** walks through 9 stages of a single forward pass for a task of your choice:

1. Input Tokens
2. Embeddings — Tokens Become Vectors
3. Layer 0 — Attention
4. Layer 0 — MLP
5. Layer 0 — Residual Stream
6. Layer 1 — Attention
7. Layer 1 — MLP
8. Layer 1 — Residual Stream
9. Final Prediction

Each stage shows:
- Plain-language explanation of what's happening
- What changed from the previous stage
- What to notice (highlighted callout)
- A focused visualization (custom SVG, no chart library deps)
- A link to the corresponding Streamlit Investigate Mode view

## What this is NOT

- A replacement for Streamlit. Investigate Mode (all 6 technical views) stays in Streamlit.
- An intervention tool. No ablation, patching, or model modification — that's Phase 4.
- A live model runner. JSON packages are pre-exported static files.

## Stack

- Vite + React 18 + TypeScript
- Zero charting library deps — all visualizations are custom SVG
- `publicDir` set to project root so `learn_data/` is served as `/learn_data/`

## Component tree

```
App
├── Header (task selector, Investigate Mode link)
└── StagePlayer (owns playback state)
    ├── ProgressTimeline
    ├── PlaybackControls (prev/next/play/pause/reset/speed)
    ├── StageExplanation (explanation, what_to_notice, Streamlit link)
    └── StageViz (dispatches on viz.kind)
        ├── TokensViz
        ├── EmbedNormsViz (GroupedBarChart)
        ├── AttentionGridViz (HeatmapGrid × 4 heads)
        ├── MlpHeatmapViz (HeatmapGrid, diverging colormap)
        ├── ResidNormsViz (SVG line chart)
        └── LogitLensViz (HeatmapGrid + BarChart)
```

## What remains unfinished

- Markdown rendering in explanation text (bold `**text**` shows as literal `**`)
- The induction demo trace's logit lens shows low confidence — the 7-token demo
  sequence doesn't fully activate the induction circuit. A longer sequence would
  show clearer signal. This is a data quality issue, not a UI bug.
- Mobile layout not tested or optimized
- Production build (dist/) does not include learn_data/ — dev use only
