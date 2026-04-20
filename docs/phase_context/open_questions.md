# Open Questions

Unresolved decisions that need answers before or at the start of the phase they affect.
Format: status, question, why it matters, which phase it blocks.

---

## Q1 — Package manager [OPEN — blocks Phase 1]

**Question:** `uv`, `poetry`, `pip + venv`, or conda?

**Why it matters:** Affects lockfile format, reproducibility story, and how the MLX + PyTorch coexistence is expressed. MLX releases lag behind latest CPython by weeks; the package manager determines how easy it is to pin a working combination.

**Blocks:** Phase 1 (first `src/` code and dependency manifest).

**Options to consider:**
- `uv` — fast, lockfile-native, growing MLX support
- `poetry` — stable, well-documented, slightly heavier
- `pip + venv` — simplest, least magic, easiest to document for learners

---

## Q2 — PyTorch device target [OPEN — blocks Phase 2]

**Question:** MPS (Apple GPU), CPU-only, or both?

**Why it matters:** Determines whether PyTorch interpretability bridges can run sizable traces on the M1 Air at reasonable speed, or must stay strictly small. MPS support in PyTorch is real but some ops fall back to CPU silently — worth knowing upfront.

**Blocks:** Phase 2 (activation capture) and Phase 4 (causal interventions).

---

## Q3 — Python version floor [OPEN — blocks Phase 1]

**Question:** Python 3.11 or 3.12?

**Why it matters:** MLX versions track closely to CPython releases. Too aggressive a floor (3.13) may exclude recent stable mlx-lm versions. 3.11 is the safe conservative choice; 3.12 is reasonable if mlx-lm compatibility is confirmed.

**Blocks:** Phase 1 (dependency manifest and environment setup).

**Current recommendation:** 3.11 (stated in `docs/ENVIRONMENT.md`, not yet enforced).

---

## Q4 — Checkpoint format [OPEN — blocks Phase 5]

**Question:** MLX-native (`.safetensors` via mlx), PyTorch-native, or a neutral `.safetensors` layer?

**Why it matters:** Phase 5 (checkpoint evolution) needs to load multiple checkpoints efficiently. Phase 8 (pretrained bridge) may need to load HuggingFace-compatible weights. Picking the wrong format now means a migration during Phase 5 or 8.

**Blocks:** Phase 5 (checkpoint comparison tools) and Phase 8 (pretrained bridge).

---

## Q5 — Tracing framework [OPEN — blocks Phase 2]

**Question:** Custom MLX hooks, PyTorch hooks, or an NNsight-style abstraction?

**Why it matters:** This is the highest-consequence decision in the interpretability stack. Phase 2 design, Phase 3 visualization, Phase 4 interventions, Phase 6 SAE, and Phase 7 runtime lab all depend on how activations are captured. The wrong choice here spreads across every subsequent phase.

**Blocks:** Phase 2 (activation cache system).

**Options:**
- Custom MLX: stays on-framework, but more work
- PyTorch hooks: richer ecosystem (TransformerLens, nnsight), requires bridge from MLX training
- NNsight: clean API, active development, PyTorch-native

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

## Q8 — Phase 0.5 for tooling? [OPEN — decide before Phase 1]

**Question:** Should CI, formatting, pre-commit hooks, and linting be a small dedicated phase between 0 and 1, or absorbed at the start of Phase 1?

**Why it matters:** Starting Phase 1 without any linting/formatting means the first real code sets undisciplined precedents. But adding CI setup as a separate gate adds process overhead before anything is built.

**Blocks:** Phase 1 kickoff plan.

**Options:**
- Phase 0.5 — small dedicated tooling phase (ruff, pyright, GitHub Actions smoke test)
- Phase 1 opener — first two commits of Phase 1 set up tooling, then model code follows
- Defer entirely — add tooling reactively when it causes pain

---
