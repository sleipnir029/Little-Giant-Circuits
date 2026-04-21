"""
Key-value retrieval task.

What this task tests
--------------------
Given a sequence of key-value pairs followed by a query key, predict the
value associated with that key. Tests whether the model can implement an
in-context associative lookup.

Sequence format (n_pairs=3, vocab=32):
    [k1, v1, k2, v2, k3, v3, q_key, v_q]   (length = 2*n_pairs + 2)

  Keys:   tokens 1 .. vocab_size//2
  Values: tokens vocab_size//2+1 .. vocab_size-1

For next-token training:
    input:  seq[:-1]  = [k1, v1, ..., q_key]       (length 2*n_pairs+1)
    target: seq[1:]   = [v1, k2, ..., q_key, v_q]  (length 2*n_pairs+1)

The critical signal is at the last target position: model must predict v_q
given only q_key and the key-value pairs seen earlier.

seq_len parameter convention: seq_len = 2*n_pairs + 2, so n_pairs is derived
as (seq_len - 2) // 2. For seq_len=8, n_pairs=3.

Example (n_pairs=2, vocab=16):
    keys=[3,7], values=[11,9], query=3, answer=11
    full sequence: [3, 11, 7, 9, 3, 11]
    input:  [3, 11, 7, 9, 3]
    target: [11, 7, 9, 3, 11]   ← last position 11 is the retrieval answer

Expected circuit
----------------
Lookup heads attend from the query position (q_key) back to key positions
that match the query token, then output the associated value from the next
position. Related to induction but requires content-based matching rather
than position-based.

Evaluation metric
-----------------
last_pos_acc: fraction of examples where model's top prediction at the final
input position equals the correct value token.

SAMPLE_DATA: 3 examples with the corrected 6-token format.
"""

import numpy as np


SAMPLE_DATA = [
    {
        "n_pairs": 2,
        "vocab_size": 16,
        "keys": [3, 7],
        "values": [11, 9],
        "query_key": 3,
        "correct_value": 11,
        "full_sequence": [3, 11, 7, 9, 3, 11],
        "input":  [3, 11, 7, 9, 3],
        "target": [11, 7, 9, 3, 11],
        "note": "query key 3 matches pair 1; expect value 11",
    },
    {
        "n_pairs": 2,
        "vocab_size": 16,
        "keys": [2, 5],
        "values": [12, 10],
        "query_key": 5,
        "correct_value": 10,
        "full_sequence": [2, 12, 5, 10, 5, 10],
        "input":  [2, 12, 5, 10, 5],
        "target": [12, 5, 10, 5, 10],
        "note": "query key 5 matches pair 2; expect value 10",
    },
    {
        "n_pairs": 2,
        "vocab_size": 16,
        "keys": [4, 6],
        "values": [13, 8],
        "query_key": 4,
        "correct_value": 13,
        "full_sequence": [4, 13, 6, 8, 4, 13],
        "input":  [4, 13, 6, 8, 4],
        "target": [13, 6, 8, 4, 13],
        "note": "query key 4 matches pair 1; expect value 13",
    },
]


def generate(
    n_samples: int,
    seq_len: int = 8,
    vocab_size: int = 32,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate key-value retrieval sequences.

    seq_len = 2*n_pairs + 2; n_pairs = (seq_len - 2) // 2.
    Full sequence: [k1, v1, ..., kN, vN, q_key, v_q]
    Returns next-token prediction pairs: (inputs, targets).

    Token ranges:
      Keys:   1 .. vocab_size//2
      Values: vocab_size//2 + 1 .. vocab_size - 1

    Args:
        n_samples:  number of examples
        seq_len:    total sequence length including the answer token (must be even, ≥ 4)
        vocab_size: total vocabulary size (must be even, ≥ 4)
        seed:       random seed

    Returns:
        inputs:  (n_samples, seq_len-1)
        targets: (n_samples, seq_len-1)
    """
    assert seq_len >= 4 and seq_len % 2 == 0, "seq_len must be even and ≥ 4"
    assert vocab_size >= 4 and vocab_size % 2 == 0
    n_pairs = (seq_len - 2) // 2
    rng = np.random.default_rng(seed)
    key_max = vocab_size // 2
    val_min = vocab_size // 2 + 1
    val_max = vocab_size   # exclusive upper bound

    sequences = []
    for _ in range(n_samples):
        keys = rng.choice(key_max - 1, size=n_pairs, replace=False) + 1  # 1..key_max-1
        values = rng.integers(val_min, val_max, size=n_pairs)
        q_idx = rng.integers(n_pairs)
        q_key = int(keys[q_idx])
        q_val = int(values[q_idx])

        seq = []
        for k, v in zip(keys, values):
            seq.extend([int(k), int(v)])
        seq.append(q_key)
        seq.append(q_val)          # answer token — this is the critical signal
        sequences.append(seq)

    full = np.array(sequences, dtype=np.int32)   # (N, seq_len)
    return full[:, :-1], full[:, 1:]              # inputs, targets


def evaluate(
    model,
    inputs: np.ndarray,
    targets: np.ndarray,
    seq_len: int | None = None,
    batch_size: int = 64,
) -> dict:
    """
    Evaluate KV retrieval accuracy.

    The correct value is at targets[:, -1] (the last position of each target
    sequence), so no separate labels array is needed.

    Returns:
      last_pos_acc: fraction correct at the final position (the retrieval answer)
      overall_acc:  next-token accuracy across all positions
    """
    import mlx.core as mx
    import numpy as _np

    n = len(inputs)
    last_correct = 0
    total_correct = 0
    total_tokens = 0

    for start in range(0, n, batch_size):
        x = mx.array(inputs[start : start + batch_size])
        y = mx.array(targets[start : start + batch_size])

        logits = model(x)
        preds = mx.argmax(logits, axis=-1)  # (B, T)
        correct = preds == y
        mx.eval(correct, preds)

        correct_np = _np.array(correct)
        total_correct += correct_np.sum()
        total_tokens += correct_np.size
        # The last position in targets is always the answer value (v_q)
        last_correct += correct_np[:, -1].sum()

    return {
        "last_pos_acc": last_correct / n,
        "overall_acc": total_correct / total_tokens,
    }
