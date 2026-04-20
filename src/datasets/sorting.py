"""
Sorting / reversal task.

What this task tests
--------------------
Given a random sequence of tokens, predict the sorted (or reversed) version.
Tests whether the model can implement a comparison-based reordering of tokens —
a task that requires attending across the entire input and performing a
non-local transformation.

This is the most complex of the six Phase 1 tasks because:
  1. The output at each position depends on ALL input positions (not just one).
  2. The model must solve the "which token goes here?" question, not just "what
     follows this token?".
  3. For larger inputs, this task may require O(n²) comparisons, which stress-
     tests the attention mechanism.

Two variants
------------
  - reversal: output = reverse of input (simpler, position-based, no comparison)
  - sorting:  output = sorted input (harder, requires comparison)

We implement reversal as the default because it is position-based and more
tractable at tiny model scale. Sorting is included as a mode parameter.

Sequence format (reversal, seq_len=8):
    Input:  [3, 1, 4, 1, SEP]          (prefix + separator)
    Target: [1, 4, 1, 3, 1, 4, 1, 3]  (interleaved or sequential)

For simplicity, we use a next-token format over the concatenated sequence:
    Full:   [3, 1, 4, 1, SEP, 1, 4, 1, 3]  (input + SEP + reversed output)
    Input:  [3, 1, 4, 1, SEP, 1, 4, 1]
    Target: [1, 4, 1, SEP, 1, 4, 1, 3]
    (model only needs to predict the output half correctly)

Vocabulary layout:
  Content tokens: 1 .. vocab_size-2
  SEP token:      vocab_size - 1

Expected circuit
----------------
For reversal: position-based attention. A head at output position i should
attend to input position (half - 1 - i) to copy the correct token.
For sorting: comparison-based circuit, likely more complex than any other task.

Evaluation metric
-----------------
Output accuracy: fraction correct at positions after SEP (the prediction
region where the model must output the reordered sequence).

SAMPLE_DATA: 3 example reversal sequences.
"""

import numpy as np


SAMPLE_DATA = [
    {
        "mode": "reversal",
        "input_half": [3, 1, 4, 1],
        "reversed": [1, 4, 1, 3],
        "full_sequence": [3, 1, 4, 1, 99, 1, 4, 1, 3],  # SEP=99
        "note": "reverse of [3,1,4,1] is [1,4,1,3]",
    },
    {
        "mode": "reversal",
        "input_half": [5, 2, 8],
        "reversed": [8, 2, 5],
        "full_sequence": [5, 2, 8, 99, 8, 2, 5],
        "note": "reverse of [5,2,8] is [8,2,5]",
    },
]


def generate(
    n_samples: int,
    seq_len: int = 16,
    vocab_size: int = 32,
    seed: int = 42,
    mode: str = "reversal",
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate sorting/reversal sequences.

    The full sequence is: [input_half | SEP | output_half].
    Input to the model is all but the last token; target is shifted by 1.
    The model needs to correctly predict the output_half tokens.

    seq_len must be odd: (input_half_len) + 1 (SEP) + (output_half_len),
    where input_half_len == output_half_len.
    We use total_len = 2 * half + 1 where half = (seq_len - 1) // 2.

    Args:
        n_samples:  number of examples
        seq_len:    total sequence length (should be odd: 2k+1)
        vocab_size: total vocabulary; SEP = vocab_size - 1
        seed:       random seed
        mode:       "reversal" (default) or "sorting"

    Returns:
        inputs:  (n_samples, 2*half)       — full sequence minus last token
        targets: (n_samples, 2*half)       — shifted by 1
    """
    assert mode in ("reversal", "sorting"), f"mode must be 'reversal' or 'sorting'"
    rng = np.random.default_rng(seed)
    SEP = vocab_size - 1
    half = (seq_len - 1) // 2

    input_halves = rng.integers(1, SEP, size=(n_samples, half)).astype(np.int32)

    if mode == "reversal":
        output_halves = input_halves[:, ::-1].copy()
    else:
        output_halves = np.sort(input_halves, axis=1)

    sep_col = np.full((n_samples, 1), SEP, dtype=np.int32)
    full = np.concatenate([input_halves, sep_col, output_halves], axis=1)  # (N, 2*half+1)
    return full[:, :-1], full[:, 1:]


def evaluate(
    model,
    inputs: np.ndarray,
    targets: np.ndarray,
    seq_len: int,
    batch_size: int = 64,
) -> dict:
    """
    Evaluate sorting/reversal accuracy.

    Reports accuracy separately for:
      output_acc:  positions after the SEP token (where reordering happens)
      overall_acc: all positions
    """
    import mlx.core as mx
    import numpy as _np

    half = (seq_len - 1) // 2
    sep_idx = half       # SEP is at position `half` in the full sequence
    # In targets (shifted by 1), the output_half starts at index sep_idx
    output_start = sep_idx

    n = len(inputs)
    output_correct = 0
    output_tokens = 0
    total_correct = 0
    total_tokens = 0

    for start in range(0, n, batch_size):
        x = mx.array(inputs[start : start + batch_size])
        y = mx.array(targets[start : start + batch_size])

        logits = model(x)
        preds = mx.argmax(logits, axis=-1)
        correct = preds == y
        mx.eval(correct)

        correct_np = _np.array(correct)
        total_correct += correct_np.sum()
        total_tokens += correct_np.size
        output_correct += correct_np[:, output_start:].sum()
        output_tokens += correct_np[:, output_start:].size

    return {
        "output_acc": output_correct / output_tokens,
        "overall_acc": total_correct / total_tokens,
    }
