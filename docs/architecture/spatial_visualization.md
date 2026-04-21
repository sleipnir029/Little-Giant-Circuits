# Spatial Visualization — Architecture Spec

**Status:** APPROVED for implementation (first slice scoped below).
**Role of this doc:** Authoritative design for the spatial Learn/Explore viewer that
supersedes the slide-deck-style React Learn Mode (Phase 3C).
**Author:** Opus 4.7, principal research advisor.
**Date:** 2026-04-21.

> The React Learn Mode built in Phase 3C is a narrative slide deck. It advances stage
> by stage, renders one chart per stage, and calls that "playback." That is not the
> target. The target is a spatial, interactive, explorable view of a transformer
> where a learner can rotate around the model, see activity unfold, click into
> components, and understand what the model is doing mechanistically. This document
> defines that system.

---

## A. Problem framing

### A.1 Why the current solution is insufficient

The Phase 3C React Learn Mode delivered:
- 9 ordered stages (input → embeddings → L0 attn → L0 MLP → … → prediction).
- One 2D chart per stage (attention heatmap grid, MLP heatmap, residual line chart, logit lens heatmap).
- Prev/Next/Play/Pause controls over stage index.
- An explanation panel beside each chart.

This is functionally a slide deck. Every serious limitation follows from that shape:

1. **Spatial relationships are hidden.** A transformer is a layered, parallel structure:
   residual streams run through all layers, attention heads compute in parallel, MLPs
   fan out and fan back in, information flows from embeddings to logits. The slide
   deck reduces all of that to a single chart at a time with no visible topology.
2. **There is no "camera."** A learner cannot look at the whole model and then look
   closer at one piece. The viewer has no notion of zoom, rotation, or focus. Every
   stage resets the view to a fresh 2D panel.
3. **Playback is tied to stage index, not to computation.** Clicking "next" does not
   advance a computation front — it swaps the entire chart. The learner never sees
   activity propagate along the residual stream or see one layer's output becoming
   the next layer's input.
4. **No selection, no inspection.** Components (layers, heads, neurons) cannot be
   clicked, hovered, or isolated. A learner cannot ask "what is that attention head
   doing?" by pointing at it.
5. **No "explode."** A layer is opaque in the overview. The subcomponent structure
   (heads within attention, neurons within MLP) is never visible as a structure.
6. **Separate views, separate universes.** The Streamlit Investigate Mode and the
   React Learn Mode share data but present it as disconnected 2D panels. There is no
   shared spatial model the learner can carry between them.

### A.2 What the real user experience must be

The target experience is an **interactive mechanistic viewer** — closer to a CAD
assembly viewer, a 3D anatomy inspector, or a game-engine runtime inspector than to a
dashboard or slide deck. A learner should be able to:

- Load a traced example (task + input sequence + checkpoint).
- See the full model laid out in space with the residual stream visible as a conduit.
- Rotate, zoom, and pan around the model with direct camera control.
- Watch activity propagate layer by layer when playback advances, independent of
  wall-clock compute speed, at a learner-controlled rate.
- Click a layer or component to select it and open an inspector panel with
  plain-language explanation, key tensors, and technical-depth links.
- "Explode" a selected layer to see its internal structure (attention heads laid
  out as separate tiles, MLP as a neuron/feature grid) without losing context.
- See which components are active for the current input — activations drive visual
  intensity, not decorative colors.
- Swap the input and see what changes — eventually, compare two inputs side by side
  (deferred past the first slice).
- Move down from the overview into neuron- or feature-level inspection when ready,
  and climb back up without losing the mental model.

This is not a better dashboard. It is a **glass-box spatial model** of the computation.

---

## B. Honest visual metaphor

### B.1 Rule

**No biology. No organic imagery. No "neural lobes," "brains," or "synapses."**
A transformer is not a brain and pretending otherwise teaches learners something
false. The metaphor must be mechanical and faithful to the actual computation.

### B.2 The adopted metaphor: **instrumented pipeline on a residual bus**

Treat the transformer as:

- A **residual stream bus** that runs the full length of the model. Each token
  position is one parallel channel on the bus. The bus is a visible conduit/pipe
  structure.
- A **stack of layer modules** arranged along the bus. Each module is a physical
  "station" the bus passes through.
- Inside each layer module, two sub-blocks tap into the bus: an **attention block**
  and an **MLP block**. They read the current bus state, do computation, and write
  their output back into the bus (additive residual).
- The **attention block** contains H parallel **head units** — each head is a
  sub-region inside the block. Heads read and write to the bus separately and get
  summed.
- The **MLP block** is a fan-out → nonlinearity → fan-in structure. Internally it
  contains 4·d_model neurons; these are visible as a grid only when the learner
  explodes the MLP.
- At the end of the bus, the **unembedding / head** converts the final bus state
  into per-token logit distributions.

### B.3 Spatial axes

| Axis | Meaning |
|------|---------|
| **X** | Token position — the residual bus has T parallel channels running across X. |
| **Y** | Depth — layer 0 at the bottom, layer L at the top. Computation proceeds upward. |
| **Z** | Component interior — heads within an attention block spread along Z; neurons within an MLP spread along Z×X. |

This choice means:
- Looking at the model from the front, you see a 2D cross-section: positions × depth.
- Rotating 90° around Y reveals the interior structure of whichever component you're
  near (heads fanning out, neurons as a cloud).
- Playback is a **horizontal cutting plane** advancing along Y (depth): as it rises,
  earlier layers' outputs are already "written into the bus" and later layers are
  still latent.

### B.4 What this metaphor is faithful to

- Residual stream as a **bus** is mathematically correct: `resid_post = resid_pre +
  attn_out + mlp_out`. Every layer reads and writes the same d_model-wide vector
  per token position.
- Attention heads as **parallel sub-units** is correct: `attn_out =
  sum_h head_h(resid_pre)`. Heads are additive contributions; summing them into the
  bus is literally what the code does.
- MLP as **fan-out/fan-in** is correct: `mlp_out = W2 · σ(W1 · resid_mid)`, with an
  intermediate dimension of `4·d_model`.
- Playback as **layer-wise progression** is correct: the forward pass is a strictly
  ordered traversal of layers, not a parallel burst.
- Token positions as **parallel channels** is correct: each token has its own
  residual vector; attention mixes information between them but the vectors
  themselves are indexed by position.

### B.5 What this metaphor abstracts away (and how to surface it honestly)

- **Layer norm and bias terms** are not drawn. If the learner asks, the inspector
  panel for the residual stream must mention that a LayerNorm is applied before
  each sub-block reads from the bus.
- **QKV projections** are collapsed inside each head's tile. When a head is
  selected, the inspector shows Q, K, V, scores, pattern as separate tensor
  summaries — do not hide them.
- **The softmax inside attention** is not drawn as a step; the attention pattern is
  shown as the post-softmax routing. The inspector text must say "post-softmax" to
  avoid implying the raw scores are what the model "uses."
- **Causal masking** is not drawn as a wall. The attention pattern inherently shows
  it (upper-triangular zeros). The inspector should call this out in plain language.

No metaphor is free. The rule for this project is: **every abstraction must be
declared in the inspector panel where a learner would encounter it.**

### B.6 Metaphors explicitly rejected

- **Brain / neural anatomy** — false biological claim. Not used.
- **Electrical circuits with current flow animations** — misleading: data is not a
  continuous current, and the "flow" is feed-forward, not cyclic.
- **Neural network as a sparsely-connected graph of neurons** — this is the
  MLP-era picture and is misleading for transformers where most structure lives in
  attention and residuals, not neuron-to-neuron wires.
- **"Tokens traveling through a factory"** — cute but implies tokens move along
  separate tracks; actually they share a bus and attention mixes them.

---

## C. User modes

Two modes, one shared spatial model.

### C.1 Learn / Explore mode

- Primary audience: a learner who does not already understand transformers.
- Entry view: the full model, residual bus visible, camera positioned to see the
  whole tower front-on.
- Default interactions: rotate, zoom, pan, hover, click, play/pause a layer-wise
  sweep.
- Every selection opens an inspector with plain-language explanation, "what this
  component is doing for this input," and a link to deeper-technical content.
- Each component has a short educational blurb authored in Python (reused and
  extended from the existing Stage explanations).

### C.2 Investigate / technical mode

- Primary audience: a user who knows transformers and wants exact tensor data.
- Entry view: same spatial scene, but the inspector panel defaults to the **tensor
  tab** (raw shapes, per-head pattern heatmap, per-neuron activation bars, logit
  numbers) instead of the **explanation tab**.
- Optional cross-link: the Streamlit Investigate Mode is kept as a reference
  implementation for views that do not yet exist in the spatial viewer (e.g.,
  run-to-run comparison). The spatial viewer is allowed to link out to it by name
  ("Open in Streamlit: Attention view, L0 H2").

### C.3 Relation between modes

- **Single source of truth for scene state.** Camera position, selected component,
  current playback index, and current trace are shared across modes. Switching
  modes must not reset the view.
- **Mode toggle is a tab in the top bar**, not a separate app.
- The two modes differ only in the default inspector content and the density of
  detail shown on hover. The 3D scene itself is identical.

---

## D. Interaction model

### D.1 Full list

| Interaction | Description | First slice? |
|---|---|---|
| **Rotate** | Drag to orbit camera around the model. | Yes |
| **Zoom** | Wheel / pinch to dolly toward/away. Clamp to sane bounds. | Yes |
| **Pan** | Middle-drag or shift-drag to translate. | Yes |
| **Reset camera** | Button to return to default front-on framing. | Yes |
| **Hover** | Highlight the component under the cursor; show its name + one-line summary as a floating tooltip. | Yes |
| **Click / select** | Make a component the focused one. Opens inspector panel. Second click on the same component deselects. | Yes |
| **Isolate** | "Solo" a component: fade everything else to low opacity so the selected component stands alone in context. Toggle. | Yes (minimum viable) |
| **Playback** | Advance the computation cursor layer-by-layer; stop at end. Play / pause / prev / next / reset. | Yes |
| **Speed control** | Control the ms-per-layer rate of playback independent of compute. | Yes |
| **Explode** | Transform a selected layer to separate its attention block and MLP block and fan the attention heads outward. Reversible (implode). | Slice 2 |
| **Drill-in neuron view** | Transform a selected MLP block into a neuron/feature grid. | Slice 3 |
| **Compare inputs** | Run two traces, show them side-by-side with a diff overlay. | Later (Phase 4+ scope) |
| **Intervention / ablation** | Apply zero / mean ablation to a selected head or neuron and re-render activations. | Phase 4 (do not build yet) |
| **Feature-level annotation** | Overlay SAE feature labels or known-circuit annotations. | Phase 6 |

### D.2 Invariants

- **Every interaction preserves the camera framing unless the user requests a
  reset.** Clicking a component does not teleport the camera. An auto-frame
  "focus" button may move the camera, but only on explicit request.
- **Playback speed is decoupled from compute speed.** Computation is done upfront
  (the trace is already in memory); playback is a visual scrub over precomputed
  data, not a re-computation. This is what makes slow-motion possible.
- **Selection is sticky across playback.** Advancing the playback cursor does not
  clear the selected component.
- **The scene never goes blank.** Every state has a visible model; loading errors
  show an overlay, not a wipe.

---

## E. Scene design

### E.1 Minimum viable scene (first slice)

One scene at load time. Components:

1. **Residual bus.** T parallel translucent pipes running from y=0 (input
   embedding) to y=Y_top (final unembed). Each pipe is one token position.
2. **Embedding plate.** A flat plate at y=0 with T slots; each slot is labeled
   with the token id / symbol.
3. **Layer modules.** One module per layer, stacked vertically. Each module is a
   box with two visible sub-blocks labeled "Attention" and "MLP."
4. **Attention sub-block.** Drawn as a rectangular panel; not yet exploded into
   heads in slice 1.
5. **MLP sub-block.** Drawn as a second rectangular panel; not yet exploded into
   neurons in slice 1.
6. **Unembed plate.** A flat plate at y=Y_top with T slots; each slot shows the
   top predicted token and confidence at that position.
7. **Playback cursor.** A thin horizontal plane (or glowing ring) at the current
   computation depth. Below the cursor, components are rendered as "active /
   written" (full opacity, activation-driven intensity); above, as "latent"
   (low opacity, muted color).

### E.2 Selected-layer view (slice 1 end)

When a layer is clicked:
- The module subtly raises or scales (~5–10%) to indicate selection.
- Neighboring layers dim to ~40% opacity.
- The inspector panel docks on the right with the layer's info.
- Camera may gently dolly toward the selected layer only if the learner presses
  a "focus" button — not automatically.

### E.3 Exploded-layer view (slice 2)

When a layer is exploded (button in inspector or keyboard "E"):
- The attention block separates from the MLP block along Z.
- The attention block fans its H heads out along Z, each head becomes a small
  visible tile.
- Each head tile displays the attention pattern as a small heatmap texture on
  one face.
- Hovering a head tile shows the head's pattern enlarged as a HUD overlay.
- Clicking a head tile selects that head; inspector updates.
- "Implode" button collapses it back.

### E.4 MLP neuron view (slice 3)

When an MLP block is drilled into:
- The camera frames the MLP block; surrounding layers fade further.
- The MLP expands into a neuron grid: top-K most-active neurons as a
  position×neuron heatmap, arranged as a 2D plane inside the MLP bounding box.
- Selecting a neuron shows its activation across positions + its output
  contribution magnitude into the residual bus.
- Implode returns to the flat MLP block.

### E.5 Minimum viable spatial viewer = slice 1 only

The first shippable viewer is E.1 + E.2 + interactions in D.1 marked "first
slice." E.3 and E.4 are subsequent slices and are out of scope for the initial
build.

---

## F. Data contract requirements

The Phase 3B JSON contract (`docs/architecture/react_learn_mode.md §5`) is
stage-oriented and does not describe the model's spatial structure or per-
component activation summaries. The spatial viewer needs an additional export.

### F.1 New package: `scene.json`

Produced alongside the existing `learn_data/{task}/{trace_id}.json`. Path:
`learn_data/{task}/{trace_id}.scene.json`.

The existing stage package is **not replaced** — it is still valid for stage
narration and remains the source of explanation text. The scene package adds
structural and activation data the spatial viewer needs.

### F.2 Top-level scene schema

```json
{
  "task": "induction",
  "trace_id": "demo",
  "model": {
    "n_layers": 2,
    "n_heads": 4,
    "d_model": 64,
    "d_mlp": 256,
    "vocab_size": 32,
    "n_tokens": 7
  },
  "tokens": {
    "ids": [3, 7, 1, 5, 3, 7, 1],
    "labels": ["3", "7", "1", "5", "3", "7", "1"]
  },
  "components": [ ...Component[] ... ],
  "ticks": [ ...Tick[] ... ],
  "stages_ref": "induction/demo.json"
}
```

### F.3 `Component` — the scene graph

Each component has a stable ID, a type, a human-readable label, and parent/child
relationships. This is the scene graph React Three Fiber will render against.

```json
{
  "id": "L0.attn.h2",
  "type": "head",
  "label": "Layer 0 — Head 2",
  "parent_id": "L0.attn",
  "children": [],
  "explanation_ref": "stages[2]",
  "summary_blurb": "One of 4 attention heads. Reads from the residual bus, writes an additive update."
}
```

Component types expected in slice 1:
- `model` (root)
- `embed`
- `residual_bus` (one per token position, optional aggregate)
- `layer` (one per layer)
- `attn` (one per layer)
- `mlp` (one per layer)
- `unembed`

Component types added in later slices:
- `head` (H per layer)
- `neuron` (top-K per MLP)

### F.4 `Tick` — per-layer activity summary

One tick per logical playback step. The natural tick granularity is a **sub-layer
step**: `embed`, then for each layer `(attn, mlp)`, then `unembed`. For a 2-layer
model this is 6 ticks.

```json
{
  "index": 3,
  "label": "Layer 1 — Attention",
  "component_id": "L1.attn",
  "stage_ref": 5,
  "active_components": [
    {"id": "L1.attn.h0", "intensity": 0.12},
    {"id": "L1.attn.h1", "intensity": 0.87},
    {"id": "L1.attn.h2", "intensity": 0.34},
    {"id": "L1.attn.h3", "intensity": 0.58}
  ],
  "bus_state": {
    "resid_norms": [1.56, 1.78, 2.01, ...]
  },
  "delta": {
    "component_id": "L1.attn",
    "delta_norm_per_position": [0.23, 0.11, 0.08, ...]
  }
}
```

### F.5 Derived fields the exporter must compute

From the existing activation cache:

| Field | How |
|---|---|
| `component.id` | Deterministic naming: `L{i}.attn`, `L{i}.attn.h{h}`, `L{i}.mlp`, `L{i}.mlp.n{k}` |
| Head intensity per tick | L2 norm of per-head output (`blocks.i.attn.output` split per-head) averaged across positions, normalized to [0, 1] within the layer. |
| MLP intensity per tick | L2 norm of `blocks.i.mlp.output` per position, max-pooled, normalized. |
| Per-neuron top-K | Top-K by max abs post-GELU across positions. Slice 1 skips this; Phase-scoped for slice 3. |
| `bus_state.resid_norms` | Reuse `residual_norms` helper from `src/viz/loading.py`. |
| `delta.delta_norm_per_position` | `||resid_after_component|| − ||resid_before_component||` per token position. |
| Per-token relevance | Slice 1 may skip. In later slices, compute per-token `||head_output_position|| / ||layer_output_position||` as a crude contribution estimate. |

### F.6 Explanation text: reuse the existing stage package

Do not duplicate explanation content. The scene package references stage indices
(`stage_ref: 5`) and the viewer loads the corresponding `stages[5].explanation`,
`what_changed`, `what_to_notice` from the existing package. This keeps Python as
the single source of truth for narrative text.

### F.7 Comparison hooks (later)

Reserved fields in the schema, unused in slice 1:

```json
"compare_ref": null,
"intervention": null
```

Document them in the schema so slice-N additions do not require schema-breaking
changes.

---

## G. Frontend architecture

### G.1 Stack

| Layer | Choice | Why |
|---|---|---|
| Build | **Existing Vite** in `app/react_learn/` | Do not fork. Extend. |
| UI | **React 18 + TypeScript** | Already in use. |
| 3D | **react-three-fiber (@react-three/fiber)** | Thin declarative wrapper over Three.js; keeps the scene in React-idiomatic code. |
| 3D helpers | **@react-three/drei** | Stock cameras, controls, text, bounds helpers. Reduces boilerplate. |
| 3D engine | **three.js** (pulled in transitively) | Stable, well-documented, no alternative of comparable maturity. |
| State | **zustand** | Lightweight global store for `{selection, playback, trace, camera}`. Avoids prop drilling through deep scene graphs. |
| Data fetching | **Existing `useLearnData` hook**, extended to load `.scene.json` | No new data layer. |
| Text / inspector UI | Plain React components with CSS; reuse existing `StageExplanation` | No new UI framework. |

**Do not add:** Redux, Recoil, MUI, Tailwind, Framer-motion, physics engines, or
game-engine-style middleware. Keep dependencies minimal.

### G.2 Module layout (incremental additions only)

```
app/react_learn/src/
  App.tsx                                  [modified: add mode toggle Spatial / Legacy]
  hooks/
    useLearnData.ts                        [modified: also fetch .scene.json]
    useSpatialStore.ts                     [new: zustand store]
  spatial/                                 [new subtree]
    SpatialViewer.tsx                      [top-level R3F canvas + overlay]
    scene/
      SceneRoot.tsx                        [model-level layout]
      ResidualBus.tsx                      [T translucent pipes]
      EmbedPlate.tsx
      LayerModule.tsx                      [one per layer]
      AttentionBlock.tsx
      MlpBlock.tsx
      UnembedPlate.tsx
      PlaybackCursor.tsx
    overlay/
      InspectorPanel.tsx                   [right dock; reuses StageExplanation]
      HoverTooltip.tsx
      PlaybackBar.tsx                      [bottom; prev/next/play/speed]
      ComponentBreadcrumb.tsx              [top-left; Model › Layer 0 › Attention]
    logic/
      selection.ts                         [pure helpers; zustand-agnostic]
      tickMapping.ts                       [tick ↔ stage ↔ component]
      colorScale.ts                        [activation intensity → color]
  components/                              [existing; untouched]
```

Existing Phase 3C components remain. A new top-level toggle lets the user switch
between the legacy stage-player and the new spatial viewer while the spatial
viewer stabilizes. Once the spatial viewer is the primary Learn Mode, the legacy
player can be demoted to a "Flat view" option behind the same toggle.

### G.3 Minimal dependencies added

```
three
@react-three/fiber
@react-three/drei
zustand
```

That is the full new-dependency list.

---

## H. Incremental implementation plan

Each step is bounded, ends with a runnable artifact, and is independently reviewable.

### Step A — Spatial scene shell (no activations, no playback)

**Goal:** A static spatial model loads on screen. Camera works.

- Add dependencies (`three`, `@react-three/fiber`, `@react-three/drei`, `zustand`).
- Add `SpatialViewer.tsx` rendered behind a new `view=spatial` tab in `App.tsx`.
- Implement `SceneRoot` that arranges `EmbedPlate`, N `LayerModule`s, `UnembedPlate`
  vertically along Y, and T `ResidualBus` pipes running through them.
- Implement orbit controls (drei `OrbitControls`) with sane clamps and a reset button.
- Render static labels (component type + id) on each box.
- Use the existing `useLearnData` hook to read `n_layers`, `n_heads`, `n_tokens`
  from the existing package so the scene adapts to any trace. No scene.json yet.

**Done when:** Loading the app shows a spatial model for any of the 6 tasks, the
user can rotate/zoom/pan, and components are labeled. No activations yet.

### Step B — Scene export + activation-driven intensity

**Goal:** Components light up according to actual activation magnitude.

- Build `src/viz/export_scene.py` with the `scene.json` schema from §F.
- Extend `scripts/export_learn_stages.py` (or add a peer) to also emit `scene.json`
  for every task. Regenerate `learn_data/`.
- Extend `useLearnData` to fetch `scene.json` alongside the existing package.
- Map `tick.active_components[i].intensity` to material opacity or emissive color
  on the corresponding mesh. A simple sequential colormap is enough at this stage.
- Static visualization only: the final tick is shown (all components lit at their
  final intensities). No playback animation yet.

**Done when:** On induction, the layer 0 attention block is visibly brighter than
layer 1's MLP (or whichever component the trace data supports). Running with a
different task changes which components light up.

### Step C — Selection + inspector panel

**Goal:** Click a component; see its explanation and key tensors.

- Add zustand `useSpatialStore` with `{selected_id, tick_index, is_playing, speed}`.
- Add raycast-based `onClick` handlers to meshes.
- Add `InspectorPanel` as a right dock. On selection, show:
  - Component label + type + parent breadcrumb.
  - Short summary blurb from the scene package.
  - Reused `StageExplanation` content for the stage that corresponds to the
    selected component (via `stages_ref` and component type).
  - A "View in Streamlit" deep link (existing `next_technical_view` field).
- Hover: show a minimal `HoverTooltip` with the component name.

**Done when:** A learner can click any layer, attn block, or MLP block and read
explanation text describing what it does in this trace.

### Step D — Playback (layer-wise cursor)

**Goal:** Advance a visible cursor layer by layer; below-cursor is active, above
is latent.

- Add `PlaybackBar` with prev/next/play/pause/reset buttons and a speed slider
  (presets 0.5×, 1×, 2×, 4× — ms-per-tick: 3000, 1500, 750, 375).
- Render a `PlaybackCursor` plane at the current tick's Y height.
- Components below the cursor render with full activation-driven intensity;
  components at the cursor are highlighted; components above are at low opacity.
- On play, `requestAnimationFrame`-driven index advance; ref-stored index to avoid
  stale closures.
- Playback stops at final tick; reset returns to first tick.

**Done when:** Pressing play advances the visible computation front from embed to
unembed over a learner-controlled duration; the residual bus visibly "fills."

### Step E — Isolate + focus + camera polish

**Goal:** First-slice viewer feels usable and calm.

- Add `isolate` toggle: fade non-selected components to ~30% opacity.
- Add "focus selected" button that gently dollies the camera to frame the current
  selection without teleporting.
- Add a keyboard shortcut layer (`arrows`, `space`, `r` for reset, `esc` to
  deselect). Document in a hover tooltip on the playback bar.
- Add a loading/error state that keeps the scene visible during refetch.

**Done when:** A user who has not seen the viewer before can complete a minimal
task ("find which head is most active in layer 0 on the induction trace") in
under a minute without instruction beyond the inspector panel.

### Step F — Exploded layer view (slice 2)

Deferred. Prerequisites: A–E stable.

- On double-click or "explode" button, the selected layer's attention block fans
  its H heads along Z; heads become individually selectable tiles with per-head
  activation patterns painted as textures.
- MLP block shifts aside but does not yet explode.
- Implode animation restores the flat layer.

### Step G — Neuron / feature local view (slice 3)

Deferred. Prerequisites: F stable.

- On drill-into-MLP, the MLP block transforms to a neuron grid (top-K by activity).
- Neurons are selectable; inspector shows per-position activation and residual
  contribution.
- Feature labels (from Phase 6 SAE work) can be overlaid later without schema change.

---

## I. Acceptance criteria

Slice 1 is **accepted** when all of the following are true on the induction demo
trace:

1. **Spatial structure is present.** A learner can visually count 2 layers, each
   with an attention block and an MLP block, and see T residual-bus pipes
   connecting embedding to unembedding.
2. **Camera works.** Rotate, zoom, pan, and reset are all functional with no
   visible glitches. No axis flips, no runaway gimbal.
3. **Scene adapts to data.** Switching to a different task (e.g., `sorting`)
   updates the number of layers, heads, and tokens rendered without a code change.
4. **Activations drive intensity.** At least one component's visible intensity
   changes meaningfully between two different traces (e.g., induction vs.
   bracket_match). The color scale is documented in the inspector.
5. **Selection works.** Clicking a layer, attn block, or MLP block opens an
   inspector panel whose text comes from the existing Python-authored stage text.
6. **Playback is decoupled.** The speed slider changes how fast the cursor
   advances; compute speed does not change. Pausing halts the cursor. Reset
   returns to tick 0.
7. **Isolate works.** Toggling isolate on a selected component fades the rest of
   the scene visibly.
8. **No biology, no false claims.** No component is labeled with a biological
   term. All metaphor abstractions (LN, softmax, masking) are surfaced in the
   inspector text of the component where they apply.
9. **Streamlit is untouched.** `app/streamlit_app.py`, `app/views/`, and
   `src/viz/` are not broken. Streamlit Learn Mode and Investigate Mode still run.
10. **Existing Phase 3C legacy viewer still loads.** Users who prefer the flat
    stage player can switch to it from the tab bar.

Acceptance is **rejected** if:

- The viewer shows "auto-play" as the default behavior.
- Components are drawn as organic shapes, glowing brains, or flowing fluids.
- The viewer requires re-running the Python model to change playback speed.
- The viewer renames or re-explains any of the tensors from the activation cache.
  Names must match `docs/architecture/react_learn_mode.md` and `review_notes §16.3`.

---

## J. Non-goals

These are explicitly not part of this phase. Building them now causes drift.

- **Phase 4 interventions.** No ablation, no patching, no runtime steering. Read-only.
- **Phase 5 checkpoint comparison.** No cross-checkpoint view of activations.
- **Phase 6 SAE feature overlay.** Feature labels are a later overlay; the data
  contract reserves a field, nothing more.
- **Phase 8 pretrained-model work.** The viewer is for tiny-transformer traces
  from this repo.
- **Replacing Streamlit.** Investigate Mode stays in Streamlit until a genuine
  gap forces migration.
- **Tokenizer / text rendering.** Token labels are integers with task-specific
  hints. No natural-language rendering layer.
- **Mobile / touch.** Desktop-first. Touch gestures are not required.
- **Accessibility polish beyond basic semantics.** The 3D viewer has limited
  accessible alternatives; Streamlit Investigate Mode is the accessible path.
- **Performance optimization.** T ≤ 32, L ≤ 2, H ≤ 4, 4·d_model = 256. A naive
  R3F scene handles this at 60 FPS on an M1 Air. Do not premature-optimize.
- **Animation polish.** Smooth tween curves, particle effects, audio cues are not
  needed. Functional first.
- **Auth, multi-user, server.** The viewer stays fully static-file driven.
- **Custom input entry.** The user cannot type a custom sequence in slice 1; only
  the pre-exported demo traces are shown. Custom input is a Phase 4+ concern
  because it implies running the model from the frontend.

---

## K. Where this doc stops

This doc defines the architecture and the first three slices. Slice-level
implementation details (exact file contents, exact prop shapes, exact shader
materials) live in the Sonnet handoff brief (`docs/proposals/spatial_viewer_plan.md`).
The handoff is the actionable checklist; this doc is the contract.
