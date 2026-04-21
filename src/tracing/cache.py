"""
ActivationCache — thin wrapper around the raw nested cache dict from Transformer.__call__.

Why a wrapper?
  The raw cache is a nested dict with lists for the blocks layer. Addressing a specific
  tensor requires chained indexing like cache["blocks"][0]["attn"]["scores"]. The
  ActivationCache wrapper flattens this to dot-key access:
      ac["blocks.0.attn.scores"]
  which mirrors TransformerLens conventions and makes Phase 3 visualization code
  independent of the Python nesting structure.

Key naming convention (TransformerLens-style):
    embed.tok             — token embeddings       (B, T, d_model)
    embed.pos             — positional embeddings  (T, d_model)
    embed.combined        — tok + pos              (B, T, d_model)
    blocks.{i}.resid_pre  — residual before block  (B, T, d_model)
    blocks.{i}.resid_mid  — after attn, before MLP (B, T, d_model)
    blocks.{i}.resid_post — residual after block   (B, T, d_model)
    blocks.{i}.attn.q     — Q projections          (B, H, T, Dh)
    blocks.{i}.attn.k     — K projections          (B, H, T, Dh)
    blocks.{i}.attn.v     — V projections          (B, H, T, Dh)
    blocks.{i}.attn.scores  — post-mask pre-softmax (B, H, T, T)
    blocks.{i}.attn.pattern — post-softmax weights  (B, H, T, T)
    blocks.{i}.attn.output  — attention output      (B, T, d_model)
    blocks.{i}.mlp.pre    — after mlp1, pre-GELU   (B, T, 4*d_model)
    blocks.{i}.mlp.post   — after GELU, pre-mlp2   (B, T, 4*d_model)
    blocks.{i}.mlp.output — MLP contribution       (B, T, d_model)
    ln_f.input            — final LayerNorm input  (B, T, d_model)
    logits                — output logits          (B, T, vocab)
"""

import mlx.core as mx


def _flatten_cache(node: object, prefix: str = "") -> dict[str, mx.array]:
    """Recursively flatten a nested cache dict to dot-notation keys.

    Handles: dicts (recurse with key.subkey), lists (recurse with key.index),
    mx.array leaves (store), and anything else (skip).
    """
    flat: dict[str, mx.array] = {}
    if isinstance(node, dict):
        for k, v in node.items():
            child_key = f"{prefix}.{k}" if prefix else k
            flat.update(_flatten_cache(v, child_key))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            flat.update(_flatten_cache(item, f"{prefix}.{i}"))
    elif isinstance(node, mx.array):
        flat[prefix] = node
    return flat


class ActivationCache:
    """Flat-key accessor for a Transformer activation cache.

    Built from the raw nested dict returned by Transformer.__call__(return_cache=True).

    Example:
        logits, raw = model(tokens, return_cache=True)
        cache = ActivationCache(raw)
        scores = cache["blocks.0.attn.scores"]  # (B, H, T, T)
        keys = cache.keys()
    """

    def __init__(self, raw: dict) -> None:
        self._flat: dict[str, mx.array] = _flatten_cache(raw)

    def __getitem__(self, key: str) -> mx.array:
        if key not in self._flat:
            available = sorted(self._flat.keys())
            raise KeyError(f"Key '{key}' not found. Available keys:\n" + "\n".join(f"  {k}" for k in available))
        return self._flat[key]

    def __contains__(self, key: str) -> bool:
        return key in self._flat

    def keys(self) -> list[str]:
        return sorted(self._flat.keys())

    def flat(self) -> dict[str, mx.array]:
        """Return the flat key → mx.array dict (used for serialization)."""
        return dict(self._flat)

    def __repr__(self) -> str:
        shapes = {k: tuple(v.shape) for k, v in self._flat.items()}
        lines = [f"ActivationCache ({len(self._flat)} tensors):"]
        for k in sorted(shapes):
            lines.append(f"  {k}: {shapes[k]}")
        return "\n".join(lines)
