"""
Stage-based narrative decomposition of a transformer forward pass.

Each Stage represents one conceptual computation step (embed, attention, MLP,
residual, prediction). Stages carry:
  - plain-language explanation text
  - a focused Plotly figure showing one aspect of the computation
  - links to the corresponding Investigate Mode view

This module is streamlit-free. It returns data; the learn mode UI renders it.

Usage:
    stages = build_stages(cache, model, cfg, meta)
    stage = stages[2]  # Layer 0 — Attention
    fig = stage.figure
    print(stage.what_to_notice)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import plotly.graph_objects as go

from src.tracing import ActivationCache
from src.viz.loading import (
    compute_logit_lens,
    residual_norms,
    token_labels,
    token_label,
)
from src.viz.plotting import (
    attention_heatmap,
    residual_norms_fig,
    mlp_heatmap,
    top_k_bar,
    logit_evolution_heatmap,
)


@dataclass
class Stage:
    """One step in the forward-pass narrative."""
    index: int
    name: str
    explanation: str
    what_changed: str
    what_to_notice: str
    next_technical_view: str   # name of the Investigate Mode view to open next
    figure: Optional[go.Figure] = None


# ---------------------------------------------------------------------------
# Per-stage figure builders
# ---------------------------------------------------------------------------

def _token_sequence_fig(tokens: list[int], task: str, vocab_size: int) -> go.Figure:
    """Simple bar-like display of the input token sequence."""
    labels = token_labels(task, tokens, vocab_size)
    fig = go.Figure(go.Bar(
        x=list(range(len(tokens))),
        y=[1] * len(tokens),
        text=labels,
        textposition="inside",
        hovertemplate="pos %{x}: token %{text}<extra></extra>",
        marker_color="steelblue",
    ))
    fig.update_layout(
        title="Input token sequence",
        xaxis_title="Position",
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        height=220,
        margin=dict(l=40, r=20, t=50, b=40),
        showlegend=False,
    )
    return fig


def _embed_norms_fig(cache: ActivationCache) -> go.Figure:
    """Show token vs positional embedding magnitudes per position."""
    tok_emb = np.array(cache["embed.tok"])[0]       # (T, d_model)
    pos_emb = np.array(cache["embed.pos"])           # (T, d_model)
    combined = np.array(cache["embed.combined"])[0]  # (T, d_model)

    T = tok_emb.shape[0]
    x = list(range(T))

    tok_norms = np.linalg.norm(tok_emb, axis=-1)
    pos_norms = np.linalg.norm(pos_emb, axis=-1)
    combined_norms = np.linalg.norm(combined, axis=-1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=tok_norms.tolist(), mode="lines+markers",
                             name="Token emb", line=dict(color="steelblue")))
    fig.add_trace(go.Scatter(x=x, y=pos_norms.tolist(), mode="lines+markers",
                             name="Pos emb", line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=x, y=combined_norms.tolist(), mode="lines+markers",
                             name="Combined", line=dict(color="green", dash="dash")))
    fig.update_layout(
        title="Embedding L2 norms per position",
        xaxis_title="Position",
        yaxis_title="L2 norm",
        height=280,
        margin=dict(l=60, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def _all_heads_fig(
    cache: ActivationCache,
    layer: int,
    n_heads: int,
    t_labels: list[str],
) -> go.Figure:
    """Grid of all heads in one layer as a single figure (subplots)."""
    from plotly.subplots import make_subplots

    cols = min(n_heads, 4)
    rows = (n_heads + cols - 1) // cols
    titles = [f"L{layer} H{h}" for h in range(n_heads)]
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=titles)

    for h in range(n_heads):
        pat = np.array(cache[f"blocks.{layer}.attn.pattern"])[0, h]  # (T, T)
        row = h // cols + 1
        col = h % cols + 1
        fig.add_trace(
            go.Heatmap(
                z=pat.tolist(),
                x=t_labels,
                y=t_labels,
                colorscale="Blues",
                showscale=(h == 0),
                hovertemplate="query %{y} → key %{x}<br>weight=%{z:.3f}<extra></extra>",
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        title=f"Layer {layer} — all {n_heads} attention heads",
        height=max(280, 260 * rows),
        margin=dict(l=40, r=20, t=80, b=40),
    )
    return fig


def _resid_norms_layer_fig(
    cache: ActivationCache,
    n_layers: int,
    t_labels: list[str],
    highlight_layer: Optional[int] = None,
) -> go.Figure:
    """Residual norms line chart, optionally highlighting one layer's contribution."""
    stages = residual_norms(cache, n_layers)
    fig = residual_norms_fig(stages, t_labels)
    if highlight_layer is not None:
        # Add vertical annotation band is not straightforward in plotly line charts;
        # instead add a note in the title.
        title = fig.layout.title.text or ""
        fig.update_layout(title=f"{title} — Layer {highlight_layer} highlighted")
    return fig


def _mlp_layer_fig(
    cache: ActivationCache,
    layer: int,
    t_labels: list[str],
) -> go.Figure:
    """MLP activation heatmap for one layer (post-GELU)."""
    post = np.array(cache[f"blocks.{layer}.mlp.post"])[0]  # (T, 4*d_model)
    return mlp_heatmap(post, t_labels, title=f"Layer {layer} MLP — post-GELU activations")


def _prediction_fig(
    cache: ActivationCache,
    tokens: list[int],
    task: str,
    vocab_size: int,
) -> go.Figure:
    """Top-k prediction bar for the last meaningful position."""
    logits_np = np.array(cache["logits"])[0]          # (T, vocab)
    exp_logits = np.exp(logits_np - logits_np.max(axis=-1, keepdims=True))
    probs_all = exp_logits / exp_logits.sum(axis=-1, keepdims=True)

    # Use last position or most interesting: the position before the last token
    T = len(tokens)
    pos = max(0, T - 2)  # second-to-last: predicts the final token
    probs = probs_all[pos]
    actual_next = tokens[pos + 1] if pos + 1 < T else None

    top_k = min(8, vocab_size)
    return top_k_bar(
        probs,
        top_k=top_k,
        actual_next=actual_next,
        title=f"Model's top-{top_k} predictions at position {pos}",
    )


# ---------------------------------------------------------------------------
# Stage builder
# ---------------------------------------------------------------------------

def build_stages(
    cache: ActivationCache,
    model,
    cfg: dict,
    meta: dict,
) -> list[Stage]:
    """Build the ordered list of narrative Stages from a trace.

    Produces 9 stages for a 2-layer model. For n_layers != 2, the
    per-layer stages are generated dynamically (3 stages per layer).
    """
    task: str = meta["task"]
    tokens: list[int] = meta["tokens"]
    n_layers: int = cfg["model"]["n_layers"]
    n_heads: int = cfg["model"]["n_heads"]
    vocab_size: int = cfg["model"]["vocab_size"]
    d_model: int = cfg["model"]["d_model"]

    t_labels = token_labels(task, tokens, vocab_size)
    stages: list[Stage] = []
    idx = 0

    # ------------------------------------------------------------------
    # Stage 0 — Input Tokens
    # ------------------------------------------------------------------
    stages.append(Stage(
        index=idx,
        name="Step 1: Input Tokens",
        explanation=(
            f"The input is a sequence of {len(tokens)} integer tokens. "
            f"Each integer is an index into a vocabulary of {vocab_size} possible values — "
            "like an ID in a lookup table rather than a human-readable word. "
            f"This model was trained on the **{task}** task, where the token sequence has a "
            "specific structural meaning."
        ),
        what_changed="Nothing has been computed yet. This is the raw input.",
        what_to_notice=(
            "Look at the sequence structure. "
            + {
                "induction": "The sequence repeats a pattern: [A, B, ..., A, B, ...]. After seeing A again, the model should predict B.",
                "kv_retrieval": "Key-value pairs appear at the start (k1, v1, k2, v2, ...), then a query key. The model must retrieve the matching value.",
                "modular_arith": "Two integers: a and b. The model predicts (a + b) mod p.",
                "bracket_match": "( = token 1, ) = token 2. The model predicts whether each position should be open or close.",
                "factual_lookup": "A single token: a 'subject'. The model must return its memorized 'attribute'.",
                "sorting": "Unsorted integers, then a SEP token, then... the model should output the sorted sequence.",
            }.get(task, "Observe the length and token range.")
        ),
        next_technical_view="Token Overview",
        figure=_token_sequence_fig(tokens, task, vocab_size),
    ))
    idx += 1

    # ------------------------------------------------------------------
    # Stage 1 — Embeddings
    # ------------------------------------------------------------------
    stages.append(Stage(
        index=idx,
        name="Step 2: Embeddings — Tokens Become Vectors",
        explanation=(
            f"Each token ID is looked up in an **embedding table** to get a {d_model}-dimensional vector. "
            "A separate **positional embedding** is added to each vector so the model knows where in the "
            "sequence each token sits. These two are summed together before entering the transformer blocks. "
            "At this point, every token has an independent representation — no information has been "
            "shared between positions yet."
        ),
        what_changed=(
            f"Tokens went from integers to {d_model}-dimensional floating-point vectors. "
            "This is the only place where the raw input is converted into the model's internal representation."
        ),
        what_to_notice=(
            "The embedding norms. Token embeddings and positional embeddings contribute different magnitudes. "
            "If the positional norm is much smaller than the token norm, position information starts weak "
            "and must be amplified by attention. "
            "The combined norm is the starting 'energy' in the residual stream."
        ),
        next_technical_view="Layer Overview",
        figure=_embed_norms_fig(cache),
    ))
    idx += 1

    # ------------------------------------------------------------------
    # Per-layer stages: Attention → MLP → Residual
    # ------------------------------------------------------------------
    for layer in range(n_layers):
        ordinal = ["first", "second", "third", "fourth"][layer] if layer < 4 else f"layer {layer}"

        # --- Attention ---
        stages.append(Stage(
            index=idx,
            name=f"Step {idx + 1}: Layer {layer} — Attention",
            explanation=(
                f"This is the **{ordinal} attention layer**. "
                "Attention allows each position to gather information from other positions in the sequence. "
                f"It uses {n_heads} attention heads, each learning a different pattern of information routing. "
                "Each head computes Q (query), K (key), V (value) projections, then attends based on "
                "Q·K similarity. The output is a weighted sum of V vectors — the information each "
                "position collects from across the sequence."
            ),
            what_changed=(
                "Information can now flow between positions for the first time. "
                "Before attention, each position only knew its own embedding. "
                "After attention, each position's representation includes contributions from other positions."
            ),
            what_to_notice=(
                "The attention patterns (the heatmaps below). "
                "Each row is a query position; each column is a key position. "
                "Bright = high attention weight. "
                + (
                    "For the induction task: look for a **previous-token head** (bright diagonal offset by 1) "
                    "and an **induction head** (bright where the same token appeared earlier)."
                    if task == "induction" else
                    "Look for structured patterns vs. uniform attention. "
                    "Uniform attention means the head isn't doing selective routing — it's averaging."
                )
            ),
            next_technical_view="Attention",
            figure=_all_heads_fig(cache, layer, n_heads, t_labels),
        ))
        idx += 1

        # --- MLP ---
        stages.append(Stage(
            index=idx,
            name=f"Step {idx + 1}: Layer {layer} — MLP Transformation",
            explanation=(
                f"After attention, a **feed-forward network (MLP)** processes each position independently. "
                f"It expands to {4 * d_model} dimensions, applies a GELU nonlinearity, then projects back to {d_model}. "
                "Unlike attention, the MLP cannot move information between positions — it applies the same "
                "learned function to every position's representation separately. "
                "MLPs are sometimes described as 'key-value memories': certain input patterns activate "
                "specific neurons, which then contribute specific values to the residual stream."
            ),
            what_changed=(
                "Each position's vector has been transformed by a learned nonlinear function. "
                "The MLP adds a new contribution to the residual stream."
            ),
            what_to_notice=(
                "Which neurons (columns) activate most strongly and at which positions (rows). "
                "Neurons with large post-GELU values are 'detecting' something about that position's current representation. "
                + (
                    "For key-value retrieval, look for neurons that activate strongly at the query position — "
                    "they may be doing the 'lookup' computation."
                    if task == "kv_retrieval" else
                    "Compare neurons across positions. If the same neurons fire for similar tokens, "
                    "those neurons are encoding a shared feature."
                )
            ),
            next_technical_view="MLP Activations",
            figure=_mlp_layer_fig(cache, layer, t_labels),
        ))
        idx += 1

        # --- Residual Stream ---
        stages.append(Stage(
            index=idx,
            name=f"Step {idx + 1}: After Layer {layer} — Residual Stream",
            explanation=(
                "The **residual stream** is the central information highway of the transformer. "
                "After each attention and MLP sublayer, their outputs are **added** to the stream "
                "(not replacing it). This means information accumulates additively across layers. "
                f"After layer {layer}, the stream contains: original embedding + attention output + MLP output "
                + (f"from all {layer + 1} layer(s) so far." if layer > 0 else "from layer 0.")
            ),
            what_changed=(
                f"Layer {layer}'s full computation (attention + MLP) has been added to the residual stream. "
                "The stream now has more information than it did before this layer."
            ),
            what_to_notice=(
                "The L2 norm per position. A large norm jump compared to the previous stage means "
                f"layer {layer} contributed significant 'energy' to that position's representation. "
                "Positions that the model will predict correctly often show higher norm growth — "
                "the model is 'building up' the answer in those positions."
            ),
            next_technical_view="Layer Overview",
            figure=_resid_norms_layer_fig(cache, n_layers, t_labels, highlight_layer=layer),
        ))
        idx += 1

    # ------------------------------------------------------------------
    # Final stage — Prediction
    # ------------------------------------------------------------------
    per_layer_probs = compute_logit_lens(cache, model, n_layers)
    T = len(tokens)
    actual_nexts = [tokens[i + 1] if i + 1 < T else tokens[i] for i in range(T)]

    stages.append(Stage(
        index=idx,
        name=f"Step {idx + 1}: Final Prediction",
        explanation=(
            "The residual stream is passed through a **final LayerNorm** (scaling and centering), "
            "then a **linear projection** converts it to vocabulary logits — one number per token in the vocabulary. "
            "**Softmax** turns these into probabilities. The token with the highest probability is the "
            "model's prediction at each position. "
            "For the logit lens view, we can also ask: 'what would the model have predicted after each "
            "earlier layer?' — revealing when the correct answer was first encoded."
        ),
        what_changed=(
            "The residual stream has been projected from "
            f"{d_model} internal dimensions into {vocab_size} vocabulary logits. "
            "The model's answer is now readable as a probability distribution."
        ),
        what_to_notice=(
            "How confident the model is at the final layer (tall dominant bar = confident). "
            "Compare with the logit lens heatmap: does the model 'know' the answer after layer 0, "
            "or does it only emerge in the final layer? "
            + (
                "For the induction task, the second half of the sequence (induction positions) "
                "should show near-100% confidence. The first half should be uncertain."
                if task == "induction" else
                f"For the {task} task at ~"
                + {"kv_retrieval": "97%", "sorting": "100%", "modular_arith": "99%",
                   "bracket_match": "68%", "factual_lookup": "100%"}.get(task, "?")
                + " accuracy, look for which positions show high confidence."
            )
        ),
        next_technical_view="Logit Evolution",
        figure=logit_evolution_heatmap(per_layer_probs, t_labels,
                                       [f"after L{i}" for i in range(n_layers)],
                                       actual_nexts),
    ))

    return stages
