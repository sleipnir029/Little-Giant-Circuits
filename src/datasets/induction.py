"""
Induction / copying task.

What this task tests
--------------------
Given a sequence where the second half is a repetition of the first half,
predict the next token at each position. In the second half, this requires
the model to recall what token followed the current token the first time it
appeared — which is exactly the computation performed by an induction head.

Example (seq_len=8):
    Sequence:  [3, 7, 1, 5, 3, 7, 1, 5]
    Input:     [3, 7, 1, 5, 3, 7, 1]   (all but last)
    Target:    [7, 1, 5, 3, 7, 1, 5]   (shifted by 1)

Positions 0–3: the model sees a random prefix and must predict the next
random token. Performance here is at chance (~1/vocab_size).

Positions 4–7 (induction positions): the model can now predict correctly
by recalling what followed each token in positions 0–3. A model with a
working induction circuit should reach near-100% accuracy here.

Expected circuit
----------------
Layer 1, some head: "previous token" head — attends to the token just
  before the current token in the sequence.
Layer 2, some head: "induction" head — attends back to wherever the current
  token appeared earlier in the sequence, then looks at what the next token
  was there. This is the head that solves the task.

Evaluation metric
-----------------
Two accuracy numbers are reported:
  - overall: next-token accuracy across all positions
  - induction: next-token accuracy only at positions seq_len//2 onward
    (the positions where the induction circuit is required)

SAMPLE_DATA: 5 example sequences showing input/target/label structure.
"""

import numpy as np


SAMPLE_DATA = [
    {
        "seq_len": 8,
        "sequence": [3, 7, 1, 5, 3, 7, 1, 5],
        "input": [3, 7, 1, 5, 3, 7, 1],
        "target": [7, 1, 5, 3, 7, 1, 5],
        "note": "second half mirrors first; positions 3-6 require induction",
    },
    {
        "seq_len": 8,
        "sequence": [12, 4, 9, 2, 12, 4, 9, 2],
        "input": [12, 4, 9, 2, 12, 4, 9],
        "target": [4, 9, 2, 12, 4, 9, 2],
        "note": "same structure; different prefix",
    },
]


def generate(
    n_samples: int,
    seq_len: int = 16,
    vocab_size: int = 32,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate induction sequences.

    Each sequence is [prefix | prefix] where prefix is a random array of
    length seq_len // 2. The returned inputs/targets are for next-token
    prediction: input = seq[:-1], target = seq[1:].

    Args:
        n_samples:  number of training examples
        seq_len:    total sequence length (must be even)
        vocab_size: number of distinct tokens (tokens drawn from 1..vocab_size-1)
        seed:       random seed for reproducibility

    Returns:
        inputs:  (n_samples, seq_len-1) int array
        targets: (n_samples, seq_len-1) int array
    """
    assert seq_len % 2 == 0, "seq_len must be even for the induction task"
    rng = np.random.default_rng(seed)
    half = seq_len // 2
    # Tokens start at 1 to reserve 0 as a potential pad token in future phases
    prefix = rng.integers(1, vocab_size, size=(n_samples, half))
    sequences = np.concatenate([prefix, prefix], axis=1)  # (N, seq_len)
    inputs = sequences[:, :-1]   # (N, seq_len-1)
    targets = sequences[:, 1:]   # (N, seq_len-1)
    return inputs, targets


def evaluate(
    model,
    inputs: np.ndarray,
    targets: np.ndarray,
    seq_len: int,
    batch_size: int = 64,
) -> dict:
    """
    Evaluate model on induction dataset.

    Returns a dict with:
      overall_acc:   next-token accuracy across all positions
      induction_acc: next-token accuracy at positions seq_len//2 - 1 onward
                     (the positions in 'target' that require the induction circuit)
    """
    import mlx.core as mx

    induction_start = seq_len // 2 - 1  # index into targets where induction kicks in
    n = len(inputs)
    total_correct = 0
    induction_correct = 0
    total_tokens = 0
    induction_tokens = 0

    for start in range(0, n, batch_size):
        x = mx.array(inputs[start : start + batch_size])
        y = mx.array(targets[start : start + batch_size])

        logits = model(x)               # (B, T, vocab)
        preds = mx.argmax(logits, axis=-1)  # (B, T)
        correct = preds == y            # (B, T) bool

        mx.eval(correct)
        correct_np = np.array(correct)

        total_correct += correct_np.sum()
        total_tokens += correct_np.size

        induction_correct += correct_np[:, induction_start:].sum()
        induction_tokens += correct_np[:, induction_start:].size

    return {
        "overall_acc": total_correct / total_tokens,
        "induction_acc": induction_correct / induction_tokens,
    }
