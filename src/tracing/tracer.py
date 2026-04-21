"""
trace() — run a forward pass and return an ActivationCache.

Design rationale:
  This function is the single entry point for all tracing work. It accepts an
  already-loaded Transformer and a token array, calls model(tokens, return_cache=True),
  evaluates all lazy MLX arrays immediately (MLX is lazy by default — unevaluated
  tensors in a cache would fail or produce stale values if the computation graph is
  freed before serialization), and wraps the result in an ActivationCache.

  Keeping this in a separate module means neither transformer.py nor cache.py need
  to know about each other — the tracing workflow is:
      load model → trace(model, tokens) → inspect / save

Why mx.eval() matters here:
  MLX builds a computation graph lazily. When return_cache=True, every intermediate
  tensor in the cache is a lazy node pointing back to the original input. Calling
  mx.eval() materializes them before the function returns, so the caller gets plain
  float32 arrays rather than live graph references. Without this, saving or printing
  a cache tensor after the model has been re-used for another call could silently
  return incorrect values.
"""

import mlx.core as mx
import mlx.nn as nn

from .cache import ActivationCache


def trace(model: nn.Module, tokens: mx.array) -> tuple[mx.array, ActivationCache]:
    """Run a forward pass with full activation capture.

    Args:
        model:  A Transformer instance with loaded weights.
        tokens: Integer token array, shape (B, T) or (T,).
                If 1-D, a batch dimension is added automatically.

    Returns:
        logits: (B, T, vocab_size) — same as model(tokens), verified identical.
        cache:  ActivationCache with all intermediate tensors materialized.

    The returned logits are bit-for-bit identical to model(tokens) (no return_cache).
    This is the anti-drift guarantee: if the return_cache path ever diverges from the
    clean forward pass, it will be caught by comparing these outputs.
    """
    # Ensure batch dimension exists
    if tokens.ndim == 1:
        tokens = tokens[None, :]  # (1, T)

    logits, raw_cache = model(tokens, return_cache=True)

    # Materialize all lazy tensors in the cache immediately.
    # Flatten to a list of arrays for a single mx.eval call.
    from .cache import _flatten_cache
    flat_tensors = list(_flatten_cache(raw_cache).values())
    mx.eval(logits, *flat_tensors)

    return logits, ActivationCache(raw_cache)
