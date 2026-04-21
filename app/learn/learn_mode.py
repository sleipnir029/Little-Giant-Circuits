"""
Learn Mode — guided, stage-stepped walkthrough of a transformer forward pass.

This module renders the full Learn Mode experience:
  - Playback controls (← Previous / Next →) with stage indicator
  - Stage explanation panel (what, what changed, what to notice)
  - Focused Plotly figure for this stage
  - Link to the corresponding Investigate Mode view

State is stored in st.session_state under the "learn_stage_idx" key.
The stage list is built once per trace (cached via st.session_state).
"""

import streamlit as st

from src.tracing import ActivationCache
from src.viz.stages import Stage, build_stages
from src.viz import playback


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_or_build_stages(
    cache: ActivationCache,
    model,
    cfg: dict,
    meta: dict,
) -> list[Stage]:
    """Build stages once per trace; store in session_state keyed by trace identity."""
    trace_key = f"learn_stages_{id(cache)}"
    if trace_key not in st.session_state:
        with st.spinner("Building learning stages..."):
            st.session_state[trace_key] = build_stages(cache, model, cfg, meta)
    return st.session_state[trace_key]


def _render_playback_controls(stages: list[Stage]) -> int:
    """Render ← / → buttons + progress indicator. Returns the current stage index."""
    n = len(stages)
    current_idx = playback.get_stage_index(st.session_state)

    cols = st.columns([1, 4, 1])

    with cols[0]:
        if st.button("← Previous", disabled=playback.is_first(st.session_state),
                     use_container_width=True, key="learn_prev"):
            current_idx = playback.step_backward(st.session_state, n)

    with cols[1]:
        st.progress(
            (current_idx) / max(1, n - 1),
            text=playback.stage_label(st.session_state, stages),
        )

    with cols[2]:
        if st.button("Next →", disabled=playback.is_last(st.session_state, n),
                     use_container_width=True, key="learn_next"):
            current_idx = playback.step_forward(st.session_state, n)

    # Quick-jump selector
    with st.expander("Jump to any step"):
        stage_names = [f"{s.index + 1}. {s.name}" for s in stages]
        jump_sel = st.selectbox(
            "Select stage",
            stage_names,
            index=current_idx,
            key="learn_jump_select",
            label_visibility="collapsed",
        )
        jumped_idx = stage_names.index(jump_sel)
        if jumped_idx != current_idx:
            current_idx = playback.goto_stage(st.session_state, jumped_idx, n)

    return playback.get_stage_index(st.session_state)


def _render_stage(stage: Stage) -> None:
    """Render the full content of one Stage."""

    # Header
    st.markdown(f"## {stage.name}")
    st.divider()

    # Three-panel explanation
    col_exp, col_viz = st.columns([1, 2], gap="large")

    with col_exp:
        st.markdown("### What's happening")
        st.write(stage.explanation)

        st.markdown("### What changed")
        st.write(stage.what_changed)

        st.markdown("### What to notice")
        st.markdown(f"> {stage.what_to_notice}")

        st.markdown("---")
        st.caption(
            f"Want technical detail? "
            f"Switch to **Investigate Mode** → **{stage.next_technical_view}**"
        )

    with col_viz:
        if stage.figure is not None:
            st.plotly_chart(stage.figure, use_container_width=True)
        else:
            st.info("No figure for this stage.")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render(cache: ActivationCache, meta: dict, model, cfg: dict) -> None:
    """Render the full Learn Mode for a loaded trace."""

    st.markdown("# Learn Mode")
    st.caption(
        "Walk through the model's forward pass one step at a time. "
        "Use **← Previous** and **Next →** to navigate. "
        "Each step explains what the model is doing in plain language."
    )
    st.divider()

    stages = _get_or_build_stages(cache, model, cfg, meta)

    if not stages:
        st.error("Could not build stages for this trace.")
        return

    current_idx = _render_playback_controls(stages)

    st.divider()

    stage = stages[current_idx]
    _render_stage(stage)

    # Navigation hint at the bottom
    st.divider()
    nav_cols = st.columns([1, 4, 1])
    with nav_cols[0]:
        if st.button("← Previous", disabled=playback.is_first(st.session_state),
                     use_container_width=True, key="learn_prev_bottom"):
            playback.step_backward(st.session_state, len(stages))
            st.rerun()
    with nav_cols[2]:
        if st.button("Next →", disabled=playback.is_last(st.session_state, len(stages)),
                     use_container_width=True, key="learn_next_bottom"):
            playback.step_forward(st.session_state, len(stages))
            st.rerun()
