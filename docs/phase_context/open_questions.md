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

## Q8 — Phase 0.5 for tooling? [RESOLVED — 2026-04-21]

**Question:** Should CI, formatting, pre-commit hooks, and linting be a small dedicated phase between 0 and 1, or absorbed at the start of Phase 1?

**Resolution:** Phase 1 opener. First two commits of Phase 1 set up ruff + pyright
(strict: false, basic type coverage). No GitHub Actions CI in Phase 1 — smoke test is
Phase 2 scope. Prevents undisciplined first-Python without adding phase overhead.
(Resolved by Opus Phase 1 advisory, §10.2)

---
