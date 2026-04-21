# Open Questions

Unresolved decisions that need answers before or at the start of the phase they affect.
Format: status, question, why it matters, which phase it blocks.

---

## Q1 — Package manager [RESOLVED — 2026-04-21]

**Question:** `uv`, `poetry`, `pip + venv`, or conda?

**Resolution:** `pip + venv` with a pinned `requirements.txt`. Lowest magic, easiest
to document for learners, no lockfile format bets. Revisit `uv` if install times
become painful in Phase 3+. (Resolved by Opus Phase 1 advisory, §10.2)

---

## Q2 — PyTorch device target [DECIDED — 2026-04-21, not yet enforced]

**Question:** MPS (Apple GPU), CPU-only, or both?

**Decision:** CPU-only for Phase 2 bridge. MPS has silent op fallbacks that complicate
interpretability debugging. Revisit if Phase 4 intervention speed is unacceptable.
(Decided by Opus Phase 1 advisory, §10.2 — enforced when Phase 2 bridge is built)

**Blocks:** Phase 2 (activation capture) and Phase 4 (causal interventions).

---

## Q3 — Python version floor [RESOLVED — 2026-04-21, updated 2026-04-21]

**Question:** Python 3.11 or 3.12?

**Original resolution:** Python 3.11. Conservative, safe for current mlx-lm versions.
Do not chase 3.12 until an mlx release explicitly confirms compatibility.

**Update (Phase 1 implementation):** Python 3.11 is not installed on the host (M1 Air).
Python 3.12.9 is installed. MLX 0.31.1 on PyPI supports Python 3.12 — this is the
explicit confirmation the original resolution required before switching. Project runs
on Python 3.12 in practice. `pyproject.toml` says `requires-python = ">=3.11"`, which
3.12 satisfies. No conflict with the spirit of the original decision.
(Updated by Sonnet Phase 1 pre-implementation check, review_notes.md §11.5)

---

## Q4 — Checkpoint format [OPEN — blocks Phase 5]

**Question:** MLX-native (`.safetensors` via mlx), PyTorch-native, or a neutral `.safetensors` layer?

**Why it matters:** Phase 5 (checkpoint evolution) needs to load multiple checkpoints efficiently. Phase 8 (pretrained bridge) may need to load HuggingFace-compatible weights. Picking the wrong format now means a migration during Phase 5 or 8.

**Blocks:** Phase 5 (checkpoint comparison tools) and Phase 8 (pretrained bridge).

---

## Q5 — Tracing framework [OPEN — PHASE 2 BLOCKER — RESOLVE BEFORE CODING]

**Question:** Custom MLX hooks, PyTorch hooks, or an NNsight-style abstraction?

**Why it matters:** This is the highest-consequence decision in the interpretability stack.
Phase 2 design, Phase 3 visualization, Phase 4 interventions, Phase 6 SAE, and Phase 7
runtime lab all depend on how activations are captured. The wrong choice here spreads
across every subsequent phase.

**Key constraint:** MLX has no `register_forward_hook` equivalent. This is not a minor
difference — it changes which options are viable without touching `transformer.py`.

**Blocks:** Phase 2 (tracing infrastructure). Must be resolved before any Phase 2 code is written.

**Options:**
- **MLX-native with optional cache dict:** Add `return_cache: bool = False` flag to the
  transformer's `__call__`. When set, return `(logits, cache_dict)` where cache_dict
  contains intermediate tensors. No PyTorch dependency; keeps everything in MLX.
  Downside: changes `transformer.py` interface; tracing logic lives inside the model.
- **Wrapper class (preferred if clean):** Create `src/tracing/tracer.py` that wraps the
  existing model, calls forward, and intercepts/captures outputs at each module boundary
  using MLX's functional design. Keeps `transformer.py` unchanged.
- **PyTorch CPU bridge:** Convert MLX weights to PyTorch format; run inference on a
  PyTorch replica with standard `register_forward_hook`. Full hook ecosystem available
  (TransformerLens, nnsight). Adds conversion overhead; adds PyTorch as Phase 2 dependency.
- **NNsight:** Clean API, active development, PyTorch-native. Requires bridge as above.

**Recommended resolution path:** Opus advisory (write the next advisory section in review_notes.md, after §15) before Sonnet codes.

---

## Q6 — Streamlit suitability [OPEN — inform Phase 3 design]

**Question:** Is Streamlit the right tool for layerwise-logit and attention-map views, or will it become a bottleneck?

**Why it matters:** Principle C says visualization is core. If Streamlit's reactive model makes interactive attention maps laggy or awkward, the visualization phase will fight the tool rather than use it. Worth a quick spike before committing Phase 3 scope to Streamlit-first design.

**Blocks:** Phase 3 design (not start, but design). Early validation recommended.

**Options:**
- Streamlit (current plan)
- Gradio (similar simplicity, slightly different model)
- Panel / HoloViews (more power for interactive plots)
- Jupyter + ipywidgets (stays close to analysis context)

---

## Q7 — Repo-name consistency [RESOLVED in Phase 0]

**Question (original):** README showed `glassbox-playground/` while project is `little-giant-circuits`. Which is canonical?

**Resolution:** `little-giant-circuits` is canonical. README repo-tree corrected in Phase 0 implementation. Closed.

---

## Q8 — Phase 0.5 for tooling? [RESOLVED — 2026-04-21]

**Question:** Should CI, formatting, pre-commit hooks, and linting be a small dedicated phase between 0 and 1, or absorbed at the start of Phase 1?

**Resolution:** Phase 1 opener. First two commits of Phase 1 set up ruff + pyright
(strict: false, basic type coverage). No GitHub Actions CI in Phase 1 — smoke test is
Phase 2 scope. Prevents undisciplined first-Python without adding phase overhead.
(Resolved by Opus Phase 1 advisory, §10.2)

---

## Q9 — Activation cache format [OPEN — blocks Phase 2]

**Question:** What is the on-disk and in-memory format for activation caches produced by Phase 2 tracing?

**Why it matters:** Every forward-pass trace generates a cache of intermediate activations.
Phase 3 visualization and Phase 4 interventions both consume this cache. An arbitrary format
chosen during Phase 2 implementation propagates to every downstream phase — migrating all
saved traces later is expensive.

**Blocks:** Phase 2 (tracing infrastructure design). Resolve alongside Q5.

**Scope of the decision:**
- In-memory: what Python structure? (`dict[str, mx.array]`? nested by layer/component?)
- On-disk: how are caches saved? (`.npz`? `.safetensors` per-trace? plain `.npy` per tensor?)
- Metadata: where does metadata live? (which checkpoint, which task, which input, which step?)
- Dtype: `float32` everywhere, or preserve `bfloat16` where MLX uses it?
- Naming convention: how are layers and components named in the cache keys?
  (e.g., `layer.0.attn.scores` vs `blocks[0].attn_scores`)

**Recommended resolution path:** Resolve with Q5 (tracing framework) — the in-memory
format depends on whether MLX arrays are used directly or converted to numpy/torch.
