"""
Phase 2 tracing module.

Public API:
    trace(model, tokens)             → ActivationCache
    save_trace(cache, tokens, ...)   → saves activations.safetensors + trace_meta.json
    load_trace(trace_dir)            → (ActivationCache, meta_dict)
"""

from .cache import ActivationCache
from .export import load_trace, save_trace
from .tracer import trace

__all__ = ["ActivationCache", "trace", "save_trace", "load_trace"]
