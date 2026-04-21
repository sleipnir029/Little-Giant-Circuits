"""
Attention View — where does each head route information?

This view answers: which positions does each attention head "look at"?

In a transformer, attention computes a weighted average over value vectors.
The pattern matrix tells you the weights: pattern[q, k] is how much of
key position k's value vector gets added to query position q's output.

What to look for in the induction task:
  - Previous-token heads: strong diagonal at pattern[q, q-1].
  - Induction heads: strong off-diagonal pattern where q attends to the
    position where the same token appeared earlier (q - seq_len//2).

We show two tensors:
  - pattern (post-softmax): actual routing weights, sums to 1 per row.
  - scores (pre-softmax): raw attention logits, shows "what the head wants"
    before normalization. Useful for seeing masked positions (−inf → ~0 after softmax).
"""

import numpy as np
import streamlit as st

from src.tracing import ActivationCache
from src.viz.loading import token_labels
from src.viz.plotting import attention_heatmap


def render(
    cache: ActivationCache,
    meta: dict,
    model,
    cfg: dict,
) -> None:
    task = meta["task"]
    tokens = meta["tokens"]
    n_layers = cfg["model"]["n_layers"]
    n_heads = cfg["model"]["n_heads"]
    vocab_size = cfg["model"]["vocab_size"]

    t_labels = token_labels(task, tokens, vocab_size)

    st.subheader("Attention View")
    st.caption(
        "Select a layer and head to see the attention pattern. "
        "Rows = query positions (what's asking), columns = key positions (what's being looked at). "
        "Bright = high attention weight."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        layer = st.selectbox("Layer", list(range(n_layers)), key="attn_layer")
    with col2:
        head = st.selectbox("Head", list(range(n_heads)), key="attn_head")
    with col3:
        tensor_type = st.radio("Tensor", ["pattern (post-softmax)", "scores (pre-softmax)"], key="attn_tensor")

    use_pattern = "pattern" in tensor_type
    key_suffix = "pattern" if use_pattern else "scores"
    cache_key = f"blocks.{layer}.attn.{key_suffix}"

    arr = np.array(cache[cache_key])[0, head]         # (T, T)

    title = f"Layer {layer}, Head {head} — {key_suffix}"
    fig = attention_heatmap(arr, t_labels, title=title)
    st.plotly_chart(fig, use_container_width=True)

    if use_pattern:
        st.caption(
            "**Pattern**: post-softmax weights. Each row sums to 1. "
            "This is the actual information routing — what each position gathers from other positions."
        )
    else:
        st.caption(
            "**Scores**: post-causal-mask, pre-softmax logits. "
            "Upper triangle is masked to −∞. Lower triangle shows raw preference before normalization."
        )

    # --- All heads at a glance ---
    with st.expander(f"All {n_layers}×{n_heads} heads — pattern overview"):
        for l in range(n_layers):
            st.markdown(f"**Layer {l}**")
            head_cols = st.columns(n_heads)
            for h, col in enumerate(head_cols):
                pat = np.array(cache[f"blocks.{l}.attn.pattern"])[0, h]  # (T, T)
                small_fig = attention_heatmap(pat, t_labels, title=f"L{l}H{h}")
                small_fig.update_layout(height=200, showlegend=False,
                                        margin=dict(l=20, r=10, t=30, b=20))
                small_fig.update_coloraxes(showscale=False)
                col.plotly_chart(small_fig, use_container_width=True)

    # --- Per-query-position analysis ---
    st.divider()
    st.markdown("**Max-attended key per query position**")
    st.caption("For the selected head, which key position receives the most attention from each query?")

    pat = np.array(cache[f"blocks.{layer}.attn.pattern"])[0, head]  # (T, T)
    T = pat.shape[0]
    rows = []
    for q in range(T):
        max_key = int(np.argmax(pat[q]))
        rows.append({
            "query_pos": q,
            "query_token": tokens[q],
            "max_key_pos": max_key,
            "max_key_token": tokens[max_key] if max_key < len(tokens) else "?",
            "max_weight": f"{pat[q, max_key]:.3f}",
        })
    st.dataframe(rows, use_container_width=True)
