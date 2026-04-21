# Phase 2 — Tracing Foundation

> This file reflects what actually happened, not what was planned.
> Do not pre-fill speculatively.

---

## Overview

**Phase number:** 2
**Phase name:** Tracing Foundation
**Status:** COMPLETE
**Started:** 2026-04-21
**Completed:** 2026-04-21

---

## Goals

*From `PROJECT_PLAN.md §6 Phase 2`:*

- [x] Activation cache system — captures all intermediate tensors per forward pass
- [x] Prompt runner — `trace(model, tokens)` single entry point
- [x] Trace export format — `activations.safetensors` + `trace_meta.json`
- [x] Comparison-ready data structures — `ActivationCache` with dot-key access

**Captures implemented:**
- [x] Token embeddings
- [x] Positional embeddings
- [x] Combined embedding (tok + pos)
- [x] Q, K, V projections per head
- [x] Attention scores (post-causal-mask, pre-softmax)
- [x] Attention patterns (post-softmax weights)
- [x] Attention output (after out-projection)
- [x] Residual stream: pre-block, mid-block (after attn), post-block
- [x] MLP pre-activation (after mlp1, before GELU)
- [x] MLP post-activation (after GELU, before mlp2)
- [x] MLP output contribution
- [x] Final LayerNorm input
- [x] Final logits

---

## What Was Built

### Modified

- `src/models/transformer.py` — added `return_cache: bool = False` to `MultiHeadSelfAttention.__call__`,
  `TransformerBlock.__call__`, and `Transformer.__call__`. When `True`, returns `(output, nested_cache_dict)`.
  The `False` path is byte-for-byte identical to the original — training code is unaffected.

### New Module: `src/tracing/`

- `src/tracing/__init__.py` — public API: `trace`, `ActivationCache`, `save_trace`, `load_trace`
- `src/tracing/cache.py` — `ActivationCache` class; wraps raw nested cache; supports
  TransformerLens-style dot-key access (`cache["blocks.0.attn.scores"]`)
- `src/tracing/tracer.py` — `trace(model, tokens)` function; calls `model(tokens, return_cache=True)`;
  materializes all lazy MLX arrays with `mx.eval` before returning
- `src/tracing/export.py` — `save_trace` / `load_trace`; saves `activations.safetensors`
  + `trace_meta.json` to a caller-specified directory

### New Script

- `scripts/trace_prompt.py` — CLI demo; loads a checkpoint, traces a prompt, prints
  attention patterns as ASCII grids, top-k predictions, residual stream norms, and
  optionally saves the trace with a save/load round-trip verification

---

## Validation Results (induction task)

Run:
```
python scripts/trace_prompt.py --task induction --save traces/induction/demo
```

**Anti-drift check:** PASSED — `model(tokens)` == `trace(model, tokens)[0]` (max diff < 1e-5)

**Save/load round-trip:** PASSED

**Cache inventory:** 29 keys, all correct shapes:
```
embed.tok           (1, 15, 64)
embed.pos           (15, 64)
embed.combined      (1, 15, 64)
blocks.0.resid_pre  (1, 15, 64)
blocks.0.attn.q     (1, 4, 15, 16)
blocks.0.attn.scores (1, 4, 15, 15)   ← post-mask pre-softmax
blocks.0.attn.pattern (1, 4, 15, 15)  ← post-softmax attention weights
... (29 total)
logits              (1, 15, 32)
```

**Induction circuit visible:** Positions 8–14 (second half of `[prefix(8)|prefix(8)][:-1]`):
- Predictions 99%+ correct at all induction positions
- Layer 0, Heads 1–3: attend to position `i−7` at induction position `i` (e.g., q=8 → max key=1, q=14 → max key=7) — a **positional shortcut induction** circuit: the model uses a fixed offset rather than content-based matching. Canonical previous-token heads attend at `i−1`; this offset corresponds to the half-sequence length. Phase 4 activation patching needed to verify whether the mechanism is truly positional or content-sensitive.

---

## Key Decisions Made

### 1. `return_cache` flag over a separate `TracedTransformer`

MLX has no `register_forward_hook`. A separate tracing class would need to re-implement
the forward pass math, creating a silent drift risk. Threading `return_cache=False` through
the existing `__call__` methods keeps one canonical forward pass. The anti-drift test
(`model(x) == trace(x)[0]` bit-for-bit) confirms correctness at runtime.

### 2. TransformerLens-style flat dot-key naming

`cache["blocks.0.attn.scores"]` matches TransformerLens conventions. This makes Phase 3
visualization code independent of the Python nesting structure, and makes it easier to
compare notes with TransformerLens literature and tutorials.

### 3. `scores` vs `pattern` naming

`scores` = post-causal-mask, pre-softmax (what the model "wants" to attend to, before
normalization). `pattern` = post-softmax weights (what it actually attends to). Both are
needed: `scores` reveals raw attention preferences; `pattern` reveals the actual information
routing. Many resources conflate these — this implementation is explicit.

### 4. `mx.eval()` immediately in `trace()`

MLX is lazy. Without explicit evaluation, cache tensors are live computation graph nodes.
If the model is called again (e.g., for a second trace), the graph can be freed, making
cached values stale or causing silent corruption. `mx.eval()` on all cache tensors before
returning prevents this.

### 5. Serialization matches Phase 1 checkpoint conventions

`activations.safetensors` (via `mx.save_safetensors`) + `trace_meta.json` parallels the
Phase 1 checkpoint format (`weights.safetensors` + `meta.json`). Same on-disk pattern,
same load path, no new format bets.

### 6. No PyTorch bridge in Phase 2

MLX tracing with the `return_cache` flag is clean and sufficient for all Phase 2 goals.
PyTorch was not needed. Q2 remains decided (CPU-only for Phase 4 if bridge becomes needed)
but was not implemented here.

---

## What Was Intentionally Left Out

- Streamlit UI (Phase 3)
- Ablation and activation patching (Phase 4)
- PyTorch bridge — not needed for Phase 2
- Sparse autoencoders (Phase 6)
- Pretrained model work (Phase 8)
- Jupyter notebooks — scripts are the deliverable
- Any speculative Phase 3 abstractions pre-built "for convenience"

---

## What Each Captured Tensor Tells You

| Tensor | Shape | Interpretability Use |
|--------|-------|----------------------|
| `embed.tok` | (B, T, d_model) | What the embedding space encodes per token |
| `embed.pos` | (T, d_model) | Positional information injected |
| `blocks.i.attn.q/k/v` | (B, H, T, Dh) | Per-head projections; head specialization |
| `blocks.i.attn.scores` | (B, H, T, T) | Raw attention before normalization |
| `blocks.i.attn.pattern` | (B, H, T, T) | Actual routing weights; circuit identification |
| `blocks.i.resid_pre/mid/post` | (B, T, d_model) | How information accumulates across layers |
| `blocks.i.mlp.pre` | (B, T, 4D) | Which neurons activate before nonlinearity |
| `blocks.i.mlp.post` | (B, T, 4D) | Neuron activations after nonlinearity |
| `blocks.i.mlp.output` | (B, T, d_model) | MLP contribution to residual stream |
| `logits` | (B, T, vocab) | Final token prediction before any sampling |

---

## How Phase 3 Will Use This

Phase 3 (Streamlit visualization) reads `ActivationCache` objects directly via the
dot-key accessor. No format migration needed:
- `cache["blocks.0.attn.pattern"]` → attention heatmap
- `cache["blocks.{i}.resid_post"]` → layerwise residual stream view
- `cache["logits"]` → layerwise logit evolution
- `save_trace` / `load_trace` → pre-computed traces for a run browser

---

## Retrospective

Phase 2 delivered a clean, readable tracing system without any speculative abstractions.
The `return_cache` approach turned out to be the correct choice — the transformer code
remains readable, the anti-drift guarantee is testable, and the named tensors map
directly to interpretability concepts from the mechanistic interpretability literature.

The induction circuit was visible from the first working trace: Layer 0 Heads 1–3
attending at a consistent `i−7` offset (positional shortcut), and near-100% predictions
at induction positions. This is the payoff for building small, readable models from scratch
— you can see exactly what the model computed. Whether the mechanism is truly positional
or content-sensitive requires Phase 4 activation patching to determine; the trace establishes
the correlation, not the cause.

The residual stream norms show a large jump after Layer 0's MLP (1.8 → 27.3), suggesting
the MLP layer is doing substantial work. This is a starting point for Phase 4 ablation
studies.
