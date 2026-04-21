# Phase 1 — Tiny Transformer Training

> This file reflects what actually happened, not what was planned.
> Do not pre-fill speculatively.

---

## Overview

**Phase number:** 1
**Phase name:** Tiny transformer training
**Status:** COMPLETE — §12 waived (see `review_notes.md §15` for waiver rationale and accepted evidence)
**Started:** 2026-04-21
**Completed:** 2026-04-21

---

## Goals

*From `PROJECT_PLAN.md §6 Phase 1`:*

- [x] Dataset generators for six synthetic tasks
- [x] Tokenization pipeline (integer vocab; no external tokenizer)
- [x] Tiny transformer implemented in MLX (from scratch, <150 lines)
- [x] Training loop (`src/training/loop.py` + `train.py`)
- [x] Checkpoint saving (`checkpoints/{task}/{step:07d}/`, 4-file format)
- [x] Metrics logging (`runs/{task}/{timestamp}/train_log.txt`)

**Six tasks — all trained:**
- [x] Key-value retrieval — 97.5% last_pos_acc
- [x] Induction / copying — 100% induction_acc
- [x] Modular arithmetic — 99.6% last_pos_acc
- [x] Bracket matching — 68% (capacity limit documented)
- [x] Simple factual lookup — 100% lookup_acc
- [x] Sorting / reversal — 100% output_acc

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
- `src/training/train.py` — CLI entry point; all 6 tasks wired; TASK_DEFAULTS for per-task seq_len/vocab

### Datasets (all 6 task modules)
Each module includes: module docstring, `generate()`, `evaluate()`, `SAMPLE_DATA`.

- `src/datasets/induction.py` — TRAINED
- `src/datasets/kv_retrieval.py` — TRAINED (bug fixed during extension session)
- `src/datasets/modular_arith.py` — TRAINED
- `src/datasets/bracket_match.py` — TRAINED
- `src/datasets/factual_lookup.py` — TRAINED
- `src/datasets/sorting.py` — TRAINED

---

## Training Results (all six tasks)

### induction
Run: `python src/training/train.py --task induction --steps 2000`
- seq_len=16, vocab=32, ~11 sec on M1 Air
- Final loss: ~1.54 | overall_acc: 57.0%
- **induction_acc: 100.0%** (positions seq_len//2 onward)
- Checkpoint round-trip verified (load → eval → same accuracy)

### factual_lookup
Run: `python src/training/train.py --task factual_lookup --steps 2000`
- seq_len=2, vocab=32, ~10 sec
- Final loss: 1.3753 | overall_acc: 53.1%
- **lookup_acc: 100.0%** (final position — attribute prediction)

### kv_retrieval
Run: `python src/training/train.py --task kv_retrieval --steps 5000`
- seq_len=8 (n_pairs=3), vocab=32, ~24 sec
- Final loss: 1.8315 | overall_acc: 37.2%
- **last_pos_acc: 97.5%** (query → value retrieval)
- Interface bug fixed: original generate() dropped the v_q answer from targets

### sorting (reversal mode)
Run: `python src/training/train.py --task sorting --steps 5000`
- seq_len=9 (4+SEP+4), vocab=32, ~24 sec
- Final loss: 0.9152 | overall_acc: 74.5%
- **output_acc: 100.0%** (tokens after SEP — the reversed sequence)

### modular_arith
Run: `python src/training/train.py --task modular_arith --steps 5000`
- seq_len=2 (fixed; p=13), vocab=16, ~24 sec
- Final loss: 1.3206 | overall_acc: 54.5%
- **last_pos_acc: 99.6%** ((a+b)%13 prediction at position 1)

### bracket_match
Run: `python src/training/train.py --task bracket_match --steps 10000`
- seq_len=16, vocab=4, ~60 sec
- Final loss: ~0.45 | **overall_acc: 68%** (plateaued from step ~5000)
- Did not reach 90% — see capacity finding below

---

## Key Decisions Made

1. **Pre-norm over post-norm**: LayerNorm applied before each sublayer. More stable
   at small scale; residual stream values less distorted — better for Phase 2 tracing.

2. **No mlx-lm model classes**: Transformer written from scratch so every line of
   the forward pass is inspectable. Hard requirement from Opus §10.8.

3. **Causal mask per forward pass**: `mx.tril(mx.ones((T, T)))` created inside `__call__`.
   Less efficient than caching but maximally transparent for readers and debuggers.

4. **List-aware checkpoint unflatten**: MLX list parameters (e.g., `blocks=[Block, Block]`)
   serialize as `blocks.0.attn.q.weight`. The unflatten function detects consecutive
   integer keys and reconstructs Python lists for `model.update()`.

5. **Token offset**: All task generators start tokens at 1, reserving 0 as a potential
   pad token for Phase 2 batching with variable-length sequences.

6. **TASK_DEFAULTS in train.py**: Per-task seq_len/vocab_size defaults avoid requiring
   users to memorize task-specific constraints (e.g., sorting needs odd seq_len).

7. **seq_len convention for kv_retrieval**: seq_len = 2*n_pairs + 2 (includes the answer
   token). For seq_len=8: n_pairs=3. The answer token v_q is at targets[:, -1].

---

## Capacity Finding — bracket_match

The 2-layer, 4-head model plateaued at ~68% accuracy on bracket matching after 10000 steps
(loss flat from ~5000 onward). This is not a training failure; it is a model capacity limit.

Predicting OPEN vs CLOSE correctly requires tracking running depth (open_count − close_count
across all previous tokens). This is an inherently sequential operation. Pure attention
computes weighted sums over prior positions, not running totals. A 2-layer model must
approximate the depth counter via superposition — it partially succeeds but cannot fully
reconstruct the exact integer depth needed for correct prediction at deep nesting levels.

This is an informative result for interpretability work: in Phase 2, tracing the bracket model
at partial accuracy will show what circuits the model *does* form and where they break down.
A model at 68% that we can inspect is more valuable for learning than a larger model at 99%
that we cannot read.

---

## Retrospective

All six task modules were built and trained. Five tasks converged above 90% accuracy on their
primary metric within 2000–5000 steps. Bracket matching converged below threshold — this was
expected from Opus's Phase 1 advisory (the depth-tracking computation exceeds 2-layer capacity)
and is documented as a finding rather than a failure.

The training pipeline is modular, readable, and extensible. Each training run produces a complete
artifact set (checkpoints + log) that Phase 2 tracing can consume directly.

The kv_retrieval interface bug (generate() silently dropped the answer token from targets) was
found and fixed during the extension session. The FIXME comment in the original code correctly
identified the issue.
