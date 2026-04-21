"""
Trace serialization — save and load activation caches to disk.

Format (matches Phase 1 checkpoint conventions):
  traces/{task}/{timestamp}/
    activations.safetensors  — flat tensor dict (mx.save_safetensors)
    trace_meta.json          — checkpoint path, task, input tokens, shapes, timestamp, git hash

Why this format?
  Phase 1 checkpoints use the same 4-file pattern with safetensors for weights.
  Reusing safetensors keeps the on-disk format consistent. The meta JSON records
  everything Phase 3 needs to reconstruct context (which model produced this trace,
  what was the input, when was it run).

  Tensors are saved as float32. MLX uses float32 by default for this model size;
  no bfloat16 conversion is needed.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import mlx.core as mx

from .cache import ActivationCache


def _git_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "unknown"


def save_trace(
    cache: ActivationCache,
    tokens: mx.array,
    checkpoint_dir: Path,
    task: str,
    out_dir: Path,
) -> Path:
    """Save an ActivationCache to disk.

    Args:
        cache:           The ActivationCache to serialize.
        tokens:          The input token array (B, T) or (T,) used to produce this cache.
        checkpoint_dir:  Path to the checkpoint directory that was loaded.
        task:            Task name (e.g., "induction").
        out_dir:         Directory to write trace files into.

    Returns:
        out_dir after writing both files.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save tensors
    flat = cache.flat()
    mx.eval(*list(flat.values()))
    mx.save_safetensors(str(out_dir / "activations.safetensors"), flat)

    # Build metadata
    if tokens.ndim > 1:
        tokens_list = tokens[0].tolist()   # first item in batch
    else:
        tokens_list = tokens.tolist()

    # Record tensor shapes for human readability in the JSON
    shapes = {k: list(v.shape) for k, v in flat.items()}

    meta = {
        "task": task,
        "checkpoint_dir": str(checkpoint_dir),
        "tokens": tokens_list,
        "n_tokens": len(tokens_list),
        "tensor_shapes": shapes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_hash": _git_hash(),
    }
    (out_dir / "trace_meta.json").write_text(json.dumps(meta, indent=2))

    return out_dir


def load_trace(trace_dir: Path) -> tuple[ActivationCache, dict]:
    """Load a saved trace from disk.

    Returns:
        cache: ActivationCache with all tensors as mx.array.
        meta:  The trace_meta.json dict (task, tokens, checkpoint_dir, etc.).
    """
    trace_dir = Path(trace_dir)
    activations_path = trace_dir / "activations.safetensors"
    meta_path = trace_dir / "trace_meta.json"

    if not activations_path.exists():
        raise FileNotFoundError(f"No activations file at {activations_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"No trace_meta.json at {meta_path}")

    flat_np = mx.load(str(activations_path))
    # mx.load already returns {str: mx.array} — use directly, no numpy round-trip needed
    flat_mx: dict[str, mx.array] = dict(flat_np)
    mx.eval(*list(flat_mx.values()))

    # Wrap directly — ActivationCache._flat can be set manually since it's a plain dict
    cache = ActivationCache.__new__(ActivationCache)
    cache._flat = flat_mx

    meta = json.loads(meta_path.read_text())
    return cache, meta
