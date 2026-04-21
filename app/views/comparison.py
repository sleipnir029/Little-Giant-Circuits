"""
Comparison View — side-by-side trace inspection.

This view renders the same visualization twice, side by side, for two different
traces. It does not compute a diff — that complexity belongs to Phase 5.

The purpose is qualitative: does a different prompt activate the same heads?
Does a different task use the residual stream differently? Does changing one
input token shift the logit evolution?

Comparison mode reuses the same view functions from the other modules.
No new visualization primitives are needed.
"""

import numpy as np
import streamlit as st

from src.tracing import ActivationCache
from src.viz.loading import residual_norms, token_labels
from src.viz.plotting import attention_heatmap, residual_norms_fig


def render(
    cache_a: ActivationCache,
    meta_a: dict,
    cache_b: ActivationCache,
    meta_b: dict,
    model,
    cfg: dict,
) -> None:
    task = meta_a["task"]
    n_layers = cfg["model"]["n_layers"]
    n_heads = cfg["model"]["n_heads"]
    vocab_size = cfg["model"]["vocab_size"]

    st.subheader("Compare Traces")
    st.caption(
        "Side-by-side view of two traces. "
        "Select a view type and a layer/head to compare. "
        "No diff is computed — this is a visual comparison."
    )

    view_type = st.selectbox(
        "Compare what?",
        ["Attention patterns", "Residual norms", "Logit distributions"],
        key="cmp_view",
    )

    col_a, col_b = st.columns(2)

    tokens_a = meta_a["tokens"]
    tokens_b = meta_b["tokens"]
    t_labels_a = token_labels(task, tokens_a, vocab_size)
    t_labels_b = token_labels(task, tokens_b, vocab_size)

    with col_a:
        st.markdown("**Trace A**")
        st.caption(f"Tokens: `{tokens_a}`")
    with col_b:
        st.markdown("**Trace B**")
        st.caption(f"Tokens: `{tokens_b}`")

    if view_type == "Attention patterns":
        layer = st.selectbox("Layer", list(range(n_layers)), key="cmp_layer")
        head = st.selectbox("Head", list(range(n_heads)), key="cmp_head")

        pat_a = np.array(cache_a[f"blocks.{layer}.attn.pattern"])[0, head]
        pat_b = np.array(cache_b[f"blocks.{layer}.attn.pattern"])[0, head]

        with col_a:
            fig_a = attention_heatmap(pat_a, t_labels_a, title=f"A — L{layer}H{head}")
            st.plotly_chart(fig_a, use_container_width=True)
        with col_b:
            fig_b = attention_heatmap(pat_b, t_labels_b, title=f"B — L{layer}H{head}")
            st.plotly_chart(fig_b, use_container_width=True)

    elif view_type == "Residual norms":
        stages_a = residual_norms(cache_a, n_layers)
        stages_b = residual_norms(cache_b, n_layers)

        with col_a:
            fig_a = residual_norms_fig(stages_a, t_labels_a)
            fig_a.update_layout(title="Trace A — residual norms")
            st.plotly_chart(fig_a, use_container_width=True)
        with col_b:
            fig_b = residual_norms_fig(stages_b, t_labels_b)
            fig_b.update_layout(title="Trace B — residual norms")
            st.plotly_chart(fig_b, use_container_width=True)

    elif view_type == "Logit distributions":
        logits_a = np.array(cache_a["logits"])[0]        # (T_a, vocab)
        logits_b = np.array(cache_b["logits"])[0]        # (T_b, vocab)

        exp_a = np.exp(logits_a - logits_a.max(axis=-1, keepdims=True))
        probs_a = exp_a / exp_a.sum(axis=-1, keepdims=True)
        exp_b = np.exp(logits_b - logits_b.max(axis=-1, keepdims=True))
        probs_b = exp_b / exp_b.sum(axis=-1, keepdims=True)

        T_a, T_b = len(tokens_a), len(tokens_b)
        if T_a > 1:
            pos_a = st.slider("Position (A)", 0, T_a - 1, 0, key="cmp_pos_a")
        else:
            pos_a = 0
            st.caption("Trace A: single token — slider hidden.")
        if T_b > 1:
            pos_b = st.slider("Position (B)", 0, T_b - 1, 0, key="cmp_pos_b")
        else:
            pos_b = 0
            st.caption("Trace B: single token — slider hidden.")

        from src.viz.plotting import top_k_bar
        top_k = 8

        with col_a:
            actual_a = tokens_a[pos_a + 1] if pos_a + 1 < T_a else None
            fig_a = top_k_bar(probs_a[pos_a], top_k=top_k, actual_next=actual_a,
                               title=f"A — pos {pos_a}")
            st.plotly_chart(fig_a, use_container_width=True)
        with col_b:
            actual_b = tokens_b[pos_b + 1] if pos_b + 1 < T_b else None
            fig_b = top_k_bar(probs_b[pos_b], top_k=top_k, actual_next=actual_b,
                               title=f"B — pos {pos_b}")
            st.plotly_chart(fig_b, use_container_width=True)
