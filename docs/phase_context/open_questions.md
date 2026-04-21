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

## Q5 — Tracing framework [RESOLVED — 2026-04-21]

**Question:** Custom MLX hooks, PyTorch hooks, or an NNsight-style abstraction?

**Resolution:** MLX-native `return_cache` flag threaded through `__call__` in
`MultiHeadSelfAttention`, `TransformerBlock`, and `Transformer`. When `return_cache=True`,
returns `(output, nested_cache_dict)`. Default `return_cache=False` is unchanged — training
code is unaffected. Anti-drift test asserts `model(x) == trace(x)[0]` bit-for-bit.

PyTorch bridge was not needed for Phase 2. If Phase 4 interventions require hook-based
patching that MLX can't support cleanly, revisit Q2 (CPU-only PyTorch device) then.

**Decided by:** Sonnet Phase 2 advisory (review_notes.md §16.2), confirmed by working implementation.

---

## Q6 — Streamlit suitability [RESOLVED — 2026-04-21]

**Question:** Is Streamlit the right tool for layerwise-logit and attention-map views?

**Resolution:** Streamlit is committed for Phase 3. All views are plotly-based
(`st.plotly_chart`), which renders smoothly in Streamlit. For tiny model sizes
(2 layers, 4 heads, T ≤ 32), there are no performance concerns.

Mitigation: `src/viz/plotting.py` has zero streamlit imports. If Phase 5/6 traces
become large enough to stress Streamlit's reactive model (e.g., many checkpoint
comparisons), the presentation layer can be swapped to Gradio or Panel without
touching the analysis functions.

(Resolved by Phase 3 implementation + successful startup validation)

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

## Q9 — Activation cache format [RESOLVED — 2026-04-21]

**Question:** What is the on-disk and in-memory format for activation caches produced by Phase 2 tracing?

**Resolution:**
- **In-memory:** `ActivationCache` — thin wrapper around nested dict; supports `cache["blocks.0.attn.scores"]` dot-key access; `flat()` returns `dict[str, mx.array]` for serialization.
- **On-disk:** `activations.safetensors` (flat tensors via `mx.save_safetensors`) + `trace_meta.json` (checkpoint, task, input tokens, shapes, timestamp, git hash).
- **Dtype:** `float32` throughout (MLX default for this model size).
- **Naming:** TransformerLens-style flat dotted keys: `blocks.{i}.attn.{q|k|v|scores|pattern|output}`, `blocks.{i}.mlp.{pre|post|output}`, `blocks.{i}.resid_{pre|mid|post}`, `embed.{tok|pos|combined}`, `ln_f.input`, `logits`.

**Decided by:** Sonnet Phase 2 advisory (review_notes.md §16.3), confirmed by working implementation + save/load round-trip test.
