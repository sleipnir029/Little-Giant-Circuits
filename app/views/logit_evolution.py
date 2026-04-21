"""
Logit Evolution View — when does the model "know" the answer?

This view implements the logit lens technique (Nostalgebraist 2020).

Instead of waiting for the final output, we project the residual stream at each
intermediate layer through the output head (ln_f + head linear) and ask:
"What would the model predict if it stopped computing here?"

This reveals:
  - WHEN the correct answer becomes encoded in the residual stream.
  - WHETHER information about the answer is already present after early layers.
  - HOW confidence builds layer by layer for different token positions.

For the induction task on a well-trained model:
  - Induction positions (second half) should show high confidence by layer 1.
  - Random positions (first half) should stay uncertain across all layers.

For the bracket_match task (only ~68% accurate):
  - You should see partial, position-dependent confidence — the model guesses
    but doesn't always commit.

The computation is: for each layer i,
    probs_i = softmax(head(ln_f(resid_post_i)))
where resid_post_i = the residual stream AFTER block i's full computation (attn + MLP).
"""

import numpy as np
import streamlit as st

from src.tracing import ActivationCache
from src.viz.loading import compute_logit_lens, token_labels
from src.viz.plotting import logit_evolution_heatmap, logit_evolution_line


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
    layer_labels = [f"after L{i}" for i in range(n_layers)]

    st.subheader("Logit Evolution (Logit Lens)")
    st.caption(
        "Projects the residual stream at each layer through the output head. "
        "Each cell shows P(target token) at that layer and position. "
        "**Bright early = the model already knows the answer after that layer.**"
    )

    with st.spinner("Computing logit lens..."):
        per_layer_probs = compute_logit_lens(cache, model, n_layers)
        # per_layer_probs: (n_layers, T, vocab_size)

    T = len(tokens)

    # --- Target token selection ---
    st.markdown("**Target token selection**")
    target_mode = st.radio(
        "Target tokens",
        ["Final layer prediction (argmax)", "Actual next token", "Manual per-position"],
        key="logit_target_mode",
        horizontal=True,
    )

    final_preds = np.argmax(per_layer_probs[-1], axis=-1).tolist()
    actual_nexts = [tokens[i + 1] if i + 1 < T else tokens[i] for i in range(T)]

    if target_mode == "Final layer prediction (argmax)":
        target_tokens = final_preds
        target_desc = "what the model predicts"
    elif target_mode == "Actual next token":
        target_tokens = actual_nexts
        target_desc = "the actual next token"
    else:
        target_tokens = []
        for i in range(T):
            t = st.number_input(f"Target at pos {i}", 0, vocab_size - 1, final_preds[i], key=f"target_{i}")
            target_tokens.append(int(t))
        target_desc = "manually chosen tokens"

    # --- Heatmap ---
    fig = logit_evolution_heatmap(per_layer_probs, t_labels, layer_labels, target_tokens)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Showing P({target_desc}) at each layer. "
        "Bright = high confidence. Dark early rows = answer not yet in residual stream."
    )

    st.divider()

    # --- Line chart for one position ---
    st.markdown("**Confidence trace for a single position**")
    if T > 1:
        pos = st.slider("Position", 0, T - 1, min(T - 1, T // 2), key="logit_pos_slider")
    else:
        pos = 0
        st.caption("Single-token sequence — position slider hidden.")

    line_fig = logit_evolution_line(
        per_layer_probs,
        layer_labels,
        position=pos,
        top_k=min(5, vocab_size),
    )
    st.plotly_chart(line_fig, use_container_width=True)

    actual_next_here = tokens[pos + 1] if pos + 1 < T else "—"
    st.caption(
        f"Position {pos} | input token = {tokens[pos]} | actual next = {actual_next_here}. "
        "Lines show how the top-5 predicted tokens' probabilities evolve across layers."
    )

    # --- Summary table ---
    with st.expander("Layer-by-layer confidence table"):
        rows = []
        for l in range(n_layers):
            row = {"layer": layer_labels[l]}
            for t in range(T):
                row[f"pos{t}(tok={tokens[t]})"] = f"{per_layer_probs[l, t, target_tokens[t]]:.2%}"
            rows.append(row)
        st.dataframe(rows, use_container_width=True)
