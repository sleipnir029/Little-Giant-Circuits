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
"""

import math

import mlx.core as mx
import mlx.nn as nn


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

    def __call__(self, x: mx.array) -> mx.array:
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
        scores = scores + causal

        attn = mx.softmax(scores, axis=-1)
        out = (attn @ v).transpose(0, 2, 1, 3).reshape(B, T, D)
        return self.out(out)


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

    def __call__(self, x: mx.array) -> mx.array:
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp2(nn.gelu(self.mlp1(self.ln2(x))))
        return x


class Transformer(nn.Module):
    """
    Tiny decoder-only transformer.

    Usage:
        model = Transformer(vocab_size=32, d_model=64, n_layers=2, n_heads=4, seq_len=16)
        logits = model(x)  # x: (batch, seq_len) int32 → logits: (batch, seq_len, vocab)
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

    def __call__(self, x: mx.array) -> mx.array:
        """x: (B, T) integer token indices. Returns logits (B, T, vocab_size)."""
        B, T = x.shape
        positions = mx.arange(T)
        h = self.tok_embed(x) + self.pos_embed(positions)
        for block in self.blocks:
            h = block(h)
        return self.head(self.ln_f(h))
