# Current Phase

## Active Phase
Phase 3D — Spatial Mechanistic Viewer

**Status:** Step A COMPLETE — awaiting Opus review before Step B
**Started:** 2026-04-21
**Step A completed:** 2026-04-21

**Predecessor:**
Phase 3C — React Learn Mode UI: COMPLETE (2026-04-21)

**Predecessor phases:**
- Phase 3 technical UI: COMPLETE (2026-04-21)
- Phase 3 Refinement (Streamlit Learn Mode): COMPLETE (2026-04-21)
- Phase 3B (React data bridge): COMPLETE (2026-04-21)

**Objective:**
Build a React-based learner-first dashboard that consumes the exported staged JSON packages
and lets a user watch and understand model computation step by step.

**Advisory:** `review_notes.md §20`

---

## Phase 3B Summary

Phase 3B built the Python→React data bridge:
- `src/viz/export_stages.py` — core exporter (semantic arrays, not Plotly specs)
- `scripts/export_learn_stages.py` — CLI to regenerate all packages
- `learn_data/` — generated JSON packages for all 6 tasks
- `docs/architecture/react_learn_mode.md` — full design doc + JSON schema

The Streamlit app (both Investigate Mode and Learn Mode) is unchanged and working.

---

## Phase 3 Refinement Objective

The existing technical inspection views are well-built but serve as a microscope, not
a teacher. A learner arriving at the app for the first time has no story, no sequencing,
and no explanation of what they are looking at.

This refinement adds a **Learn Mode** — a stage-stepped, narrative walkthrough of a
single forward pass. The learner chooses a task and trace, then advances stage by stage
through the computation, with plain-language explanations at each step.

The existing six views become **Investigate Mode** — accessible via a top-level mode
toggle, preserved and unchanged.

Understanding is still the deliverable. The refinement makes it achievable without
prior transformer knowledge.

---

## Phase 3 Refinement Exit Criteria

### From original Phase 3 (all still hold):
- [x] `streamlit run app/streamlit_app.py` starts without errors
- [x] Six Investigate Mode views render: Token Overview, Layer Overview, Attention,
      MLP Activations, Logit Evolution, Compare Traces
- [x] Induction demo trace loads and all views display correctly
- [x] Demo trace generation script works for all 6 tasks
- [x] `src/viz/` has no streamlit imports

### New refinement criteria:
- [ ] Top-level Learn / Investigate mode toggle visible on app load
- [ ] Learn Mode walks through 9 stages for a 2-layer model
- [ ] Each stage shows: explanation, what changed, what to notice, technical link
- [ ] Each stage shows a focused Plotly figure (not raw tensor dumps)
- [ ] Forward/backward step controls work via session_state
- [ ] Stage indicator ("Step 3 of 9: Layer 0 — Attention") always visible
- [ ] Prediction confidence shown simply at final stage
- [ ] Each stage links to the corresponding Investigate Mode view by name
- [ ] `src/viz/stages.py` has no streamlit imports (pure data layer)
- [ ] `src/viz/playback.py` has no streamlit imports (pure state helpers)
- [ ] `app/learn/learn_mode.py` contains all Learn Mode rendering
- [ ] `docs/phases/phase_3.md` updated with refinement section
- [ ] `review_notes.md §18` written (advisory for this refinement)

---

## Phase 3 Refinement In-Scope

- `src/viz/stages.py` — Stage dataclass + build_stages(cache, model, cfg, meta)
- `src/viz/playback.py` — pure playback state helpers (no streamlit)
- `app/learn/__init__.py` — package stub
- `app/learn/learn_mode.py` — Learn Mode render function
- `app/streamlit_app.py` — add mode toggle + Learn Mode routing (minimal changes)
- `docs/phase_context/` — review_notes §18, current_phase, implementation_status, next_actions

---

## Phase 3 Refinement Out-of-Scope

- Ablation or patching controls (Phase 4) — explicitly blocked in Learn Mode
- Checkpoint comparison (Phase 5)
- SAE feature browser (Phase 6)
- React or Gradio migration — not justified; Streamlit retained
- Animation-quality auto-play — deferred; step-buttons are better pedagogy
- Changes to `src/viz/plotting.py`, `src/viz/loading.py`, `src/tracing/`, `app/views/`

---

## Predecessor State

Phase 3 COMPLETE (2026-04-21):
- `src/viz/loading.py`, `src/viz/plotting.py` — pure plotly helpers
- `app/streamlit_app.py` with sidebar + 6 views
- `app/views/` — 6 view files (token_overview, layer_overview, attention_view,
  mlp_view, logit_evolution, comparison)
- `scripts/generate_demo_traces.py`
- Demo traces for all 6 tasks in `traces/{task}/demo/`

---

## How to Use This File

- Update Status when phase transitions: `IN PROGRESS` → `COMPLETE`.
- Do not use this file as a scratch pad. Progress goes in `implementation_status.md`.
- Unresolved decisions go in `open_questions.md`.
