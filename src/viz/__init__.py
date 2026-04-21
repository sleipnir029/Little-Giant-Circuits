"""
src/viz — pure visualization helpers for Phase 3 Streamlit app.

No streamlit imports here. Functions return plotly Figure objects or plain data
structures so Phase 4/5 scripts can reuse them without a web framework.

Public API:
    from src.viz.loading import list_checkpoints, list_traces, load_model, run_demo_trace
    from src.viz.plotting import attention_heatmap, residual_norms_fig, ...
"""
