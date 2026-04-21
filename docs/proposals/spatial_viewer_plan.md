# Spatial Viewer — Sonnet Implementation Brief (Slice 1)

**Role:** Implementation brief for Sonnet. Follow this without reinterpreting the product.
**Status:** APPROVED. Slice 1 only.
**Parent specs:**
- `docs/architecture/spatial_visualization.md` — full architecture. Read first.
- `docs/phase_context/review_notes.md §21` — why this correction was made.
- `docs/architecture/react_learn_mode.md` — existing JSON contract; do not break it.

> This brief is deliberately terse. Every deviation must be logged in
> `docs/phase_context/next_actions.md` as a drift note before shipping.

---

## 1. Exact target artifact

A working **Spatial Learn Mode** tab in `app/react_learn/` that, when the React
dev server is running on the induction demo trace, satisfies all 10 acceptance
criteria in `docs/architecture/spatial_visualization.md §I`.

This slice is **read-only, single-trace, desktop-only**. No ablation. No input
entry. No comparison. No neuron grid. No exploded heads.

---

## 2. First implementation slice (Steps A–E from §H)

Implement strictly in order. Do not start step N+1 until step N runs.

### Step A — Spatial scene shell

- Add dependencies: `three`, `@react-three/fiber`, `@react-three/drei`, `zustand`.
- Create `app/react_learn/src/spatial/` subtree per `§G.2`.
- `App.tsx`: add a tab toggle — **Spatial** (new, default) | **Flat** (existing Phase 3C player).
- Implement `SpatialViewer.tsx` as an R3F `<Canvas>` + DOM overlay.
- Inside the Canvas:
  - `SceneRoot` arranges `EmbedPlate` (y=0), N `LayerModule`s stacked along Y,
    `UnembedPlate` (y=Y_top).
  - `ResidualBus` renders T translucent cylinders running the full Y range.
  - Each `LayerModule` draws a labeled box with two internal boxes: `AttentionBlock`
    and `MlpBlock`. Label them plainly ("Layer 0 · Attention", "Layer 0 · MLP").
- Camera: drei `<PerspectiveCamera>` framed front-on. `<OrbitControls>` with
  `minDistance`, `maxDistance`, and `maxPolarAngle` clamped; `enableDamping`.
- Add a "Reset camera" button in the overlay (DOM, not inside Canvas).
- Scene dimensions come from the existing `LearnPackage` fields
  (`n_layers`, `n_heads`, `n_tokens`); no scene.json yet.

**Exit:** Scene renders for all 6 existing packages. Rotate / zoom / pan work.
Labels are readable. Legacy Flat tab is one click away.

### Step B — Scene export + activation-driven intensity

- Create `src/viz/export_scene.py`. Reuse `src/tracing.ActivationCache`,
  `src/viz/loading.compute_logit_lens` and `residual_norms`, and `src/viz/stages.build_stages`.
- Emit `learn_data/{task}/{trace_id}.scene.json` matching the schema in
  `docs/architecture/spatial_visualization.md §F`.
- Components to emit in slice 1: `model`, `embed`, one `residual_bus`, per layer
  `layer` / `attn` / `mlp`, and `unembed`. **No `head`, no `neuron` yet** (they
  belong to later slices but the schema allows them, so leave the `children`
  arrays empty).
- Ticks: one per sub-step — `embed`, `L0.attn`, `L0.mlp`, `L1.attn`, `L1.mlp`,
  `unembed`. For L layers, that's `2 + 2L` ticks.
- Extend (or peer) `scripts/export_learn_stages.py` so a single CLI run produces
  both `.json` (existing) and `.scene.json` (new) per task. Update
  `manifest.json` to include both paths.
- Extend `useLearnData.ts` to fetch both packages when a task is selected.
- In the scene, bind each component's material opacity/emissive intensity to
  the matching entry in the **final tick**'s `active_components` (slice 1 shows
  only the final state; playback is step D).

**Exit:** Switching between induction and bracket_match changes which
components look brighter. Color scale is a simple sequential map documented
with a legend in the overlay.

### Step C — Selection + inspector panel

- `useSpatialStore` (zustand): `{ selectedId, tickIndex, isPlaying, speed, isIsolated }`.
- Raycast `onClick` on every selectable mesh sets `selectedId`. Clicking empty
  space clears selection. Double-click reserved for future "explode" (not bound now).
- `InspectorPanel` docks right. Content:
  - Breadcrumb: `Model › Layer 0 › Attention`.
  - Name, type, short `summary_blurb` from the scene package.
  - **Reused Stage explanation** — look up `explanation_ref` on the component,
    resolve to a stage index, render `explanation` + `what_changed` +
    `what_to_notice` using the existing `StageExplanation` component.
  - "View in Streamlit: {next_technical_view}" link (reuse existing behavior).
- Hover: `HoverTooltip` shows only the component name; do not overload it.

**Exit:** Clicking any layer / attn / MLP block shows the matching Python-
authored narrative text. Inspector text matches what the Flat view would show
for the corresponding stage.

### Step D — Playback

- `PlaybackBar` at the bottom of the overlay: `« prev`, `play/pause`, `next »`,
  `reset`, speed dropdown (0.5× / 1× / 2× / 4× → 3000 / 1500 / 750 / 375 ms/tick).
- Auto-advance uses a `ref`-stored index inside a `setInterval` handler — avoid
  stale closures (pattern already used in Phase 3C `StagePlayer`).
- `PlaybackCursor`: a thin flat plane (or ring) at the Y height of the current
  tick's component. Mesh for visual clarity, not strict physical meaning.
- Below-cursor components: full activation-driven intensity.
- At-cursor component: a subtle outline or emissive boost.
- Above-cursor components: 25% opacity, desaturated.
- **Speed is independent of compute.** The trace is already in memory; playback
  is a visual scrub over precomputed `ticks`.

**Exit:** Pressing play advances the cursor; changing speed changes the rate;
pause halts; reset returns to tick 0; end-of-sequence stops cleanly.

### Step E — Isolate, focus, keyboard, loading

- Isolate toggle in the inspector: non-selected components fade to ~30% opacity.
  Persist across playback ticks.
- "Focus selected" button: drei `<Bounds>` or explicit camera tween to frame
  the selected component smoothly. Tween duration ~500 ms. Not auto-triggered.
- Keyboard map (documented in a small `?` tooltip on the playback bar):
  - `← / →` = prev / next
  - `space` = play / pause
  - `r` = reset playback
  - `esc` = clear selection
  - `i` = toggle isolate
- Loading and error states: overlay a dim banner with text; do not unmount the
  scene. Preserve selection and tick on refetch.

**Exit:** All 10 acceptance criteria in `spatial_visualization.md §I` are met.

---

## 3. Required stack

- **React 18 + TypeScript** (already present).
- **Vite** (already present).
- **three** + **@react-three/fiber** + **@react-three/drei** — new.
- **zustand** — new, for scene state.

Nothing else. Do not add Redux, MUI, Tailwind, Framer-motion, a charting lib, or
a physics engine. If a decision seems to need one, write it in
`docs/phase_context/open_questions.md` and ship without it.

---

## 4. Required interactions (slice 1)

| Interaction | Must work in slice 1 |
|---|---|
| Rotate (orbit) | ✓ |
| Zoom | ✓ |
| Pan | ✓ |
| Reset camera | ✓ |
| Hover → name tooltip | ✓ |
| Click → select + inspector | ✓ |
| Deselect (click empty / esc) | ✓ |
| Isolate selected | ✓ |
| Focus-selected camera tween | ✓ |
| Playback: prev / next / play / pause / reset | ✓ |
| Speed control | ✓ (4 presets) |
| Keyboard shortcuts | ✓ |
| **Explode layer** | ✗ — slice 2 |
| **Neuron grid** | ✗ — slice 3 |
| **Compare inputs** | ✗ — later |
| **Any intervention / ablation** | ✗ — Phase 4 |
| **Custom input entry** | ✗ — Phase 4+ |

---

## 5. Expected files / modules

**Python (new):**
- `src/viz/export_scene.py` — scene graph + tick extractor.
- `scripts/export_scene.py` — CLI (or extend `scripts/export_learn_stages.py`);
  writes `.scene.json` per task and updates `manifest.json`.

**Python (extended):**
- `scripts/export_learn_stages.py` — either wraps `export_scene` or calls it.
- `learn_data/manifest.json` — add `scene_path` per package.

**Python (untouched):**
- `src/tracing/*` — do not modify.
- `src/models/transformer.py` — do not modify.
- `src/viz/stages.py`, `src/viz/loading.py`, `src/viz/plotting.py`, `src/viz/export_stages.py`
  — do not modify. Reuse only.
- `app/streamlit_app.py`, `app/views/*`, `app/learn/*` — do not modify.

**TypeScript (new):**
- `app/react_learn/src/hooks/useSpatialStore.ts`
- `app/react_learn/src/spatial/SpatialViewer.tsx`
- `app/react_learn/src/spatial/scene/{SceneRoot,ResidualBus,EmbedPlate,LayerModule,AttentionBlock,MlpBlock,UnembedPlate,PlaybackCursor}.tsx`
- `app/react_learn/src/spatial/overlay/{InspectorPanel,HoverTooltip,PlaybackBar,ComponentBreadcrumb}.tsx`
- `app/react_learn/src/spatial/logic/{selection,tickMapping,colorScale}.ts`

**TypeScript (extended):**
- `app/react_learn/src/App.tsx` — add Spatial/Flat tab; default to Spatial.
- `app/react_learn/src/hooks/useLearnData.ts` — also fetch `.scene.json`.
- `app/react_learn/src/types.ts` — add `SceneComponent`, `Tick`, `ScenePackage` types.
- `app/react_learn/package.json` — add three, R3F, drei, zustand.

**TypeScript (untouched):**
- `app/react_learn/src/components/*` — existing Phase 3C viz components.
  Reuse `StageExplanation.tsx` inside the new `InspectorPanel`.
- `app/react_learn/src/components/viz/*` — belong to the Flat tab; do not import
  from the Spatial tab.

**Docs (extended):**
- `docs/phase_context/current_phase.md` — set Phase 3D active.
- `docs/phase_context/implementation_status.md` — append after each step.
- `docs/phase_context/next_actions.md` — drift notes, open items.
- `docs/phase_context/open_questions.md` — new Qs as they surface.
- `docs/phases/phase_3.md` — append a "Phase 3D — Spatial Viewer" section at
  end of slice 1.

---

## 6. Boundaries Sonnet must respect

**Hard boundaries (violating any is a drift failure):**

1. **No biology.** Zero anatomy language, zero organic shapes, zero glowing
   "brain" aesthetics. Boxes, pipes, plates, tiles.
2. **No Phase 4 controls.** No ablation, no patching, no "what-if" UI. The
   scene is read-only.
3. **No auto-play on load.** Default state: paused at tick 0. Learner initiates.
4. **No auto-camera-jumping on selection.** Camera only moves on explicit
   reset or focus button.
5. **No replacement of Streamlit.** Investigate Mode stays in Streamlit.
   Spatial viewer links *to* it, never reimplements its views.
6. **No schema break.** `docs/architecture/react_learn_mode.md §5` stays valid.
   `scene.json` is additive.
7. **No renamed tensors.** Use the exact names from `review_notes §16.3`
   (TransformerLens-style dot-keys).
8. **No new charting library.** R3F for Spatial; existing SVG components stay
   in the Flat tab.
9. **No data-fetch server.** Everything stays static files.
10. **No tokenizer.** Integer labels with task hints, as today.
11. **No scope creep into slice 2 or 3.** If the scene looks "ready to
    explode layers" after step E, stop and ship. Exploded view is a separate
    slice with its own review.
12. **No silent CLAUDE.md edits.** Proposal mode applies.

**Soft boundaries (do them unless a named blocker forces otherwise):**

- One sequential colormap in slice 1. Keep it simple; pick later if needed.
- No animation tweens beyond camera focus and cursor rise. No bounce easing.
- No particle systems, bloom post-processing, or ambient audio.
- Component boxes flat-shaded; default lighting (ambient + one directional).
- Text labels drei `<Html>` or `<Text>` — pick one and stay consistent.

---

## 7. Validation before declaring slice 1 done

Run and verify each, in order:

1. `python scripts/export_scene.py` (or the extended runner) regenerates all 6
   packages without errors. `manifest.json` lists each `scene_path`.
2. `cd app/react_learn && npm install && npm run dev` starts clean.
3. Open the app. Spatial tab is default. Scene renders for the induction
   package. `n_layers=2` layers visible, T=7 residual pipes visible.
4. Rotate, zoom, pan all work. Reset camera restores front-on view.
5. Switch task selector to `sorting`. Scene reshapes (different T, same L).
6. Click Layer 0 → Attention block. Inspector shows explanation text from the
   matching Stage. "View in Streamlit" link is present.
7. Press play at 1× speed. Cursor rises; components below cursor are fully
   rendered; above are dim. Pause halts immediately. Reset returns to tick 0.
8. Change speed to 4×. Playback accelerates. No recomputation observed; CPU
   remains near-idle (playback is a scrub, not a rerun).
9. Select the MLP block in Layer 1. Toggle isolate. All other components fade.
   Toggle off. Others restore.
10. Press `esc`. Selection clears. Press `r`. Playback resets. Press space.
    Playback toggles.
11. Check the browser console: zero uncaught errors across induction,
    kv_retrieval, sorting, modular_arith, bracket_match, factual_lookup.
12. Run Streamlit: `streamlit run app/streamlit_app.py` — both Learn Mode and
    Investigate Mode still work identically to before this slice.

When all 12 hold, append a closure note to `implementation_status.md` and
request Opus review against `docs/architecture/spatial_visualization.md §I`
acceptance criteria. **Do not self-approve.** That's §12-style independent
review territory.

---

## 8. If you get stuck

- If R3F rendering chokes on resource counts (unlikely at T≤32, L≤2, H≤4),
  add an issue to `open_questions.md` and keep the scene simple — do not
  introduce instancing prematurely.
- If the tick-to-component mapping feels ambiguous for L ≥ 3 models, document
  the convention in `open_questions.md` and pick the `2 + 2L` layout proposed
  in §H.B.
- If a design choice seems to require a Phase 4 primitive (e.g., "I need
  per-position ablation to compute per-token relevance"), **stop**. The
  slice-1 scope does not include per-token relevance. Note it in
  `next_actions.md`. Do not quietly add Phase 4 machinery.

Slice 1 is done when a learner can load the viewer and, without help, say
*"the model is a stack of layers with a shared residual stream, and this is
where it did the most work on this input"* — pointing at the actual component.
That's the bar.
