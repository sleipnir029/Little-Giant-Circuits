"""
Simple factual lookup task.

What this task tests
--------------------
Given a "subject" token, predict its associated "attribute" token — a fixed
one-to-one mapping baked into the training data. This is the simplest form of
factual association: the model must store and retrieve a discrete binding between
pairs of tokens, with no contextual variation.

Relation to key-value retrieval
--------------------------------
This task overlaps with kv_retrieval.py in spirit but differs in structure:
  - kv_retrieval: multiple pairs in-context, query at the end (in-context learning)
  - factual_lookup: single pair per sequence, mapping is fixed across all examples
                    (the model memorizes a lookup table, not learns from context)

In real language models, "Paris is the capital of France" is this kind of
binding. Here we study the minimal version: token 3 always maps to token 19.

Sequence format:
    Input:  [subject]        → single-token context
    Target: [attribute]      → single next-token prediction

We extend to a short context to give the model more signal:
    [pad, subject]  → [subject, attribute]

where pad = 0 (reserved) provides a neutral prefix so the model isn't
predicting from a completely empty context.

Vocabulary layout:
  Subjects:    1 .. vocab_size//2
  Attributes:  vocab_size//2+1 .. vocab_size-1

Expected circuit
----------------
The subject→attribute map is stored in the MLP weight matrices (key-value
memory in FFN layers, as studied by Meng et al. 2022). Phase 6 SAE work
should find sparse features corresponding to individual (subject, attribute)
pairs.

Evaluation metric
-----------------
Single-position accuracy: fraction correct at the attribute prediction position.

SAMPLE_DATA: 5 example (subject, attribute) pairs.
"""

import numpy as np


SAMPLE_DATA = [
    {"subject": 1, "attribute": 17, "note": "subject 1 → attribute 17"},
    {"subject": 2, "attribute": 21, "note": "subject 2 → attribute 21"},
    {"subject": 3, "attribute": 19, "note": "subject 3 → attribute 19"},
    {"subject": 4, "attribute": 22, "note": "subject 4 → attribute 22"},
    {"subject": 5, "attribute": 18, "note": "subject 5 → attribute 18"},
]


def _make_lookup_table(vocab_size: int, seed: int) -> np.ndarray:
    """Create a fixed subject→attribute mapping for this vocab/seed combination."""
    rng = np.random.default_rng(seed)
    n_subjects = vocab_size // 2
    attr_min = vocab_size // 2 + 1
    attr_max = vocab_size
    attributes = rng.integers(attr_min, attr_max, size=n_subjects)
    return attributes  # index i → attribute for subject (i+1)


def generate(
    n_samples: int,
    seq_len: int = 2,   # accepted for interface compatibility with train.py; ignored
    vocab_size: int = 32,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate factual lookup sequences.

    The subject→attribute mapping is deterministic given vocab_size and seed,
    and fixed across all samples. The model must memorize this mapping.

    targets[:, -1] == the correct attribute for each example, so evaluate()
    derives labels from targets rather than needing a separate return value.

    Args:
        n_samples:  number of examples (subjects sampled uniformly with replacement)
        seq_len:    ignored (sequences are always length 2); kept for interface consistency
        vocab_size: total vocabulary (must be even)
        seed:       random seed for both lookup table and sampling

    Returns:
        inputs:  (n_samples, 2) — [0, subject_token]  (0=pad prefix)
        targets: (n_samples, 2) — [subject_token, attribute_token]
    """
    assert vocab_size >= 4 and vocab_size % 2 == 0
    rng = np.random.default_rng(seed)
    lookup = _make_lookup_table(vocab_size, seed)
    n_subjects = vocab_size // 2

    subjects = rng.integers(1, n_subjects + 1, size=n_samples).astype(np.int32)
    attributes = lookup[subjects - 1].astype(np.int32)

    inputs = np.stack([np.zeros(n_samples, dtype=np.int32), subjects], axis=1)
    targets = np.stack([subjects, attributes], axis=1)

    return inputs, targets


def evaluate(
    model,
    inputs: np.ndarray,
    targets: np.ndarray,
    seq_len: int = 2,  # accepted for interface compatibility; ignored
    batch_size: int = 64,
) -> dict:
    """
    Evaluate factual lookup accuracy.

    Labels are derived from targets[:, -1] (the attribute position).

    Returns:
      lookup_acc:  fraction correct at the attribute position (last position)
      overall_acc: next-token accuracy across all positions
    """
    import mlx.core as mx
    import numpy as _np

    labels = targets[:, -1]  # attribute token is always the last target position
    n = len(inputs)
    lookup_correct = 0
    total_correct = 0
    total_tokens = 0

    for start in range(0, n, batch_size):
        x = mx.array(inputs[start : start + batch_size])
        y = mx.array(targets[start : start + batch_size])

        logits = model(x)
        preds = mx.argmax(logits, axis=-1)
        correct = preds == y
        mx.eval(correct, preds)

        correct_np = _np.array(correct)
        preds_np = _np.array(preds[:, -1])
        labels_batch = labels[start : start + batch_size]

        total_correct += correct_np.sum()
        total_tokens += correct_np.size
        lookup_correct += (preds_np == labels_batch).sum()

    return {
        "lookup_acc": lookup_correct / n,
        "overall_acc": total_correct / total_tokens,
    }
