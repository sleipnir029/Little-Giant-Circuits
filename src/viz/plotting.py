"""
Plotting helpers for Phase 3 visualization.

Pure functions — no streamlit imports. Each function returns a plotly Figure.
Streamlit views call st.plotly_chart(fig, use_container_width=True).

Phase 4/5 scripts can import these directly without pulling in streamlit.
"""

import numpy as np
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Attention view
# ---------------------------------------------------------------------------

def attention_heatmap(
    pattern: np.ndarray,
    token_labels: list[str],
    title: str = "",
) -> go.Figure:
    """Attention pattern heatmap for one head.

    Args:
        pattern:      (T, T) float array — rows=query positions, cols=key positions.
                      Values are post-softmax attention weights (sum to 1 per row).
        token_labels: T labels for both axes.
        title:        Figure title.

    Educational purpose: shows where each query token is routing attention.
    A strong off-diagonal block reveals which positions each head copies from.
    """
    T = len(token_labels)
    positions = list(range(T))
    fig = go.Figure(go.Heatmap(
        z=pattern,
        x=positions,
        y=positions,
        colorscale="Blues",
        zmin=0.0,
        zmax=1.0,
        showscale=True,
        colorbar=dict(title="Weight", thickness=12),
        hovertemplate="query=%{y}<br>key=%{x}<br>weight=%{z:.3f}<extra></extra>",
    ))
    tick_vals = positions
    fig.update_layout(
        title=title,
        xaxis_title="Key position (attended to)",
        yaxis_title="Query position (attending from)",
        xaxis=dict(tickmode="array", tickvals=tick_vals, ticktext=token_labels),
        yaxis=dict(tickmode="array", tickvals=tick_vals, ticktext=token_labels, autorange="reversed"),
        height=350,
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


# ---------------------------------------------------------------------------
# Residual stream norms
# ---------------------------------------------------------------------------

def residual_norms_fig(
    stages: dict[str, np.ndarray],
    token_labels: list[str],
) -> go.Figure:
    """Line chart of residual stream L2 norms across stages.

    Args:
        stages:       Dict mapping stage name → (T,) array of L2 norms per token.
                      Keys like "embed", "L0.resid_pre", "L0.resid_post", etc.
        token_labels: T labels for the x-axis.

    Educational purpose: shows which stages add the most "magnitude" to the
    residual stream. A large jump after a layer's MLP means the MLP is doing
    substantial computation. Near-zero change means that layer is mostly bypassed.
    """
    fig = go.Figure()
    for stage, norms in stages.items():
        fig.add_trace(go.Scatter(
            x=list(range(len(norms))),
            y=norms.tolist(),
            mode="lines+markers",
            name=stage,
            hovertemplate=f"{stage}<br>pos=%{{x}}<br>norm=%{{y:.3f}}<extra></extra>",
        ))
    fig.update_layout(
        title="Residual Stream L2 Norm per Token Position",
        xaxis=dict(tickmode="array", tickvals=list(range(len(token_labels))), ticktext=token_labels),
        yaxis_title="L2 norm",
        height=380,
        legend=dict(orientation="v", x=1.02, xanchor="left"),
        margin=dict(l=60, r=160, t=50, b=60),
    )
    return fig


# ---------------------------------------------------------------------------
# MLP activations
# ---------------------------------------------------------------------------

def mlp_heatmap(
    activations: np.ndarray,
    token_labels: list[str],
    title: str = "",
    max_neurons: int = 64,
) -> go.Figure:
    """Heatmap of MLP neuron activations across token positions.

    Args:
        activations:  (T, hidden_dim) float array.
        token_labels: T labels for the x-axis.
        title:        Figure title.
        max_neurons:  Cap the display to this many neurons (top by max abs activation).

    Educational purpose: shows which neurons fire most strongly for each token position.
    Bright cells = large activation. Post-GELU activations are always >= 0 (GELU output
    is non-negative for large positive inputs and near-zero for negative inputs), so
    bright = that neuron is "on" for that position.
    """
    T, hidden_dim = activations.shape

    # Show only the most active neurons to avoid visual noise
    if hidden_dim > max_neurons:
        neuron_max = np.abs(activations).max(axis=0)      # (hidden_dim,)
        top_idx = np.argsort(neuron_max)[::-1][:max_neurons]
        activations = activations[:, top_idx]
        yaxis_title = f"Neuron index (top {max_neurons} by max |activation|)"
    else:
        top_idx = np.arange(hidden_dim)
        yaxis_title = "Neuron index"

    x_positions = list(range(T))
    fig = go.Figure(go.Heatmap(
        z=activations.T,                  # rows=neurons, cols=positions
        x=x_positions,
        y=[str(int(i)) for i in top_idx],
        colorscale="RdBu_r",
        zmid=0,
        showscale=True,
        colorbar=dict(title="Act.", thickness=12),
        hovertemplate="pos=%{x}<br>neuron=%{y}<br>act=%{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Token position",
        xaxis=dict(tickmode="array", tickvals=x_positions, ticktext=token_labels),
        yaxis_title=yaxis_title,
        height=420,
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


def top_neurons_bar(
    activations: np.ndarray,
    position: int,
    top_k: int = 16,
    title: str = "",
) -> go.Figure:
    """Bar chart of the most active neurons at a single token position.

    Args:
        activations: (T, hidden_dim) float array.
        position:    Token position to inspect.
        top_k:       Number of top neurons to show.
        title:       Figure title.
    """
    acts = activations[position]                          # (hidden_dim,)
    top_idx = np.argsort(np.abs(acts))[::-1][:top_k]
    top_vals = acts[top_idx]

    colors = ["steelblue" if v >= 0 else "salmon" for v in top_vals]
    fig = go.Figure(go.Bar(
        x=[str(i) for i in top_idx],
        y=top_vals.tolist(),
        marker_color=colors,
        hovertemplate="neuron=%{x}<br>act=%{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title=title or f"Top {top_k} neurons at position {position}",
        xaxis_title="Neuron index",
        yaxis_title="Activation",
        height=300,
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


# ---------------------------------------------------------------------------
# Token prediction view
# ---------------------------------------------------------------------------

def top_k_bar(
    probs: np.ndarray,
    top_k: int = 8,
    actual_next: int | None = None,
    title: str = "",
) -> go.Figure:
    """Bar chart of top-k predicted token probabilities at one position.

    Args:
        probs:       (vocab_size,) softmax probability array.
        top_k:       Number of tokens to show.
        actual_next: If given, marks the actual next token in red.
        title:       Figure title.
    """
    top_idx = np.argsort(probs)[::-1][:top_k]
    top_probs = probs[top_idx]

    colors = []
    for i in top_idx:
        if actual_next is not None and i == actual_next:
            colors.append("firebrick")
        else:
            colors.append("steelblue")

    fig = go.Figure(go.Bar(
        x=[str(int(i)) for i in top_idx],
        y=top_probs.tolist(),
        marker_color=colors,
        hovertemplate="token=%{x}<br>prob=%{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Token ID",
        yaxis_title="Probability",
        yaxis=dict(range=[0, 1]),
        height=280,
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


# ---------------------------------------------------------------------------
# Logit evolution (logit lens)
# ---------------------------------------------------------------------------

def logit_evolution_heatmap(
    per_layer_probs: np.ndarray,
    token_labels: list[str],
    layer_labels: list[str],
    target_tokens: list[int] | None = None,
) -> go.Figure:
    """Heatmap showing how target-token confidence builds across layers.

    Args:
        per_layer_probs: (n_layers, T, vocab_size) — softmax probabilities per layer.
        token_labels:    T token label strings for the x-axis.
        layer_labels:    Layer name strings for the y-axis.
        target_tokens:   (T,) index of the "target" token per position. If None, uses
                         the final layer's argmax (what the model predicts).

    Educational purpose: implements the logit lens (Nostalgebraist 2020). Each cell
    shows how confident the model is about its final prediction at that layer. A cell
    that lights up early (low layer) means the residual stream already "contains" the
    answer by then. Dark early cells mean the computation needed multiple layers.
    """
    n_layers, T, vocab = per_layer_probs.shape

    if target_tokens is None:
        target_tokens = np.argmax(per_layer_probs[-1], axis=-1).tolist()

    # z[layer, pos] = probability of target_tokens[pos] at that layer
    z = np.array([
        [float(per_layer_probs[layer, pos, target_tokens[pos]]) for pos in range(T)]
        for layer in range(n_layers)
    ])

    target_labels = [f"{token_labels[t]}→{target_tokens[t]}" for t in range(T)]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=target_labels,
        y=layer_labels,
        colorscale="Viridis",
        zmin=0.0,
        zmax=1.0,
        showscale=True,
        colorbar=dict(title="P(target)", thickness=12),
        hovertemplate="layer=%{y}<br>pos=%{x}<br>P(target)=%{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title="Logit Lens: P(predicted token) at each layer",
        xaxis_title="Position → predicted token",
        yaxis_title="Layer",
        yaxis=dict(autorange="reversed"),
        height=320,
        margin=dict(l=60, r=20, t=50, b=80),
    )
    return fig


def logit_evolution_line(
    per_layer_probs: np.ndarray,
    layer_labels: list[str],
    position: int,
    top_k: int = 5,
    token_labels_vocab: list[str] | None = None,
) -> go.Figure:
    """Line chart showing how top-k token probabilities change across layers at one position.

    Args:
        per_layer_probs:    (n_layers, T, vocab_size) array.
        layer_labels:       Layer name strings.
        position:           Token position to inspect.
        top_k:              Number of top tokens to trace.
        token_labels_vocab: Optional list of vocab_size strings for token labels.
    """
    # Identify top-k tokens by final-layer probability
    final_probs = per_layer_probs[-1, position, :]           # (vocab,)
    top_idx = np.argsort(final_probs)[::-1][:top_k]

    fig = go.Figure()
    for token_id in top_idx:
        label = (token_labels_vocab[token_id] if token_labels_vocab else str(token_id))
        trace_probs = per_layer_probs[:, position, token_id]  # (n_layers,)
        fig.add_trace(go.Scatter(
            x=layer_labels,
            y=trace_probs.tolist(),
            mode="lines+markers",
            name=f"tok {label}",
        ))

    fig.update_layout(
        title=f"Token probability evolution at position {position}",
        xaxis_title="Layer",
        yaxis_title="Probability",
        yaxis=dict(range=[0, 1]),
        height=300,
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig
