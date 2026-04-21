"""
src/viz — pure visualization helpers for the Little Giant Circuits app.

No streamlit imports in this package. All functions return plotly Figure objects
or plain data structures so Phase 4/5 scripts can reuse them without a web framework.

Public API:
    from src.viz.loading import list_checkpoints, list_traces, load_model, run_demo_trace
    from src.viz.plotting import attention_heatmap, residual_norms_fig, ...
    from src.viz.stages import build_stages, Stage
    from src.viz.playback import step_forward, step_backward, get_stage_index
"""
