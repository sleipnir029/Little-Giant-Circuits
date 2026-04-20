# Phase 0 — Opus Review Notes

**Reviewer role:** advisor / architecture critic (not implementer).
**Review type:** Post-implementation independent verification.
**Date:** 2026-04-21
**Subject:** Phase 0 — Foundation and constraints (per `docs/PROJECT_PLAN.md §6`).

This document supersedes the earlier pre-implementation critique and the §10 verification pass.
It is a single, fresh independent read of the completed Phase 0 work.

---

## 1. Phase Objective (Reference)

Phase 0 exists to install the rules of the game before any model code is written. Its single
job is to make Phase 1 safe to start:

- a repo skeleton that matches the plan's intent,
- a documentation backbone that captures what is in scope and how drift is prevented,
- a working `CLAUDE.md` that reinforces the learning-first principles,
- the file-based context workflow (`docs/phase_context/`) actually in place and usable,
- an environment doc a reader can follow on an M1 Mac without guessing.

No user-runnable code ships in Phase 0.

---

## 2. Exit Criteria Verification

Independent check against the 12-item checklist in `current_phase.md`.
Files read directly — did not trust the self-reported implementation log.

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Five phase_context/*.md files exist and are non-empty | PASS |
| 2 | docs/proposals/ with README and .gitkeep | PASS |
| 3 | LICENSE present and unmodified Apache-2.0 | PASS |
| 4 | docs/ENVIRONMENT.md — Apple-Silicon scope, PM deferred | PASS |
| 5 | docs/WORKFLOW.md — operational Opus↔Sonnet description | PASS |
| 6 | docs/architecture, theory, phases/README.md each exist | PASS |
| 7 | No file under src/ | PASS |
| 8 | No dependency manifest at repo root | PASS |
| 9 | No Streamlit app file | PASS |
| 10 | README repo-tree root says `little-giant-circuits/` | PASS |
| 11 | git status clean; Phase 0 changes committed | PASS |
| 12 | Fresh reader can state Phase 1 scope from CLAUDE.md + current_phase.md | PASS |

All 12 PASS.

---

## 3. Content Quality Assessment

### docs/ENVIRONMENT.md
States Apple Silicon as a deliberate design constraint, not a limitation or oversight.
Package-manager decision explicitly deferred to Phase 1 with a pointer to open_questions.md Q1.
Python 3.11 recommended with reasoning; not yet enforced. Under 55 lines. Correct framing throughout.

### docs/WORKFLOW.md
Operational, not philosophical. Covers: who writes which file, the five-step Opus→Sonnet→Opus
cycle, governance rules for each file (append-only, RESOLVED not deleted, etc.), and a concrete
list of what breaks the workflow. Under 95 lines. Closes R5 from the pre-implementation review.

### docs/phase_context/open_questions.md
Eight questions seeded. Q7 (repo-name consistency) resolved with audit trail intact.
Seven remain OPEN, each with a "blocks which phase" annotation:
- Q1, Q3, Q8 block Phase 1 — must be answered before Phase 1 kickoff
- Q2, Q5 block Phase 2
- Q4 blocks Phase 5
- Q6 informs Phase 3 design (not a hard blocker)

### docs/phase_context/implementation_status.md
Append-only. Two dated entries. No retroactive editing. Decisions captured alongside
what was built. Open risks carried forward explicitly. Format is correct.

### docs/proposals/README.md
Operationalizes the CLAUDE.md proposal mechanism. The update pathway is now real
infrastructure, not just a referenced rule. Closes R4 from the pre-implementation review.

### docs/phases/TEMPLATE.md and docs/phases/phase_1.md
Both added beyond the original §3 scope. TEMPLATE.md is a net positive — a
reusable structure prevents future phases from inventing their own format.
phase_1.md correctly lists prerequisites (Q1, Q3, Q8, Opus review) before any
Phase 1 content is filled in. Neither introduces drift.

---

## 4. Drift Check

No silent additions found. Specifically verified absent:
- No `.github/` workflows
- No `.pre-commit-config.yaml`, `.ruff.toml`, `pyrightconfig.json`, `.python-version`
- No `src/` directory or anticipatory `.gitkeep` under future source paths
- No `notebooks/`, `experiments/`, `data/`, `checkpoints/`, `app/` directories
- No `pyproject.toml`, `requirements*.txt`, `setup.py`, `uv.lock`, `poetry.lock`, `environment.yml`
- No Python files anywhere in the repo

Repo root contents: `.git/`, `.gitignore`, `CLAUDE.md`, `LICENSE`, `README.md`, `docs/`. Correct.

---

## 5. Issues Found

### Issue 1 — README repo-tree is stale (non-blocking)

The README repo-tree was fixed for the root name (`glassbox-playground/` → `little-giant-circuits/`)
but was not updated to reflect what Phase 0 actually added to `docs/`.

**In README but doesn't exist:**
- `docs/CLAUDE_BOOTSTRAP.md` — listed in README, file never created

**Exists but missing from README:**
- `docs/WORKFLOW.md` — created in Phase 0
- `docs/ENVIRONMENT.md` — created in Phase 0
- `docs/proposals/` — created in Phase 0

This inconsistency was missed in the earlier verification pass because criterion #10 asked
only about the root name, not file-level accuracy of the tree.

**Fix:** Update the README repo-tree block to reflect the actual `docs/` structure.
Either create a minimal `docs/CLAUDE_BOOTSTRAP.md` or remove the reference;
`docs/WORKFLOW.md` appears to serve that role.

This is a single-file correction. It does not require a proposal.

---

## 6. Non-Blocking Observations

Captured for Phase 1 reference; none block Phase 0 closure.

1. **Proposal enforcement is documentary, not mechanical.** A contributor could still edit
   `CLAUDE.md` without creating a proposal file. Consider a pre-commit check in Phase 1
   (ties to Q8 tooling decision).

2. **next_actions.md item 2 does not name an actor.** "Answer Q1, Q2, Q3, Q8 with Opus"
   implies a human-triggered planning session. Making the trigger explicit reduces ambiguity.

3. **Q8 (Phase 0.5) remains open.** The Phase 1 kickoff conversation should resolve this
   before any Phase 1 implementation begins. A three-commit Phase 1 opener that sets up
   ruff + pyright + a smoke-test GitHub Action is low overhead and prevents undisciplined
   precedents in the first real Python.

---

## 7. Phase 1 Prerequisites

Before any Phase 1 implementation (no src/, no dependency manifest, no model code):

1. Resolve Q1 (package manager), Q3 (Python floor), Q8 (Phase 0.5 tooling)
2. Resolve or note Q2 (PyTorch device) — Phase 2 blocker, document even if answer is "TBD"
3. Fix README repo-tree (Issue 1 above)
4. Opus reads PROJECT_PLAN.md §6 Phase 1 and writes Phase 1 advisory notes into this file
5. Update current_phase.md to reflect Phase 1 as active

---

## 8. Recommendation

**Ready for Phase 1 with minor fixes.**

Phase 0 foundation is solid: the file-based context workflow is operational, drift was
actively prevented, documentation is concise and purposeful, and the learning-first
principles were not violated at any point.

The README repo-tree inconsistency (Issue 1) is the only genuine gap. It is a one-file
correction and does not require a proposal. Fix it before the first Phase 1 commit.

---

## 9. Phase 1 Advisory Notes

*(Superseded by §10 below — written when the human opened the Phase 1 planning session.)*

---

## 10. Phase 1 Advisory Notes (Opus)

**Reviewer role:** advisor / architecture critic (not implementer).
**Review type:** Pre-implementation phase advisory.
**Date:** 2026-04-21
**Subject:** Phase 1 — Tiny Transformer Training.

---

### 10.1 Phase Objective

Build a minimal, inspectable training system for six synthetic toy tasks. The goal is
not a capable model — it is a transparent one. Every architectural choice should favor
readability over performance, and every training artifact should be usable in Phase 2
without format migration.

---

### 10.2 Open Question Resolutions (Q1, Q2, Q3, Q8)

**Q1 — Package manager: pip + venv**
Lowest magic, easiest to document for learners, no lockfile format bets.
A single `requirements.txt` with pinned versions is enough for Phase 1.
Revisit with `uv` if install times become painful in Phase 3+.

**Q2 — PyTorch device target: CPU-only for Phase 2 bridge**
MPS support in PyTorch is real but has silent op fallbacks. For Phase 2
interpretability tooling, CPU-only is safer and avoids debugging MPS-specific tensor
layout issues. Revisit if Phase 4 intervention speed is unacceptable.

**Q3 — Python version floor: 3.11**
Conservative, safe for current mlx-lm versions. Do not chase 3.12 until an mlx
release explicitly confirms compatibility.

**Q8 — Tooling: Phase 1 opener, not a separate phase**
First two commits of Phase 1 set up ruff + pyright (strict: false, basic type coverage).
No CI in Phase 1 — a GitHub Actions smoke test is Phase 2 scope. This prevents
undisciplined first-Python without adding phase overhead.

---

### 10.3 Key Risks

**R1 — Architecture too large to inspect (highest risk)**
A 4-layer, 256-dim transformer trained on toy tasks is not inspectable — it's just
competent. The architecture must be constrained by design, not by accident.
Hard limits: ≤2 layers, ≤4 heads, d_model ≤ 64, sequence length ≤ 32, vocab ≤ 64 tokens.
If a task requires more capacity to learn, the task generator is wrong, not the model limit.

**R2 — Checkpoint format chosen carelessly**
Phase 5 (checkpoint evolution) and Phase 8 (pretrained bridge) depend on the format
chosen here. Migrating 50 saved checkpoints mid-project is expensive.
Use MLX's native `.safetensors` output and save model config (as JSON) alongside every
checkpoint. This is already HuggingFace-compatible and avoids a migration layer.

**R3 — Metrics that don't serve interpretability**
Training loss alone tells you nothing useful for Phase 2–5 analysis. Minimum required
metrics per checkpoint: loss, per-token accuracy, step number. Preferred: also log
which token positions the model gets right/wrong (for sequence tasks), as this is the
first signal of circuit formation.

**R4 — Premature framework mixing**
MLX for training; PyTorch is Phase 2 only. Do not import torch anywhere in Phase 1.
The bridge is built in Phase 2 after training is stable. Mixing them in Phase 1 creates
a dependency tangle before the training loop is even verified.

**R5 — Generators too complex**
If the data generator is complex, it obscures what the model is actually learning.
Each generator must be readable in under 30 lines. If it isn't, it's doing too much.

**R6 — Training loop monolith**
A single 400-line train.py that hardcodes everything is unreadable and untestable.
Separate: model definition, dataset/generator, training loop, config, checkpoint I/O.
Each file should be understandable in under 5 minutes.

---

### 10.4 Recommended Task Order

Start with induction, verify training, then add tasks one at a time.

1. **Induction/copying** — purest possible task (A B A → B), known to develop induction
   heads. Best first task: clean verification, fast to train, interpretable from step 1.
2. **Key-value retrieval** — tests lookup/association; well-studied in mechanistic
   interpretability literature; useful for Phase 2 circuit tracing.
3. **Modular arithmetic** — algorithmic transformation; known to develop interesting
   Fourier-like representations; expect longer training to converge.
4. **Bracket matching** — introduces structured dependency; requires tracking "open" state;
   harder to verify without position-level accuracy metrics.
5. **Sorting / reversal** — position-sensitive; requires cross-token comparison; most
   complex internal structure of the six.
6. **Simple factual lookup** — symbolic association; largely overlaps with key-value;
   implement last because the distinction from task 2 is subtle.

Do not run all six simultaneously in Phase 1. Train them sequentially, confirm each
reaches >90% accuracy before proceeding, and document what you observe.

---

### 10.5 Implementation Guidance for Sonnet

**Architecture constraints (enforce these in code, not just docs):**
```python
# In model config — these are ceilings, not defaults
MAX_LAYERS = 2
MAX_HEADS = 4
MAX_D_MODEL = 64
MAX_SEQ_LEN = 32
MAX_VOCAB = 64
```

**File structure (create exactly these, nothing more in Phase 1):**
```
src/
  models/
    transformer.py      # <150 lines; one class; no subclasses yet
  training/
    train.py            # main entry point: python train.py --task induction
    loop.py             # training step, optimizer, loss computation
  datasets/
    induction.py        # generator + evaluator for induction task
    kv_retrieval.py     # one file per task
    modular_arith.py
    bracket_match.py
    factual_lookup.py
    sorting.py
  utils/
    config.py           # dataclass for all hyperparameters
    checkpoint.py       # save/load; weights + config + step + metrics as one unit
```

**Checkpoint format (implement exactly this):**
Every checkpoint directory saves four files:
- `weights.safetensors` — MLX model weights
- `config.json` — full model config + training config
- `metrics.json` — loss, accuracy, step at save time
- `meta.json` — task name, timestamp, git hash

Directory naming: `checkpoints/{task}/{step:07d}/`

**Training loop requirements:**
- Configurable via command-line args (task, d_model, n_layers, n_heads, lr, steps)
- Checkpoint every 100 steps by default; configurable
- Print loss + accuracy every 10 steps; no external logging framework yet
- A run that hits >95% accuracy on induction within 2000 steps validates the stack

**Tokenizer:**
Do not use a real tokenizer. Each task defines its own integer vocabulary directly.
Vocabulary size is a config parameter, not discovered at runtime.

---

### 10.6 Documentation Requirements

Each task module must include:
- A module-level docstring: what the task tests, expected model behavior,
  what circuit is expected to form, and the evaluation metric.
- A `generate(n_samples, seq_len, vocab_size, seed)` function.
- An `evaluate(model, dataset)` function returning accuracy (float 0–1).
- A `SAMPLE_DATA` constant showing 3–5 example input/output pairs.

Each training run must produce:
- A `runs/{task}/{timestamp}/` directory with checkpoint subdirs.
- A `train_log.txt` with step-by-step loss and accuracy.

Update `docs/phases/phase_1.md` as items are built (not speculatively).
Append to `implementation_status.md` after each significant commit.

---

### 10.7 Validation Criteria (Phase 1 exit gate)

All must be true before Phase 2 begins:

- [ ] `python train.py --task induction` runs end-to-end without error
- [ ] Induction model reaches >90% accuracy within 2000 steps
- [ ] At least two tasks trained and documented (induction + one more)
- [ ] Checkpoint loading verified: load checkpoint, rerun evaluation, same accuracy
- [ ] A human unfamiliar with the codebase can read `transformer.py` and explain
      the forward pass in under 5 minutes
- [ ] All six task modules exist (generators + evaluators), even if not all trained
- [ ] `implementation_status.md` reflects what was actually built
- [ ] `open_questions.md` Q1, Q3, Q8 marked RESOLVED

---

### 10.8 What Not To Do In Phase 1

- Do not implement PyTorch bridge (Phase 2)
- Do not build Streamlit app (Phase 3)
- Do not add attention visualization (Phase 2/3)
- Do not use a pretrained embedding or real tokenizer
- Do not train models larger than the architecture ceiling
- Do not add weight decay, dropout, or lr scheduling in Phase 1 — they add noise
  to the training signal at tiny scale before the loop is even verified
- Do not train all 6 tasks before task 1 is verified
- Do not use mlx-lm model classes — the model must be written from scratch;
  inspectability requires knowing every line of the forward pass
- Do not add a web interface, REST API, or any serving infrastructure
- Do not write a Jupyter notebook as the primary artifact — scripts are the deliverable

---

## 11. Sonnet Phase 1 Pre-Implementation Advisory

**Role:** Sonnet implementer pre-flight check.
**Date:** 2026-04-21
**Subject:** Phase 1 — Tiny Transformer Training (pre-coding checkpoint).

### 11.1 Phase Objective (in my own words)
Build the smallest possible working training system for toy tasks. The goal is a codebase a motivated learner can read in 20 minutes and fully understand — not a system that trains fast or scales. Every file should explain itself.

### 11.2 Environment Facts (verified before writing code)
- Python 3.12.9 (Python 3.11 not installed; MLX 0.31.1 supports 3.12 — Q3 effectively updated)
- MLX 0.31.1 available via pip; `mx.save_safetensors`, `nn.value_and_grad`, `mx.load` all confirmed present
- `model.parameters()` returns a nested dict — requires flatten-to-dot-notation before `mx.save_safetensors`
- Training pattern: `nn.value_and_grad(model, loss_fn)` → `optimizer.update(model, grads)` → `mx.eval(model.parameters(), loss)`
- Causal mask: `mx.where(mx.tril(mx.ones((T,T))), 0.0, float("-inf"))` adds to scores — confirmed working

### 11.3 Top Risks
1. **MLX mutability**: MLX arrays are lazy/functional; `mx.eval()` must be called after each training step or gradients are not materialized. Easy to silently skip.
2. **Nested parameter dict**: `model.parameters()` nests by module name — must flatten for `save_safetensors`, must un-flatten for `model.update()`.
3. **Causal mask shape broadcast**: mask is (T, T), scores are (B, H, T, T) — MLX broadcasts correctly but the subtlety is easy to get wrong during debugging.
4. **Task generator complexity creeping up**: generators must stay under 30 lines each per R5.

### 11.4 Scope Boundaries
**Build now:** tooling setup, transformer.py, config.py, checkpoint.py, all 6 dataset modules (generator + evaluator), training loop, train.py entry point, README fix.
**Do not build:** PyTorch bridge, Streamlit, attention visualization, anything requiring `torch`.

### 11.5 Questions Worth Tracking
- Q3 update: Python 3.12 is the actual runtime (3.11 not installed). `pyproject.toml` will say `requires-python = ">=3.11"` (3.12 satisfies this). Update Q3 in open_questions.md.
- Checkpoint path: Opus spec says `checkpoints/{task}/{step:07d}/` at repo root. Run logs go in `runs/{task}/{timestamp}/`. These will be separate top-level directories.
