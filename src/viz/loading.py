"""
Loading helpers for Phase 3 visualization.

Pure helpers — no streamlit imports. Returns models, traces, and computed tensors
so app/views/ can call these and pass results to plotly figure functions.

Key design: load_model and load_trace_from_dir are the two expensive operations.
The Streamlit app wraps them with @st.cache_resource / @st.cache_data so they
are not recomputed on every widget interaction.
"""

import json
import sys
from pathlib import Path

import mlx.core as mx
import numpy as np

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.models.transformer import Transformer
from src.tracing import ActivationCache, load_trace, trace
from src.utils.checkpoint import load
from src.utils.config import ModelConfig


TASKS = [
    "induction",
    "kv_retrieval",
    "modular_arith",
    "bracket_match",
    "factual_lookup",
    "sorting",
]

# Default demo prompts per task — same as scripts/trace_prompt.py
DEMO_PROMPTS: dict[str, list[int]] = {
    "induction":     [3, 7, 1, 5, 8, 2, 4, 6, 3, 7, 1, 5, 8, 2, 4],
    "kv_retrieval":  [5, 11, 8, 14, 3, 9, 5],
    "modular_arith": [4, 7],
    "bracket_match": [1, 1, 2, 1, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 2],
    "factual_lookup":[5],
    "sorting":       [8, 3, 15, 6, 31],
}


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------

def list_checkpoints(task: str) -> list[Path]:
    """Return sorted list of checkpoint dirs for a task (oldest first)."""
    base = _REPO / "checkpoints" / task
    if not base.exists():
        return []
    return sorted(base.iterdir(), key=lambda p: p.name)


def list_traces(task: str) -> list[Path]:
    """Return sorted list of trace dirs for a task. Only dirs with activations.safetensors."""
    base = _REPO / "traces" / task
    if not base.exists():
        return []
    valid = [p for p in base.iterdir() if (p / "activations.safetensors").exists()]
    return sorted(valid, key=lambda p: p.name)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(ckpt_dir: Path) -> tuple[Transformer, dict]:
    """Load a Transformer from a checkpoint dir.

    Returns:
        model:    Loaded Transformer with weights.
        cfg_raw:  Full config dict (keys: "model", "train").
    """
    cfg_raw = json.loads((ckpt_dir / "config.json").read_text())
    mcfg = ModelConfig(**cfg_raw["model"])
    model = Transformer(
        vocab_size=mcfg.vocab_size,
        d_model=mcfg.d_model,
        n_layers=mcfg.n_layers,
        n_heads=mcfg.n_heads,
        seq_len=mcfg.seq_len,
    )
    load(model, ckpt_dir)
    return model, cfg_raw


# ---------------------------------------------------------------------------
# Trace running
# ---------------------------------------------------------------------------

def run_demo_trace(model: Transformer, task: str) -> tuple[mx.array, ActivationCache, list[int]]:
    """Run a forward pass with the default demo prompt for a task.

    Returns:
        logits:  (1, T, vocab) MLX array.
        cache:   ActivationCache with all intermediate tensors.
        tokens:  The input token list used.
    """
    tokens_list = DEMO_PROMPTS[task]
    tokens = mx.array(tokens_list)[None, :]
    logits, act_cache = trace(model, tokens)
    return logits, act_cache, tokens_list


def run_custom_trace(
    model: Transformer,
    tokens_list: list[int],
) -> tuple[mx.array, ActivationCache]:
    """Run a forward pass with a custom token sequence."""
    tokens = mx.array(tokens_list)[None, :]
    logits, act_cache = trace(model, tokens)
    return logits, act_cache


def load_trace_from_dir(trace_dir: Path) -> tuple[ActivationCache, dict]:
    """Load a saved trace from disk. Thin wrapper over src.tracing.load_trace."""
    return load_trace(trace_dir)


# ---------------------------------------------------------------------------
# Token labeling
# ---------------------------------------------------------------------------

def token_label(task: str, token_id: int, vocab_size: int) -> str:
    """Human-readable label for a token integer."""
    if task == "bracket_match":
        labels = {0: "PAD", 1: "(", 2: ")", 3: "B"}
        sym = labels.get(token_id, str(token_id))
        return f"{token_id}:{sym}"
    if task == "sorting":
        sep = vocab_size - 1
        if token_id == sep:
            return f"{token_id}:SEP"
    return str(token_id)


def token_labels(task: str, tokens: list[int], vocab_size: int) -> list[str]:
    """Return a list of human-readable labels for a token sequence."""
    return [token_label(task, t, vocab_size) for t in tokens]


# ---------------------------------------------------------------------------
# Residual stream norms
# ---------------------------------------------------------------------------

def residual_norms(cache: ActivationCache, n_layers: int) -> dict[str, np.ndarray]:
    """Extract L2 norm per token position at each residual stream checkpoint.

    Returns a dict mapping stage name → (T,) float32 array.
    Stages: embed.combined, blocks.0.resid_pre, ..., blocks.{n-1}.resid_post
    """
    stages: dict[str, np.ndarray] = {}
    stages["embed"] = np.linalg.norm(
        np.array(cache["embed.combined"])[0], axis=-1
    )
    for i in range(n_layers):
        for stage in ("resid_pre", "resid_mid", "resid_post"):
            key = f"blocks.{i}.{stage}"
            arr = np.array(cache[key])[0]  # (T, d_model)
            stages[f"L{i}.{stage}"] = np.linalg.norm(arr, axis=-1)
    return stages


# ---------------------------------------------------------------------------
# Logit lens — the user-implementable function
# ---------------------------------------------------------------------------

def compute_logit_lens(
    cache: ActivationCache,
    model: Transformer,
    n_layers: int,
) -> np.ndarray:
    """Apply the logit lens: project each layer's residual stream through the final head.

    The logit lens (Nostalgebraist 2020) asks: "if the model stopped computing at
    layer i and we projected the residual stream directly through the output head,
    what would it predict?"

    This reveals WHEN information about the correct answer first appears in the
    residual stream — often a layer or two before the model outputs it.

    Args:
        cache:    ActivationCache from a traced forward pass.
        model:    The loaded Transformer (needed for model.ln_f and model.head).
        n_layers: Number of transformer layers.

    Returns:
        per_layer_probs: float32 numpy array of shape (n_layers, T, vocab_size)
            per_layer_probs[i, t, v] = softmax probability of token v at position t
            if the model had stopped after layer i.

    TODO: implement this function.

    Implementation guidance (5-10 lines of numpy + mlx):
    -------------------------------------------------------
    For each layer i from 0 to n_layers-1:
      1. Get the residual stream at that layer:
            resid = cache[f"blocks.{i}.resid_post"]   # shape: (1, T, d_model)
      2. Apply the final LayerNorm then the output head (same path as the real forward):
            normed = model.ln_f(resid)                 # (1, T, d_model)
            layer_logits = model.head(normed)           # (1, T, vocab_size)
      3. Convert logits to probabilities with softmax:
            probs = mx.softmax(layer_logits, axis=-1)  # (1, T, vocab_size)
      4. Materialize: mx.eval(probs)
      5. Store as numpy: np.array(probs)[0]             # (T, vocab_size)

    Collect the (T, vocab_size) arrays for all layers into a list, then stack
    into a (n_layers, T, vocab_size) array and return it.

    Design note: using model.ln_f (the TRAINED final LayerNorm) is the standard
    logit lens approach. An alternative is to skip LN entirely or use a per-layer
    LN ("tuned lens"). The trained-LN version is simpler and still reveals the key
    insight: when does the model commit to a prediction?
    -------------------------------------------------------
    """
    # --- YOUR IMPLEMENTATION HERE ---
    # Replace `pass` and `return` with the implementation described above.
    # Remove this comment block when done.
    layers_probs: list[np.ndarray] = []
    for i in range(n_layers):
        resid = cache[f"blocks.{i}.resid_post"]          # (1, T, d_model)
        normed = model.ln_f(resid)                        # (1, T, d_model)
        layer_logits = model.head(normed)                 # (1, T, vocab_size)
        probs = mx.softmax(layer_logits, axis=-1)
        mx.eval(probs)
        layers_probs.append(np.array(probs)[0])           # (T, vocab_size)
    return np.stack(layers_probs, axis=0)                 # (n_layers, T, vocab_size)
