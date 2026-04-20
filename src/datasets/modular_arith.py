"""
Modular arithmetic task.

What this task tests
--------------------
Given two operand tokens (a, b) and an implicit modulus p, predict the result
of (a + b) % p. Tests whether the model can implement a structured algorithmic
transformation using internal representations.

Sequence format:
    [a, b]  →  next token: (a + b) % p

For next-token training, we extend to a length-3 sequence:
    Input:  [a, b]
    Target: [b, result]

where result = (a + b) % p.

Vocabulary layout:
  Tokens 1..p represent integers 0..p-1 (offset by 1 to reserve 0).

Why modular arithmetic
----------------------
This task is well-studied in mechanistic interpretability. Models trained on
modular arithmetic often develop Fourier-like representations in their weight
matrices — the key/query weights encode a discrete Fourier basis over the
circular group Z/pZ. This makes the internals interpretable through frequency
analysis, which Phase 2 will support.

Expected circuit
----------------
The model likely learns to embed a and b as approximate Fourier components,
compute the phase sum in the residual stream, then decode the result. This
requires a non-trivial internal computation that is visible in weight space.

Evaluation metric
-----------------
Last-position accuracy: fraction of examples where model predicts (a+b)%p
at the output position.

SAMPLE_DATA: 5 example (a, b, result) triples for p=13.
"""

import numpy as np


MODULUS = 13  # default prime modulus; adjustable via config


SAMPLE_DATA = [
    {"a": 3, "b": 5, "p": 13, "result": 8, "note": "(3+5)%13=8"},
    {"a": 7, "b": 9, "p": 13, "result": 3, "note": "(7+9)%13=3"},
    {"a": 0, "b": 0, "p": 13, "result": 0, "note": "(0+0)%13=0"},
    {"a": 12, "b": 12, "p": 13, "result": 11, "note": "(12+12)%13=11"},
    {"a": 6, "b": 6, "p": 13, "result": 12, "note": "(6+6)%13=12"},
]


def generate(
    n_samples: int,
    p: int = MODULUS,
    vocab_size: int = 32,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate modular arithmetic examples.

    Tokens a and b are drawn uniformly from 0..p-1.
    All token values are offset by 1 (so token 1 = integer 0, token p = integer p-1).
    Vocab must satisfy vocab_size >= p + 1.

    Args:
        n_samples:  number of examples
        p:          prime modulus (default 13)
        vocab_size: total vocabulary size (unused except for assertion)
        seed:       random seed

    Returns:
        inputs:  (n_samples, 2) — [a_token, b_token]
        targets: (n_samples, 2) — [b_token, result_token] (next-token)
    """
    assert vocab_size >= p + 1, f"vocab_size {vocab_size} < p+1 = {p+1}"
    rng = np.random.default_rng(seed)
    a = rng.integers(0, p, size=n_samples)
    b = rng.integers(0, p, size=n_samples)
    result = (a + b) % p
    # Offset by 1 so token 0 is unused (potential pad)
    a_tok = a + 1
    b_tok = b + 1
    res_tok = result + 1
    inputs = np.stack([a_tok, b_tok], axis=1).astype(np.int32)
    targets = np.stack([b_tok, res_tok], axis=1).astype(np.int32)
    return inputs, targets


def evaluate(
    model,
    inputs: np.ndarray,
    targets: np.ndarray,
    p: int = MODULUS,
    batch_size: int = 64,
) -> dict:
    """
    Evaluate modular arithmetic accuracy.

    Returns:
      last_pos_acc: fraction correct at the result position
      overall_acc:  next-token accuracy across all positions
    """
    import mlx.core as mx

    n = len(inputs)
    last_correct = 0
    total_correct = 0
    total_tokens = 0

    for start in range(0, n, batch_size):
        x = mx.array(inputs[start : start + batch_size])
        y = mx.array(targets[start : start + batch_size])

        logits = model(x)
        preds = mx.argmax(logits, axis=-1)
        correct = preds == y
        mx.eval(correct)

        import numpy as _np
        correct_np = _np.array(correct)
        total_correct += correct_np.sum()
        total_tokens += correct_np.size
        last_correct += correct_np[:, -1].sum()

    return {
        "last_pos_acc": last_correct / n,
        "overall_acc": total_correct / total_tokens,
    }
