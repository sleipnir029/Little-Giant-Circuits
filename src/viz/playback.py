"""
Playback state helpers for Learn Mode.

Pure Python — no Streamlit imports. The Streamlit UI calls these to manage
stage navigation state stored in st.session_state.

The stage index is the single source of truth. Forward/back/goto mutate it.
"""

from __future__ import annotations


def get_stage_index(session_state: dict, key: str = "learn_stage_idx") -> int:
    """Return current stage index from session state (default 0)."""
    return int(session_state.get(key, 0))


def set_stage_index(session_state: dict, idx: int, n_stages: int, key: str = "learn_stage_idx") -> int:
    """Clamp and store idx. Returns the clamped value."""
    clamped = max(0, min(idx, n_stages - 1))
    session_state[key] = clamped
    return clamped


def step_forward(session_state: dict, n_stages: int, key: str = "learn_stage_idx") -> int:
    current = get_stage_index(session_state, key)
    return set_stage_index(session_state, current + 1, n_stages, key)


def step_backward(session_state: dict, n_stages: int, key: str = "learn_stage_idx") -> int:
    current = get_stage_index(session_state, key)
    return set_stage_index(session_state, current - 1, n_stages, key)


def goto_stage(session_state: dict, idx: int, n_stages: int, key: str = "learn_stage_idx") -> int:
    return set_stage_index(session_state, idx, n_stages, key)


def is_first(session_state: dict, key: str = "learn_stage_idx") -> bool:
    return get_stage_index(session_state, key) == 0


def is_last(session_state: dict, n_stages: int, key: str = "learn_stage_idx") -> bool:
    return get_stage_index(session_state, key) >= n_stages - 1


def stage_label(session_state: dict, stages: list, key: str = "learn_stage_idx") -> str:
    """Return a human-readable progress label like 'Step 3 of 9: Layer 0 — Attention'."""
    idx = get_stage_index(session_state, key)
    n = len(stages)
    name = stages[idx].name if stages else "?"
    return f"{idx + 1} of {n}: {name}"
