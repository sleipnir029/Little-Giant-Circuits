"""
Checkpoint save/load for tiny transformer training.

Every checkpoint directory stores exactly four files:
  weights.safetensors  — MLX model weights, flat dot-notation keys
  config.json          — model config + training config at save time
  metrics.json         — loss, accuracy, step
  meta.json            — task, timestamp, git hash

Directory naming: checkpoints/{task}/{step:07d}/
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn


def _flatten(params: dict, prefix: str = "") -> dict:
    """Recursively flatten a nested parameter dict to dot-notation keys.

    MLX's model.parameters() returns nested dicts like {'blocks': [{'attn': ...}]}.
    mx.save_safetensors requires a flat {str: array} dict.
    """
    flat: dict = {}
    for k, v in params.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            flat.update(_flatten(v, key))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    flat.update(_flatten(item, f"{key}.{i}"))
                else:
                    flat[f"{key}.{i}"] = item
        else:
            flat[key] = v
    return flat


def _unflatten(flat: dict) -> dict:
    """Reconstruct a nested dict/list structure from dot-notation keys for model.update().

    MLX modules store layer lists as Python lists, not dicts. Keys like 'blocks.0.attn.q.weight'
    must reconstruct {'blocks': [{'attn': ...}, ...]} — not {'blocks': {'0': ...}}.
    We detect list nodes by checking if all child keys are consecutive integers from 0.
    """
    nested: dict = {}
    for dotkey, val in flat.items():
        parts = dotkey.split(".")
        d = nested
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = val

    def _lists(node: dict) -> dict | list:
        if not isinstance(node, dict):
            return node
        children = {k: _lists(v) for k, v in node.items()}
        # If all keys are consecutive ints 0..n-1, return as list
        if all(k.isdigit() for k in children):
            indices = sorted(int(k) for k in children)
            if indices == list(range(len(indices))):
                return [children[str(i)] for i in indices]
        return children

    return _lists(nested)


def save(
    model: nn.Module,
    checkpoint_dir: Path,
    model_cfg: dict,
    train_cfg: dict,
    step: int,
    loss: float,
    accuracy: float,
    task: str,
) -> None:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    flat = _flatten(model.parameters())
    mx.eval(flat)
    mx.save_safetensors(str(checkpoint_dir / "weights.safetensors"), flat)

    (checkpoint_dir / "config.json").write_text(
        json.dumps({"model": model_cfg, "train": train_cfg}, indent=2)
    )
    (checkpoint_dir / "metrics.json").write_text(
        json.dumps({"step": step, "loss": round(loss, 6), "accuracy": round(accuracy, 6)}, indent=2)
    )

    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        git_hash = "unknown"

    (checkpoint_dir / "meta.json").write_text(
        json.dumps(
            {
                "task": task,
                "step": step,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "git_hash": git_hash,
            },
            indent=2,
        )
    )


def load(model: nn.Module, checkpoint_dir: Path) -> dict:
    """Load weights from checkpoint into model in-place. Returns saved metrics dict."""
    flat = mx.load(str(checkpoint_dir / "weights.safetensors"))
    nested = _unflatten(dict(flat))
    model.update(nested)
    mx.eval(model.parameters())
    return json.loads((checkpoint_dir / "metrics.json").read_text())
