"""
Static JSON exporter for React Learn Mode.

Converts a saved trace into a self-contained JSON package that React can read
without a Python server. The contract uses semantic numeric arrays (not Plotly
figure specs) with a viz.kind discriminant per stage.

Data contract: docs/architecture/react_learn_mode.md §5.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from src.tracing import ActivationCache
from src.viz.loading import (
    compute_logit_lens,
    residual_norms,
    token_label,
    token_labels,
    load_model,
    load_trace_from_dir,
)
from src.viz.stages import build_stages


# Number of top neurons to export per MLP stage.
# d_model=64 → 4*d_model=256 neurons; top-32 covers the most active ~12%.
_TOP_K_NEURONS = 32

# Number of top-k predictions to include in the logit lens final stage.
_TOP_K_LOGITS = 5


# ---------------------------------------------------------------------------
# Per-stage viz data extractors
# ---------------------------------------------------------------------------

def _viz_tokens(tokens: list[int], task: str, vocab_size: int) -> dict[str, Any]:
    t_labels = token_labels(task, tokens, vocab_size)
    return {
        "kind": "tokens",
        "data": {
            "positions": list(range(len(tokens))),
            "tokens": tokens,
            "token_labels": t_labels,
        },
    }


def _viz_embed_norms(cache: ActivationCache, tokens: list[int], task: str, vocab_size: int) -> dict[str, Any]:
    tok_emb = np.array(cache["embed.tok"])[0]       # (T, d_model)
    pos_emb = np.array(cache["embed.pos"])           # (T, d_model)
    combined = np.array(cache["embed.combined"])[0]  # (T, d_model)
    t_labels = token_labels(task, tokens, vocab_size)
    T = tok_emb.shape[0]
    return {
        "kind": "embed_norms",
        "data": {
            "positions": list(range(T)),
            "token_labels": t_labels,
            "tok_norms": np.linalg.norm(tok_emb, axis=-1).tolist(),
            "pos_norms": np.linalg.norm(pos_emb, axis=-1).tolist(),
            "combined_norms": np.linalg.norm(combined, axis=-1).tolist(),
        },
    }


def _viz_attention_grid(cache: ActivationCache, layer: int, n_heads: int,
                         tokens: list[int], task: str, vocab_size: int) -> dict[str, Any]:
    t_labels = token_labels(task, tokens, vocab_size)
    patterns = []
    for h in range(n_heads):
        pat = np.array(cache[f"blocks.{layer}.attn.pattern"])[0, h]  # (T, T)
        patterns.append(pat.tolist())
    return {
        "kind": "attention_grid",
        "data": {
            "layer": layer,
            "n_heads": n_heads,
            "token_labels": t_labels,
            "patterns": patterns,  # [n_heads][T][T]
        },
    }


def _viz_mlp_heatmap(cache: ActivationCache, layer: int,
                      tokens: list[int], task: str, vocab_size: int) -> dict[str, Any]:
    post = np.array(cache[f"blocks.{layer}.mlp.post"])[0]  # (T, 4*d_model)
    t_labels = token_labels(task, tokens, vocab_size)
    # Select top-k neurons by max abs activation across positions
    max_abs = np.abs(post).max(axis=0)  # (4*d_model,)
    k = min(_TOP_K_NEURONS, post.shape[1])
    top_indices = np.argsort(max_abs)[::-1][:k]
    top_indices_sorted = np.sort(top_indices)
    return {
        "kind": "mlp_heatmap",
        "data": {
            "layer": layer,
            "token_labels": t_labels,
            "top_neuron_indices": top_indices_sorted.tolist(),
            "activations": post[:, top_indices_sorted].tolist(),  # [T][k]
        },
    }


def _viz_resid_norms(cache: ActivationCache, n_layers: int, highlight_layer: int,
                      tokens: list[int], task: str, vocab_size: int) -> dict[str, Any]:
    t_labels = token_labels(task, tokens, vocab_size)
    norms = residual_norms(cache, n_layers)
    return {
        "kind": "resid_norms",
        "data": {
            "highlight_layer": highlight_layer,
            "token_labels": t_labels,
            "stage_names": list(norms.keys()),
            "norms": {k: v.tolist() for k, v in norms.items()},
        },
    }


def _viz_logit_lens(cache: ActivationCache, model, n_layers: int,
                     tokens: list[int], task: str, vocab_size: int) -> dict[str, Any]:
    T = len(tokens)
    t_labels = token_labels(task, tokens, vocab_size)
    per_layer_probs = compute_logit_lens(cache, model, n_layers)  # (n_layers, T, vocab_size)

    actual_nexts = [tokens[i + 1] if i + 1 < T else tokens[i] for i in range(T)]
    actual_next_labels = [token_label(task, t, vocab_size) for t in actual_nexts]

    # P(correct next token) per layer per position
    prob_of_actual_next = []
    for i in range(n_layers):
        row = [float(per_layer_probs[i, t, actual_nexts[t]]) for t in range(T)]
        prob_of_actual_next.append(row)

    # Top-k at final layer for the most interesting position (second-to-last, or 0)
    final_probs = per_layer_probs[-1]  # (T, vocab_size)
    focus_pos = max(0, T - 2)
    top_k = min(_TOP_K_LOGITS, vocab_size)
    top_indices = np.argsort(final_probs[focus_pos])[::-1][:top_k]

    return {
        "kind": "logit_lens",
        "data": {
            "layer_labels": [f"after L{i}" for i in range(n_layers)],
            "token_labels": t_labels,
            "actual_nexts": actual_nexts,
            "actual_next_labels": actual_next_labels,
            "prob_of_actual_next": prob_of_actual_next,  # [n_layers][T]
            "top_k_final": {
                "position": focus_pos,
                "k": top_k,
                "token_ids": top_indices.tolist(),
                "token_labels": [token_label(task, int(i), vocab_size) for i in top_indices],
                "probs": final_probs[focus_pos, top_indices].tolist(),
            },
        },
    }


# ---------------------------------------------------------------------------
# Stage type classification (maps stage index to viz kind)
# ---------------------------------------------------------------------------

def _stage_viz(
    stage_index: int,
    n_layers: int,
    cache: ActivationCache,
    model,
    cfg: dict,
    meta: dict,
) -> dict[str, Any]:
    """Return the viz payload for a given stage index."""
    task: str = meta["task"]
    tokens: list[int] = meta["tokens"]
    n_heads: int = cfg["model"]["n_heads"]
    vocab_size: int = cfg["model"]["vocab_size"]

    # Stage layout: 0=tokens, 1=embed, then per layer: attn/mlp/resid (3 each), then final
    if stage_index == 0:
        return _viz_tokens(tokens, task, vocab_size)

    if stage_index == 1:
        return _viz_embed_norms(cache, tokens, task, vocab_size)

    # Per-layer stages: indices 2 .. 2 + 3*n_layers - 1
    per_layer_start = 2
    final_index = per_layer_start + 3 * n_layers
    if per_layer_start <= stage_index < final_index:
        offset = stage_index - per_layer_start
        layer = offset // 3
        kind_in_layer = offset % 3  # 0=attn, 1=mlp, 2=resid
        if kind_in_layer == 0:
            return _viz_attention_grid(cache, layer, n_heads, tokens, task, vocab_size)
        if kind_in_layer == 1:
            return _viz_mlp_heatmap(cache, layer, tokens, task, vocab_size)
        # kind_in_layer == 2
        return _viz_resid_norms(cache, n_layers, layer, tokens, task, vocab_size)

    # Final stage
    return _viz_logit_lens(cache, model, n_layers, tokens, task, vocab_size)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_stages(trace_dir: Path, out_path: Path) -> dict[str, Any]:
    """Export a trace as a React-ready JSON package.

    Loads the trace, calls build_stages() for text fields, computes raw array
    viz data independently, and writes a self-contained JSON package.

    Args:
        trace_dir: Directory containing activations.safetensors + trace_meta.json.
        out_path:  Destination .json file path.

    Returns:
        The package dict (also written to out_path).
    """
    cache, meta = load_trace_from_dir(trace_dir)
    ckpt_dir = Path(meta["checkpoint_dir"])
    model, cfg = load_model(ckpt_dir)

    n_layers: int = cfg["model"]["n_layers"]
    n_heads: int = cfg["model"]["n_heads"]
    d_model: int = cfg["model"]["d_model"]
    vocab_size: int = cfg["model"]["vocab_size"]
    task: str = meta["task"]
    tokens: list[int] = meta["tokens"]

    t_labels = token_labels(task, tokens, vocab_size)

    # Build stages for text fields only (figures are ignored here)
    stages_obj = build_stages(cache, model, cfg, meta)

    stages_out = []
    for stage in stages_obj:
        viz = _stage_viz(stage.index, n_layers, cache, model, cfg, meta)
        stages_out.append({
            "index": stage.index,
            "name": stage.name,
            "explanation": stage.explanation,
            "what_changed": stage.what_changed,
            "what_to_notice": stage.what_to_notice,
            "next_technical_view": stage.next_technical_view,
            "viz": viz,
        })

    package: dict[str, Any] = {
        "task": task,
        "trace_id": trace_dir.name,
        "n_tokens": len(tokens),
        "n_layers": n_layers,
        "n_heads": n_heads,
        "d_model": d_model,
        "vocab_size": vocab_size,
        "token_labels": t_labels,
        "stages": stages_out,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(package, indent=2))
    return package
