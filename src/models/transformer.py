"""
Tiny decoder-only transformer for toy sequence tasks.

This model is written from scratch in MLX so every line of the forward pass
is visible and inspectable. No mlx-lm or pretrained classes are used.

Architecture
------------
  token embedding (vocab_size → d_model)
  + positional embedding (seq_len → d_model, learnable)
  → N pre-norm transformer blocks
    each block: LayerNorm → Attention → residual
                LayerNorm → MLP      → residual
  → final LayerNorm
  → linear output head (d_model → vocab_size)

Hard limits enforced in ModelConfig (see utils/config.py):
  d_model <= 64, n_layers <= 2, n_heads <= 4, seq_len <= 32, vocab <= 64

Pre-norm vs. post-norm: pre-norm (LN before the sublayer) is more stable
at small scale and keeps residual stream values less distorted, which matters
for interpretability experiments in Phase 2+.

Tracing (Phase 2)
-----------------
Pass return_cache=True to any __call__ to get back (output, cache_dict) instead
of just output. The cache dict uses TransformerLens-style flat dotted keys when
accessed via ActivationCache (see src/tracing/cache.py). Training code always
calls model(x) with no extra arguments — the default return_cache=False path is
identical to the original forward pass.
"""

import math
from typing import Union

import mlx.core as mx
import mlx.nn as nn

# Type alias used in return annotations below.
# When return_cache=False: returns mx.array.
# When return_cache=True: returns (mx.array, dict).
_AttnReturn = Union[mx.array, tuple[mx.array, dict]]
_BlockReturn = Union[mx.array, tuple[mx.array, dict]]
_ModelReturn = Union[mx.array, tuple[mx.array, dict]]


class MultiHeadSelfAttention(nn.Module):
    """Causal multi-head self-attention.

    Each head attends over all previous positions (including current).
    Head dimension: d_head = d_model // n_heads.
    No bias on projection matrices — keeps weight inspection cleaner.
    """

    def __init__(self, d_model: int, n_heads: int) -> None:
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.q = nn.Linear(d_model, d_model, bias=False)
        self.k = nn.Linear(d_model, d_model, bias=False)
        self.v = nn.Linear(d_model, d_model, bias=False)
        self.out = nn.Linear(d_model, d_model, bias=False)

    def __call__(self, x: mx.array, return_cache: bool = False) -> _AttnReturn:
        B, T, D = x.shape
        H, Dh = self.n_heads, self.d_head

        # Project then reshape to (B, H, T, Dh) for batched head-parallel matmul
        q = self.q(x).reshape(B, T, H, Dh).transpose(0, 2, 1, 3)
        k = self.k(x).reshape(B, T, H, Dh).transpose(0, 2, 1, 3)
        v = self.v(x).reshape(B, T, H, Dh).transpose(0, 2, 1, 3)

        # Scaled dot-product attention
        scores = (q @ k.transpose(0, 1, 3, 2)) / math.sqrt(Dh)  # (B, H, T, T)

        # Causal mask: upper triangle gets -inf so softmax assigns it ~0 weight
        causal = mx.where(mx.tril(mx.ones((T, T))) == 1, 0.0, float("-inf"))
        scores = scores + causal  # post-mask, pre-softmax — saved as "scores" in cache

        pattern = mx.softmax(scores, axis=-1)  # post-softmax — saved as "pattern"
        out = (pattern @ v).transpose(0, 2, 1, 3).reshape(B, T, D)
        result = self.out(out)

        if not return_cache:
            return result

        return result, {
            "q": q,           # (B, H, T, Dh) — Q projections per head
            "k": k,           # (B, H, T, Dh)
            "v": v,           # (B, H, T, Dh)
            "scores": scores, # (B, H, T, T) — post-mask pre-softmax; "what it wants"
            "pattern": pattern, # (B, H, T, T) — post-softmax; "what it actually attends"
            "output": result, # (B, T, d_model) — full attention output
        }


class TransformerBlock(nn.Module):
    """Pre-norm transformer block: LN → Attention → add; LN → MLP → add."""

    def __init__(self, d_model: int, n_heads: int) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadSelfAttention(d_model, n_heads)
        self.ln2 = nn.LayerNorm(d_model)
        # MLP expansion ratio 4× is standard; for d_model=64 that is 256 hidden units
        self.mlp1 = nn.Linear(d_model, 4 * d_model)
        self.mlp2 = nn.Linear(4 * d_model, d_model)

    def __call__(self, x: mx.array, return_cache: bool = False) -> _BlockReturn:
        if not return_cache:
            x = x + self.attn(self.ln1(x))
            x = x + self.mlp2(nn.gelu(self.mlp1(self.ln2(x))))
            return x

        resid_pre = x

        # Attention sublayer
        attn_out, attn_cache = self.attn(self.ln1(x), return_cache=True)
        x = x + attn_out
        resid_mid = x  # residual stream between attention and MLP

        # MLP sublayer — capture pre/post GELU for neuron-level analysis
        mlp_pre = self.mlp1(self.ln2(x))    # (B, T, 4*d_model) — before GELU
        mlp_post = nn.gelu(mlp_pre)          # (B, T, 4*d_model) — after GELU
        mlp_out = self.mlp2(mlp_post)        # (B, T, d_model) — MLP contribution
        x = x + mlp_out
        resid_post = x

        return x, {
            "resid_pre": resid_pre,   # (B, T, d_model)
            "resid_mid": resid_mid,   # (B, T, d_model)
            "resid_post": resid_post, # (B, T, d_model)
            "attn": attn_cache,
            "mlp": {
                "pre": mlp_pre,     # (B, T, 4*d_model) — before nonlinearity
                "post": mlp_post,   # (B, T, 4*d_model) — after nonlinearity
                "output": mlp_out,  # (B, T, d_model) — contribution to residual
            },
        }


class Transformer(nn.Module):
    """
    Tiny decoder-only transformer.

    Usage:
        model = Transformer(vocab_size=32, d_model=64, n_layers=2, n_heads=4, seq_len=16)
        logits = model(x)  # x: (batch, seq_len) int32 → logits: (batch, seq_len, vocab)

    For tracing (returns activation cache alongside logits):
        logits, cache = model(x, return_cache=True)
        # cache is a nested dict; use ActivationCache(cache) for dot-key access
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        n_layers: int,
        n_heads: int,
        seq_len: int,
    ) -> None:
        super().__init__()
        self.tok_embed = nn.Embedding(vocab_size, d_model)
        self.pos_embed = nn.Embedding(seq_len, d_model)
        self.blocks = [TransformerBlock(d_model, n_heads) for _ in range(n_layers)]
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def __call__(self, x: mx.array, return_cache: bool = False) -> _ModelReturn:
        """x: (B, T) integer token indices. Returns logits (B, T, vocab_size)."""
        B, T = x.shape
        positions = mx.arange(T)
        tok_emb = self.tok_embed(x)       # (B, T, d_model)
        pos_emb = self.pos_embed(positions)  # (T, d_model) — broadcast over batch
        h = tok_emb + pos_emb

        if not return_cache:
            for block in self.blocks:
                h = block(h)
            return self.head(self.ln_f(h))

        block_caches = []
        for block in self.blocks:
            h, block_cache = block(h, return_cache=True)
            block_caches.append(block_cache)

        ln_f_input = h
        logits = self.head(self.ln_f(h))

        raw_cache = {
            "embed": {
                "tok": tok_emb,   # (B, T, d_model)
                "pos": pos_emb,   # (T, d_model)
                "combined": h,    # (B, T, d_model) — tok_emb + pos_emb already computed
            },
            "blocks": block_caches,   # list of per-block dicts
            "ln_f": {
                "input": ln_f_input,  # (B, T, d_model) — input to final LayerNorm
            },
            "logits": logits,         # (B, T, vocab_size)
        }
        return logits, raw_cache
