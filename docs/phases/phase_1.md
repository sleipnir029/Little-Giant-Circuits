# Phase 1 — Tiny Transformer Training

> This file will be filled in as Phase 1 progresses. Use `docs/phases/TEMPLATE.md` as the guide.
> Do not pre-fill speculatively — content here should reflect what actually happened, not what was planned.

---

## Overview

**Phase number:** 1
**Phase name:** Tiny transformer training
**Status:** IN PROGRESS
**Started:** 2026-04-21
**Completed:** *(pending)*

---

## Goals

*From `PROJECT_PLAN.md §6 Phase 1`:*

- [x] Dataset generators for six synthetic tasks
- [x] Tokenization pipeline (integer vocab; no external tokenizer)
- [x] Tiny transformer implemented in MLX (from scratch, <150 lines)
- [x] Training loop (`src/training/loop.py` + `train.py`)
- [x] Checkpoint saving (`checkpoints/{task}/{step:07d}/`, 4-file format)
- [x] Metrics logging (`runs/{task}/{timestamp}/train_log.txt`)

**Six tasks:**
- Key-value retrieval
- Induction / copying
- Modular arithmetic
- Bracket matching
- Simple factual lookup
- Sorting / reversal

---

## Prerequisites (must be resolved before Phase 1 begins)

From `docs/phase_context/open_questions.md`:

- [x] **Q1** — Package manager: pip + venv (resolved 2026-04-21)
- [x] **Q2** — PyTorch device target: CPU-only for Phase 2 bridge (decided 2026-04-21)
- [x] **Q3** — Python version floor: 3.11 (resolved 2026-04-21)
- [x] **Q8** — Tooling: Phase 1 opener (ruff + pyright, no CI yet) (resolved 2026-04-21)
- [x] Opus Phase 1 review notes written into `docs/phase_context/review_notes.md §10` (2026-04-21)

---

## Learning Outcomes

*From `PROJECT_PLAN.md §6 Phase 1`:*

- Understand next-token learning in a small setting
- Connect training objective to model behavior
- Observe learning progression through checkpoints

---

## What Was Built

### Tooling
- `pyproject.toml` — project metadata, requires-python >= 3.11
- `requirements.txt` — mlx==0.31.1, numpy>=1.26.0
- `ruff.toml` — linting config (E, F, W, I rules, line-length 100)
- `pyrightconfig.json` — basic type coverage, strict=false

### Source tree
- `src/models/transformer.py` — from-scratch decoder-only transformer in MLX
  - `MultiHeadSelfAttention`, `TransformerBlock`, `Transformer` classes
  - Pre-norm architecture; causal mask per forward pass; no mlx-lm classes used
- `src/utils/config.py` — `ModelConfig` + `TrainConfig` dataclasses with hard architecture ceilings
- `src/utils/checkpoint.py` — save/load with 4-file format (weights, config, metrics, meta)
- `src/training/loop.py` — `loss_fn`, `make_train_step`, `get_batch`, `compute_accuracy`
- `src/training/train.py` — CLI entry point: `python src/training/train.py --task induction`

### Datasets (all 6 task modules)
- `src/datasets/induction.py` — TRAINED; see training results below
- `src/datasets/kv_retrieval.py` — stub complete; known targets bug (FIXME in source); not trained
- `src/datasets/modular_arith.py` — stub complete, not yet trained
- `src/datasets/bracket_match.py` — stub complete, not yet trained
- `src/datasets/factual_lookup.py` — TRAINED; see training results below
- `src/datasets/sorting.py` — stub complete (reversal + sorting modes), not yet trained

Each module includes: module docstring, `generate()`, `evaluate()`, `SAMPLE_DATA`.

### Training results (induction task)
Run: `python src/training/train.py --task induction --steps 2000`
- Runtime: ~11 seconds (MLX on Apple Silicon M1 Air)
- Final loss: ~1.54
- Overall next-token accuracy: 57.0% (first-half at chance; expected)
- **Induction accuracy: 100.0%** (positions seq_len//2 onward)
- Holdout eval (seed=999, 1000 examples): induction_acc = 100.0% — generalizes

Checkpoint loading verified: fresh model loaded from `checkpoints/induction/0002000/`,
re-evaluated, same accuracy — checkpoint round-trip confirmed.

### Training results (factual_lookup task)
Run: `python src/training/train.py --task factual_lookup --seq_len 2 --steps 2000`
- Runtime: ~10 seconds (MLX on Apple Silicon M1 Air)
- Final loss: 1.3753
- Overall next-token accuracy: 53.1% (position 0 predicts subject from pad — at chance)
- **lookup_acc: 100.0%** (attribute prediction at position 1 — perfectly solved)
- Expected circuit: FFN key-value memory (subject→attribute binding in MLP weights)

Note: seq_len=2 because the sequence is [pad, subject] → [subject, attribute]. The
overall_acc of 53% is correct: half the positions are chance, half are solved.

---

## Key Decisions Made

1. **Pre-norm over post-norm**: LayerNorm applied before each sublayer. More stable
   at small scale; residual stream values less distorted — better for Phase 2 tracing.

2. **No mlx-lm model classes**: Transformer written from scratch so every line of
   the forward pass is inspectable. This is a hard requirement from Opus §10.8.

3. **Causal mask per forward pass**: `mx.tril(mx.ones((T, T)))` created inside `__call__`.
   Less efficient than caching but maximally transparent for readers and debuggers.

4. **List-aware checkpoint unflatten**: MLX list parameters (e.g., `blocks=[Block, Block]`)
   serialize as `blocks.0.attn.q.weight`. The unflatten function detects consecutive
   integer keys and reconstructs Python lists for `model.update()`.

5. **Token offset**: All task generators start tokens at 1, reserving 0 as a potential
   pad token for Phase 2 batching with variable-length sequences.

6. **Induction accuracy definition**: Positions `seq_len//2 - 1` onward in the target
   array (the "second half" positions where the induction circuit is required). Position
   `seq_len//2 - 1` predicts the first token of the second copy from the last token
   of the first copy — not a pure induction case, but included as a conservative metric.

---

## Retrospective

*(Fill in at phase close)*
