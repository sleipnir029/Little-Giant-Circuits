"""
Bracket matching task.

What this task tests
--------------------
Given a sequence of opening and closing brackets, predict the next bracket.
Tests whether the model can track a "depth counter" — an internal state that
increments on '(' and decrements on ')'. This requires persistent state across
many tokens, which is non-trivial for pure attention mechanisms.

Vocabulary:
  Token 1: '(' (open bracket)
  Token 2: ')' (close bracket)
  Token 3: 'B' (balanced — optionally used as sequence terminator)

Sequence structure:
  Sequences are generated from a simple grammar that produces balanced bracket
  strings. The model's task is next-token prediction: at each position, predict
  whether the next token is '(' or ')'.

At any position, the correct next token is determined by the current "balance"
(open - close so far) and the remaining required tokens. A model solving this
task must track the running balance across the full sequence.

Example (depth-1 only):
  Input:  [1, 2, 1]   (= '(', ')', '(')
  Target: [2, 1, 2]   (= ')', '(', ')')

Why this is hard
----------------
Unlike induction, the relevant past context is not a single previous token —
it's a COUNT accumulated across all previous positions. This may require the
model to use multiple heads together to maintain this count.

Expected circuit
----------------
One or more heads implement a "balance tracker": at each position, they
compute a weighted sum of previous tokens (roughly: +1 for each open, -1
for each close) to determine the current depth. The MLP may then decode this
depth into a prediction of the next bracket.

Evaluation metric
-----------------
Next-token accuracy. A useful secondary metric is "syntactic violation rate":
fraction of predictions that would produce an unbalanced prefix.

SAMPLE_DATA: 5 example sequences.
"""

import numpy as np

OPEN = 1
CLOSE = 2


SAMPLE_DATA = [
    {
        "bracket_str": "(())",
        "sequence": [1, 1, 2, 2],
        "input": [1, 1, 2],
        "target": [1, 2, 2],
        "note": "depth goes 1→2→1→0",
    },
    {
        "bracket_str": "()()",
        "sequence": [1, 2, 1, 2],
        "input": [1, 2, 1],
        "target": [2, 1, 2],
        "note": "alternating open/close",
    },
    {
        "bracket_str": "((()))",
        "sequence": [1, 1, 1, 2, 2, 2],
        "input": [1, 1, 1, 2, 2],
        "target": [1, 1, 2, 2, 2],
        "note": "nested depth 3",
    },
]


def _generate_balanced(rng: np.random.Generator, seq_len: int) -> list[int] | None:
    """Generate one balanced bracket sequence of length seq_len using a random walk.

    Returns None if unable to generate a valid sequence in this attempt.
    seq_len must be even.
    """
    assert seq_len % 2 == 0
    half = seq_len // 2
    seq = []
    depth = 0
    remaining_open = half
    remaining_close = half

    for i in range(seq_len):
        remaining = seq_len - i
        can_open = remaining_open > 0
        can_close = depth > 0 and remaining_close > 0
        must_close = depth == remaining  # must close all remaining

        if must_close:
            choice = CLOSE
        elif not can_close:
            choice = OPEN
        else:
            choice = int(rng.choice([OPEN, CLOSE]))

        seq.append(choice)
        if choice == OPEN:
            depth += 1
            remaining_open -= 1
        else:
            depth -= 1
            remaining_close -= 1

    return seq if depth == 0 else None


def generate(
    n_samples: int,
    seq_len: int = 16,
    vocab_size: int = 32,  # unused; kept for interface consistency
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate balanced bracket sequences for next-token prediction.

    Each sequence has equal numbers of '(' and ')' and is fully balanced.
    seq_len must be even.

    Args:
        n_samples:  number of examples
        seq_len:    total sequence length (must be even)
        vocab_size: unused (bracket vocab is always {1=OPEN, 2=CLOSE})
        seed:       random seed

    Returns:
        inputs:  (n_samples, seq_len-1)
        targets: (n_samples, seq_len-1)
    """
    assert seq_len % 2 == 0, "seq_len must be even for bracket matching"
    rng = np.random.default_rng(seed)
    sequences = []

    while len(sequences) < n_samples:
        seq = _generate_balanced(rng, seq_len)
        if seq is not None:
            sequences.append(seq)

    arr = np.array(sequences, dtype=np.int32)
    return arr[:, :-1], arr[:, 1:]


def evaluate(
    model,
    inputs: np.ndarray,
    targets: np.ndarray,
    seq_len: int | None = None,  # unused; accepted for train.py compatibility
    batch_size: int = 64,
) -> dict:
    """
    Evaluate bracket matching accuracy.

    Returns:
      overall_acc: next-token accuracy across all positions
    """
    import mlx.core as mx

    n = len(inputs)
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

    return {"overall_acc": total_correct / total_tokens}
