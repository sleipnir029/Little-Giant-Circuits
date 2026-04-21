"""
MLP / Activation View — which neurons fire and where?

This view answers: which neurons activate most strongly for each position,
and how does the GELU nonlinearity shape their output?

The MLP in each block applies:
  1. mlp1 (linear): d_model → 4*d_model
  2. GELU nonlinearity: introduces sparse activations
  3. mlp2 (linear): 4*d_model → d_model  (writes back to residual)

We expose two tensors:
  - pre-GELU (mlp.pre): what the linear transformation produces before squashing
  - post-GELU (mlp.post): which neurons are actually "on"

The GELU function is approximately: x if x > 0, ~0 if x << 0. So post-GELU
activation shows which neurons are truly contributing to the MLP output.
Pre-GELU shows the full linear preference, including suppressed neurons.

What to look for:
  - Sparse post-GELU activation → healthy; few neurons do most of the work.
  - Position-selective neurons → some neurons fire only at specific token positions.
  - Layer 0 vs Layer 1 MLP patterns → different layers solve different subproblems.
"""

import numpy as np
import streamlit as st

from src.tracing import ActivationCache
from src.viz.loading import token_labels
from src.viz.plotting import mlp_heatmap, top_neurons_bar


def render(
    cache: ActivationCache,
    meta: dict,
    model,
    cfg: dict,
) -> None:
    task = meta["task"]
    tokens = meta["tokens"]
    n_layers = cfg["model"]["n_layers"]
    vocab_size = cfg["model"]["vocab_size"]
    d_model = cfg["model"]["d_model"]
    hidden_dim = 4 * d_model

    t_labels = token_labels(task, tokens, vocab_size)

    st.subheader("MLP / Activation View")
    st.caption(
        "MLP neuron activations across all token positions. "
        "Pre-GELU = raw linear output. Post-GELU = neurons that are actually on. "
        "Each column is one token position; each row is one neuron."
    )

    col1, col2 = st.columns(2)
    with col1:
        layer = st.selectbox("Layer", list(range(n_layers)), key="mlp_layer")
    with col2:
        stage = st.radio("Stage", ["pre (before GELU)", "post (after GELU)"], key="mlp_stage")

    key_suffix = "pre" if "pre" in stage else "post"
    cache_key = f"blocks.{layer}.mlp.{key_suffix}"
    activations = np.array(cache[cache_key])[0]     # (T, hidden_dim)

    fig = mlp_heatmap(
        activations,
        t_labels,
        title=f"Layer {layer} MLP — {key_suffix}-GELU activations",
        max_neurons=64,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Only the top 64 most active neurons are shown (by max absolute activation across positions). "
        "Post-GELU values are ≥ 0 for neurons with positive pre-activations."
    )

    st.divider()

    # --- Per-position top-neuron bar chart ---
    st.markdown("**Top activated neurons at a single position**")
    if len(tokens) > 1:
        pos = st.slider("Position", 0, len(tokens) - 1, 0, key="mlp_pos_slider")
    else:
        pos = 0
        st.caption("Single-token sequence — position slider hidden.")
    top_k = st.slider("Show top-k neurons", 8, min(32, hidden_dim), 16, key="mlp_topk")

    bar_fig = top_neurons_bar(
        activations,
        position=pos,
        top_k=top_k,
        title=f"Layer {layer} MLP {key_suffix}-GELU — pos {pos} (token={tokens[pos]})",
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    st.caption(
        "Blue bars = positive activations (neuron is on), "
        "red bars = negative (only possible pre-GELU; post-GELU is always ≥ 0 for large positive inputs)."
    )

    # --- MLP output contribution ---
    with st.expander("MLP output contribution to residual stream"):
        mlp_out = np.array(cache[f"blocks.{layer}.mlp.output"])[0]   # (T, d_model)
        out_norms = np.linalg.norm(mlp_out, axis=-1)

        import plotly.graph_objects as go
        norm_fig = go.Figure(go.Bar(
            x=t_labels,
            y=out_norms.tolist(),
            marker_color="mediumseagreen",
            hovertemplate="pos=%{x}<br>‖mlp_out‖=%{y:.4f}<extra></extra>",
        ))
        norm_fig.update_layout(
            title=f"Layer {layer} MLP output ‖ · ‖ per position",
            xaxis_title="Token position",
            yaxis_title="L2 norm of MLP contribution",
            height=280,
            margin=dict(l=60, r=20, t=50, b=60),
        )
        st.plotly_chart(norm_fig, use_container_width=True)
        st.caption(
            "This is how much the MLP layer added to the residual stream at each position. "
            "High norm = MLP did substantial work here."
        )
