"""
Little Giant Circuits — Interpretability Microscope

Main Streamlit entry point.

Two modes:
  - Learn Mode:       guided, stage-stepped narrative walkthrough of the forward pass
  - Investigate Mode: technical inspection views (6 views, preserved from Phase 3)

Run:
    streamlit run app/streamlit_app.py

Architecture:
  - src/viz/loading.py     — pure helpers (no streamlit)
  - src/viz/plotting.py    — pure plotly figure functions
  - src/viz/stages.py      — Stage dataclass + build_stages (no streamlit)
  - src/viz/playback.py    — playback state helpers (no streamlit)
  - app/learn/learn_mode.py — Learn Mode rendering
  - app/views/             — Investigate Mode: one view module per visualization
  - app/streamlit_app.py   — this file: mode toggle + sidebar + routing
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure repo root is on the path regardless of working directory
_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.tracing import load_trace, save_trace
from src.viz.loading import (
    DEMO_PROMPTS,
    TASKS,
    list_checkpoints,
    list_traces,
    load_model,
    load_trace_from_dir,
    run_custom_trace,
    run_demo_trace,
)

import app.views.token_overview as v_token
import app.views.layer_overview as v_layer
import app.views.attention_view as v_attn
import app.views.mlp_view as v_mlp
import app.views.logit_evolution as v_logit
import app.views.comparison as v_cmp
import app.learn.learn_mode as v_learn


# ---------------------------------------------------------------------------
# Streamlit cached wrappers
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading model...")
def cached_load_model(ckpt_dir_str: str):
    """Load and cache a Transformer model by checkpoint path."""
    return load_model(Path(ckpt_dir_str))


@st.cache_resource(show_spinner="Loading trace...")
def cached_load_trace(trace_dir_str: str):
    """Load and cache a trace from disk by path."""
    return load_trace_from_dir(Path(trace_dir_str))


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Little Giant Circuits",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔬 Little Giant Circuits")
st.caption("Interpretability lab for tiny trained transformers · Phase 3 Refinement")

# ---------------------------------------------------------------------------
# Top-level mode toggle — Learn Mode vs Investigate Mode
# ---------------------------------------------------------------------------

mode = st.radio(
    "Mode",
    ["Learn Mode", "Investigate Mode"],
    horizontal=True,
    help=(
        "**Learn Mode**: guided walkthrough — step through the forward pass with plain-language explanations.  "
        "**Investigate Mode**: technical inspection views — raw tensors, full controls."
    ),
)
st.divider()


# ---------------------------------------------------------------------------
# Sidebar — trace loading
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Trace Loader")

    # --- Task selection ---
    task = st.selectbox("Task", TASKS, index=0)

    # --- Checkpoint selection ---
    ckpts = list_checkpoints(task)
    if not ckpts:
        st.error(f"No checkpoints found for **{task}**. Train first:\n`python src/training/train.py --task {task}`")
        st.stop()

    ckpt_names = [p.name for p in ckpts]
    ckpt_sel = st.selectbox("Checkpoint", ckpt_names, index=len(ckpt_names) - 1,
                             help="Step number of the saved checkpoint. Latest = most trained.")
    ckpt_dir = ckpts[ckpt_names.index(ckpt_sel)]

    # --- Load model (cached) ---
    model, cfg = cached_load_model(str(ckpt_dir))
    n_layers = cfg["model"]["n_layers"]
    n_heads = cfg["model"]["n_heads"]
    vocab_size = cfg["model"]["vocab_size"]

    # --- Trace source ---
    st.divider()
    st.subheader("Trace")
    trace_mode = st.radio(
        "Source",
        ["Load saved trace", "Run demo prompt", "Run custom tokens"],
        help="Load a pre-saved trace, or run a new one.",
    )

    cache = None
    meta = None

    if trace_mode == "Load saved trace":
        saved_traces = list_traces(task)
        if not saved_traces:
            st.info(
                f"No saved traces for **{task}**. "
                "Switch to 'Run demo prompt' or run:\n"
                f"`python scripts/generate_demo_traces.py`"
            )
            st.stop()
        trace_names = [p.name for p in saved_traces]
        trace_sel = st.selectbox("Trace", trace_names, index=0)
        trace_dir = saved_traces[trace_names.index(trace_sel)]

        cache, meta = cached_load_trace(str(trace_dir))
        # Ensure meta has required fields
        if "task" not in meta:
            meta["task"] = task

    elif trace_mode == "Run demo prompt":
        default_tokens = DEMO_PROMPTS.get(task, [1, 2, 3])
        st.caption(f"Demo tokens: `{default_tokens}`")
        if st.button("Run trace", type="primary"):
            with st.spinner("Running trace..."):
                logits, cache, tokens_used = run_demo_trace(model, task)
            st.session_state[f"live_cache_{task}"] = cache
            st.session_state[f"live_meta_{task}"] = {
                "task": task,
                "tokens": tokens_used,
                "checkpoint_dir": str(ckpt_dir),
                "n_tokens": len(tokens_used),
            }
            st.success("Trace complete.")

        cache = st.session_state.get(f"live_cache_{task}")
        meta = st.session_state.get(f"live_meta_{task}")

        if cache is None:
            st.info("Click **Run trace** to generate a trace.")
            st.stop()

        save_label = st.text_input("Save as (optional)", value="demo", key="save_name_demo")
        if st.button("Save trace to disk"):
            import mlx.core as mx
            tokens_mx = mx.array(meta["tokens"])
            save_trace(
                cache=cache,
                tokens=tokens_mx,
                checkpoint_dir=ckpt_dir,
                task=task,
                out_dir=_REPO / "traces" / task / save_label,
            )
            st.success(f"Saved to traces/{task}/{save_label}/")
            # Clear cache so the new trace appears in the dropdown
            cached_load_trace.clear()

    else:  # Run custom tokens
        default_str = " ".join(str(t) for t in DEMO_PROMPTS.get(task, [1, 2, 3]))
        tokens_str = st.text_area("Token IDs (space-separated)", value=default_str, height=80)
        try:
            custom_tokens = [int(t) for t in tokens_str.strip().split()]
        except ValueError:
            st.error("Please enter space-separated integers.")
            st.stop()

        if any(t >= vocab_size or t < 0 for t in custom_tokens):
            st.warning(f"Some tokens out of range [0, {vocab_size - 1}]. Check your input.")

        if st.button("Run trace", type="primary", key="run_custom_btn"):
            with st.spinner("Running trace..."):
                logits, custom_cache = run_custom_trace(model, custom_tokens)
            st.session_state[f"custom_cache_{task}"] = custom_cache
            st.session_state[f"custom_meta_{task}"] = {
                "task": task,
                "tokens": custom_tokens,
                "checkpoint_dir": str(ckpt_dir),
                "n_tokens": len(custom_tokens),
            }
            st.success("Trace complete.")

        cache = st.session_state.get(f"custom_cache_{task}")
        meta = st.session_state.get(f"custom_meta_{task}")

        if cache is None:
            st.info("Click **Run trace** to generate a trace.")
            st.stop()

    # --- View selection (Investigate Mode only) ---
    view = None
    if mode == "Investigate Mode":
        st.divider()
        st.subheader("View")
        view = st.selectbox(
            "Select view",
            [
                "Token Overview",
                "Layer Overview",
                "Attention",
                "MLP Activations",
                "Logit Evolution",
                "Compare Traces",
            ],
        )
    else:
        st.divider()
        st.caption(
            "Learn Mode: step through the forward pass using the controls on the main panel."
        )

    st.divider()
    st.caption(
        f"Model: {n_layers}L × {n_heads}H × d={cfg['model']['d_model']} · "
        f"vocab={vocab_size} · task={task}"
    )


# ---------------------------------------------------------------------------
# Guard: ensure we have a trace before rendering any view
# ---------------------------------------------------------------------------

if cache is None or meta is None:
    st.info("Load or run a trace using the sidebar to begin.")
    st.stop()


# ---------------------------------------------------------------------------
# View routing
# ---------------------------------------------------------------------------

if mode == "Learn Mode":
    v_learn.render(cache, meta, model, cfg)

elif view == "Token Overview":
    v_token.render(cache, meta, model, cfg)

elif view == "Layer Overview":
    v_layer.render(cache, meta, model, cfg)

elif view == "Attention":
    v_attn.render(cache, meta, model, cfg)

elif view == "MLP Activations":
    v_mlp.render(cache, meta, model, cfg)

elif view == "Logit Evolution":
    v_logit.render(cache, meta, model, cfg)

elif view == "Compare Traces":
    st.subheader("Compare Traces")
    st.caption("Load a second trace to compare side-by-side with the current trace.")

    saved_traces_cmp = list_traces(task)
    if len(saved_traces_cmp) < 1:
        st.info(
            "Save at least one trace first (use 'Run demo prompt' → 'Save trace'), "
            "then load a second trace here."
        )
    else:
        trace_names_cmp = [p.name for p in saved_traces_cmp]
        trace_b_sel = st.selectbox("Second trace", trace_names_cmp, key="cmp_trace_b")
        trace_b_dir = saved_traces_cmp[trace_names_cmp.index(trace_b_sel)]
        cache_b, meta_b = cached_load_trace(str(trace_b_dir))
        if "task" not in meta_b:
            meta_b["task"] = task

        v_cmp.render(cache, meta, cache_b, meta_b, model, cfg)
