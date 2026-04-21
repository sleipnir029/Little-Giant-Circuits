"""
Layer Overview — where does the residual stream change most?

This view answers: which layer is doing the most computational work?

The residual stream is the central highway of the transformer. At each layer,
attention and MLP each add a contribution vector to the stream. The L2 norm at
each stage tells you roughly how much "energy" the residual stream carries at
that point.

What to look for:
  - Large norm jump after a layer's MLP → that MLP is dominating computation.
  - Small jump after an attention sublayer → attention may be routing rather than
    computing (which is common in well-studied heads like "previous-token" heads).
  - Near-flat norms across layers → the model may be mostly relying on embeddings.
"""

import numpy as np
import streamlit as st

from src.tracing import ActivationCache
from src.viz.loading import residual_norms, token_labels
from src.viz.plotting import residual_norms_fig


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

    t_labels = token_labels(task, tokens, vocab_size)

    st.subheader("Layer Overview")
    st.caption(
        "L2 norm of the residual stream at each stage and token position. "
        "A jump after a sublayer means that sublayer added significant magnitude."
    )

    stages = residual_norms(cache, n_layers)
    fig = residual_norms_fig(stages, t_labels)
    st.plotly_chart(fig, use_container_width=True)

    # --- Table: mean norm per stage ---
    with st.expander("Mean norm per stage (averaged over token positions)"):
        rows = [{"stage": name, "mean_norm": f"{norms.mean():.4f}",
                 "max_norm": f"{norms.max():.4f}", "min_norm": f"{norms.min():.4f}"}
                for name, norms in stages.items()]
        st.dataframe(rows, use_container_width=True)

    st.divider()

    # --- Per-position norm breakdown ---
    st.markdown("**Norm at a specific position across all stages**")
    if len(tokens) > 1:
        pos = st.slider("Position", 0, len(tokens) - 1, 0, key="layer_pos_slider")
    else:
        pos = 0
        st.caption("Single-token sequence — position slider hidden.")

    stage_names = list(stages.keys())
    stage_vals = [float(stages[s][pos]) for s in stage_names]

    import plotly.graph_objects as go
    bar_fig = go.Figure(go.Bar(
        x=stage_names,
        y=stage_vals,
        marker_color="steelblue",
        hovertemplate="%{x}<br>norm=%{y:.4f}<extra></extra>",
    ))
    bar_fig.update_layout(
        title=f"Residual stream norm at position {pos} (token={tokens[pos]})",
        xaxis_title="Stage",
        yaxis_title="L2 norm",
        height=300,
        xaxis=dict(tickangle=30),
        margin=dict(l=60, r=20, t=50, b=80),
    )
    st.plotly_chart(bar_fig, use_container_width=True)
