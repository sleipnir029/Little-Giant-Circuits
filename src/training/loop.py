"""
Training step utilities.

Keeps the single-step mechanics separate from the training orchestration
in train.py. Nothing in this file knows about tasks, checkpoints, or logging.
"""

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim


def loss_fn(model: nn.Module, x: mx.array, y: mx.array) -> mx.array:
    """Cross-entropy loss over all token positions."""
    logits = model(x)           # (B, T, V)
    B, T, V = logits.shape
    return mx.mean(nn.losses.cross_entropy(logits.reshape(B * T, V), y.reshape(B * T)))


def make_train_step(model: nn.Module):
    """Return a compiled train_step function bound to model.

    Using nn.value_and_grad (not mx.value_and_grad) because model parameters
    are the implicit state — this handles MLX's functional gradient API correctly.
    """
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    def train_step(
        optimizer: optim.Optimizer, x: mx.array, y: mx.array
    ) -> float:
        loss, grads = loss_and_grad(model, x, y)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), loss)
        return loss.item()

    return train_step


def get_batch(
    inputs: np.ndarray,
    targets: np.ndarray,
    batch_size: int,
    rng: np.random.Generator,
) -> tuple[mx.array, mx.array]:
    """Sample a random batch from numpy arrays."""
    idx = rng.integers(len(inputs), size=batch_size)
    return mx.array(inputs[idx]), mx.array(targets[idx])


def compute_accuracy(model: nn.Module, x: mx.array, y: mx.array) -> float:
    """Next-token accuracy (fraction of positions predicted correctly)."""
    logits = model(x)
    preds = mx.argmax(logits, axis=-1)  # (B, T)
    acc = mx.mean(preds == y)
    mx.eval(acc)
    return acc.item()
