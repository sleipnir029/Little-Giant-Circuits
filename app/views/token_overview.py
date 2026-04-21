"""
Token Overview — what went in and what did the model predict?

This is the starting point for any inspection session. It answers:
  - What tokens are in the input sequence?
  - At each position, what is the model's top prediction for the NEXT token?
  - How confident is the model? (top-k probabilities)

For well-trained tasks, the prediction at induction positions should be near
100%. For random-looking positions (first half of induction, non-target
positions in kv_retrieval), confidence will be spread across many tokens.
"""

import numpy as np
import streamlit as st

from src.tracing import ActivationCache
from src.viz.plotting import top_k_bar


def render(
    cache: ActivationCache,
    meta: dict,
    model,
    cfg: dict,
) -> None:
    task = meta["task"]
    tokens = meta["tokens"]
    T = len(tokens)
    vocab_size = cfg["model"]["vocab_size"]

    st.subheader("Token Overview")
    st.caption(
        "Input tokens and the model's predictions at each position. "
        "The model predicts the **next** token at every position — shift the target by 1."
    )

    # --- Token sequence display ---
    st.markdown("**Input sequence**")
    cols = st.columns(min(T, 16))
    for i, (col, tok) in enumerate(zip(cols, tokens)):
        col.metric(label=f"pos {i}", value=str(tok))

    st.divider()

    # --- Per-position prediction view ---
    logits_np = np.array(cache["logits"])[0]         # (T, vocab)
    exp_logits = np.exp(logits_np - logits_np.max(axis=-1, keepdims=True))
    probs_all = exp_logits / exp_logits.sum(axis=-1, keepdims=True)  # (T, vocab) softmax

    if T > 1:
        position = st.slider("Inspect position", 0, T - 1, 0, key="tok_pos_slider")
    else:
        position = 0
        st.caption("Single-token sequence — position slider hidden.")
    actual_next = tokens[position + 1] if position + 1 < T else None

    probs = probs_all[position]                       # (vocab,)
    top1 = int(np.argmax(probs))

    col1, col2, col3 = st.columns(3)
    col1.metric("Token at this position", str(tokens[position]))
    col2.metric("Predicted next token", str(top1), help="Argmax of softmax(logits)")
    col3.metric(
        "Actual next token",
        str(actual_next) if actual_next is not None else "—",
        delta="✓ correct" if actual_next == top1 else ("✗ wrong" if actual_next is not None else ""),
        delta_color="normal" if actual_next == top1 else "inverse",
    )

    top_k = st.slider("Show top-k tokens", 4, min(16, vocab_size), 8, key="tok_topk_slider")
    fig = top_k_bar(probs, top_k=top_k, actual_next=actual_next, title=f"Predictions at position {position}")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "🔴 Red bar = actual next token. Tall red bar means the model is correct. "
        "Many equal-height bars = model is uncertain."
    )

    # --- Summary table ---
    with st.expander("All positions — top prediction and confidence"):
        rows = []
        for t in range(T):
            p = probs_all[t]
            top_tok = int(np.argmax(p))
            top_conf = float(p[top_tok])
            next_t = tokens[t + 1] if t + 1 < T else "?"
            rows.append({
                "pos": t,
                "token": tokens[t],
                "next_actual": next_t,
                "top_pred": top_tok,
                "top_conf": f"{top_conf:.1%}",
                "correct": "✓" if str(next_t) == str(top_tok) else "✗",
            })
        st.dataframe(rows, use_container_width=True)
