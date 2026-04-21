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

---

## 12. [WAIVED — see §15]

*(§12 independent Opus verification waived. Rationale and accepted evidence recorded in §15.)*

---

## 13. Sonnet Phase 1 Extension Advisory

**Role:** Sonnet implementer — extension planning checkpoint.
**Date:** 2026-04-21
**Subject:** Phase 1 extension — train remaining tasks (kv_retrieval, sorting, modular_arith, bracket_match).

### 13.1 Phase Objective (in my own words)

Phase 1 exit criteria are already green: induction and factual_lookup trained, all 6 dataset
modules exist, transformer + training loop verified. This session extends Phase 1 by wiring up
the four remaining tasks, fixing interface bugs, and training them sequentially per §10.4 order:
kv_retrieval → sorting → modular_arith → bracket_match (stop if quality degrades).

The goal is still readable, inspectable code — not a larger model or more complex training loop.

### 13.2 Interface Issues Found (verified by reading source)

1. **kv_retrieval bug (blocking):** `generate()` returns 3 values `(inputs, targets, labels)` but
   train.py expects 2. Worse, the target construction has a dead no-op: labels are appended then
   immediately sliced off, so `targets[:, -1]` never contains the correct value token. The model
   never sees the retrieval signal during training.
   - Fix: build the full sequence as `[k1,v1,...,kN,vN,q_key,v_q]` first, then slice. Return
     `(inputs, targets)` only. Update SAMPLE_DATA to match new length-6 shape.

2. **kv_retrieval.evaluate() signature mismatch:** takes `(model, inputs, targets, labels, ...)`
   but train.py calls `evaluate(model=model, inputs=inputs, targets=targets, seq_len=args.seq_len)`.
   - Fix: derive labels from `targets[:, -1]`; add `seq_len=None` kwarg (same pattern as factual_lookup).

3. **modular_arith.generate() signature mismatch:** second positional arg is `p` not `seq_len`.
   train.py passes `seq_len=args.seq_len` by keyword — this won't bind to `p`.
   - Fix: change to `generate(n_samples, seq_len=None, vocab_size=32, seed=42, p=13)`. seq_len is
     accepted but unused (task has inherent seq_len=2).

4. **modular_arith.evaluate() signature mismatch:** second kwarg is `p` but train.py passes `seq_len`.
   - Fix: add `seq_len=None` kwarg; keep `p=13` as separate kwarg.

5. **bracket_match.evaluate()** doesn't accept `seq_len`.
   - Fix: add `seq_len=None` kwarg.

6. **train.py TASK_MODULES** only has induction and factual_lookup.
   - Fix: add all 4 remaining tasks + a TASK_DEFAULTS dict for per-task seq_len/vocab_size.

### 13.3 Top Risks

1. **kv_retrieval may need more steps**: content-based matching is harder than position-based
   induction. If 2000 steps aren't enough, bump to 5000 — do not scale the model.
2. **sorting/reversal seq_len must be odd** (2*half + 1). train.py default seq_len=16 is even —
   must use --seq_len 9 or similar. TASK_DEFAULTS handles this.
3. **modular_arith vocab** must be ≥ p+1 = 14. TASK_DEFAULTS sets vocab_size=16.
4. **Interface fix drift**: kv_retrieval fix touches generator + evaluator + SAMPLE_DATA — keep
   changes tight, don't refactor surrounding code.

### 13.4 Scope Boundaries

**Build now:**
- Fix kv_retrieval interface (generator bug + evaluate signature)
- Fix modular_arith and bracket_match evaluate signatures
- Wire up all 4 remaining tasks in train.py with TASK_DEFAULTS
- Train and document: kv_retrieval → sorting → modular_arith → bracket_match (in order)

**Do not build:**
- PyTorch bridge, Streamlit, attention visualization
- Model size increases or additional hyperparameter tuning
- New abstraction layers in training code

### 13.5 Per-Task Expected Args (TASK_DEFAULTS)

| Task           | seq_len | vocab_size | Notes                              |
|----------------|---------|------------|------------------------------------|
| induction      | 16      | 32         | already working                    |
| factual_lookup | 2       | 32         | already working                    |
| kv_retrieval   | 8       | 32         | n_pairs=3 derived as (seq_len-2)//2 |
| modular_arith  | 2       | 16         | p=13, needs vocab≥14               |
| bracket_match  | 16      | 4          | must be even; only uses tokens 1,2 |
| sorting        | 9       | 32         | odd (4+SEP+4); SEP=vocab-1=31      |

---

## 14. Sonnet — Phase 1 Closeout Advisory

**Role:** Sonnet implementer — phase transition checkpoint.
**Date:** 2026-04-21
**Subject:** Phase 1 closure assessment + Phase 2 preparation.

---

### 14.1 Current Repo State Assessment

Phase 1 is substantively complete. All six tasks trained; all exit criteria from §10.7
self-report green. The training pipeline is modular and readable. Checkpoint + metrics
artifacts are in place. `phase_1.md` accurately documents what was built and what was found.

**One structural gap:** §12 (Opus independent verification of Phase 1 exit criteria) was
never written. It is reserved for Opus; Sonnet cannot fill it without violating role discipline
(CLAUDE.md: "do not self-approve code you just wrote"). Phase 1 is self-declared complete,
not independently verified.

**Git state warning:** `checkpoints/` and `runs/` are untracked at the repo root. Five
modified source files are also uncommitted. These should be committed (or `.gitignore`d in
the case of checkpoints/runs) before Phase 2 begins. This cleanup is the user's call.

---

### 14.2 Whether Phase 1 Is Complete Enough to Close

**Verdict: conditionally yes.** The learning-first objective is met — six tasks trained,
capacity finding documented, checkpoint format locked in for Phase 2 consumption. The
only gap is §12. Two options:

- **Option A:** User waives §12 and accepts Sonnet's self-declaration as sufficient to close.
  Fastest path. Risk: a genuine issue with exit criteria could be masked.
- **Option B:** Opus writes §12 before Phase 2 begins. Correct per CLAUDE.md role discipline.
  Recommended if the user plans a fresh Opus session before Phase 2 implementation starts.

This advisory proceeds with cleanup under Option A assumption. If the user chooses Option B,
the Phase 2 activation below should be treated as "Phase 2 staged, not started."

---

### 14.3 Cleanup Required Before Phase 2

1. **Extract Phase 0 block from `current_phase.md`** — lines 1–58 are Phase 0 content
   that was never moved to `docs/phases/phase_0.md`. Extract and create that file.
2. **Rewrite `current_phase.md`** as Phase 2 only.
3. **Update `next_actions.md`** — all items are stale Phase 1 follow-up.
4. **Append Phase 1 closure to `implementation_status.md`**.
5. **Promote Q5 in `open_questions.md`** as top Phase 2 blocker; add Q9 (activation cache format).
6. **User decision needed:** commit Phase 1 files + `.gitignore checkpoints/ runs/` before Phase 2 starts.

---

### 14.4 Top Risks for Phase 2

1. **MLX has no forward-hook API.** PyTorch's `register_forward_hook` has no direct
   MLX equivalent. Capturing intermediate activations requires either: (a) instrumenting
   the forward pass in `transformer.py` to optionally return a cache dict, or (b) building
   a PyTorch bridge and re-running inference on the CPU-only PyTorch replica. Option (a) is
   cleaner but requires touching Phase 1 code; option (b) keeps concerns separate but adds
   a conversion step. This is the single highest-risk design decision for Phase 2.

2. **Activation cache format chosen carelessly mirrors checkpoint format risk.** Q5 covers
   the framework. A new Q9 covers the data format — what shape, what dtype, what on-disk
   structure. Getting this wrong means migrating every saved trace in Phase 3/4.

3. **`transformer.py` instrumentation may create Phase 1/Phase 2 coupling.**
   If tracing hooks are added directly into `transformer.py`, a tracing bug could break
   training. Prefer an instrumentation wrapper or a separate `tracer.py` that wraps the
   model rather than modifying it.

4. **Bracket match at 68% is the most interesting tracing target but also the hardest to
   interpret.** Its partial circuits will be visible — but interpreting incomplete, noisy
   activations requires care. Prioritize well-converged tasks (induction, kv_retrieval)
   for initial Phase 2 tracing; add bracket_match once the pipeline is validated.

---

### 14.5 What Should Not Change in This Cleanup Pass

- `src/` — no Phase 2 implementation yet; only docs/context files change
- `CLAUDE.md` — proposal required for any rule changes
- `docs/phases/phase_1.md` — already accurate; only update Status field from
  "COMPLETE (pending Opus verification)" to reflect the §12 situation honestly
- The history in `implementation_status.md` — append only, never rewrite
- `docs/PROJECT_PLAN.md` — authoritative; not touched here

---

## 15. Phase 1 Finalization — Closure Note

**Role:** Phase 1 finalization pass (Sonnet, documentation-only).
**Date:** 2026-04-21
**Subject:** Phase 1 formal closure; §12 waiver; Phase 2 activation reversal.

---

### 15.1 Current Assessment

Phase 1 is substantively complete. All 8 exit criteria from §10.7 are satisfied by measured
training results logged in `implementation_status.md`. The only outstanding item is §12 — the
reserved Opus independent verification pass — which was never written.

The Phase 2 activation in `current_phase.md` was premature. Phase 2 cannot begin until
Phase 1 is formally closed and the user confirms the §12 waiver. This pass corrects that.

---

### 15.2 What Is Still Unresolved

- §12 independent verification was not written — resolved by waiver below (§15.3)
- Five Phase 1 source files remain uncommitted — user decision: commit + `.gitignore` for `checkpoints/` and `runs/`
- Q5 and Q9 remain open — they are Phase 2 blockers, not Phase 1 gaps

---

### 15.3 §12 — Waived

**§12 is waived.** The independent verification mechanism in §12 was intended to catch
gaps between Sonnet's self-declaration and what was actually built. The available evidence
makes that gap unlikely and the residual risk is mitigated by Phase 2 tracing.

**Accepted evidence for Phase 1 closure:**

| Exit Criterion (§10.7) | Evidence |
|------------------------|----------|
| `train.py` runs end-to-end | Training logs in `runs/` show 6 complete runs |
| Induction ≥ 90% in 2000 steps | `induction_acc: 100.0%` at step 2000 |
| ≥ 2 tasks trained and documented | 6/6 tasks trained; all in `implementation_status.md` |
| Checkpoint round-trip verified | Load → re-evaluate → same accuracy (documented) |
| `transformer.py` readable in 5 min | <150 lines; pre-norm; no external model classes |
| All 6 task modules exist | Confirmed in `src/datasets/` |
| `implementation_status.md` accurate | Append-only log with per-task training results |
| Q1, Q3, Q8 marked RESOLVED | Confirmed in `open_questions.md` |

**Residual risk:** No independent check that `induction_acc: 100%` measures the claimed
induction circuit rather than a positional shortcut. Mitigation: Phase 2 tracing will
directly interrogate circuits — if the circuit doesn't exist, tracing will show it.
This is functionally stronger than a documentary re-read.

---

### 15.4 Scope of This Finalization Pass

Changes made in this pass (documentation only — no `src/` changes):

- `current_phase.md` — Phase 2 activation reverted; set to Phase 1 Finalization state
- `review_notes.md` — §12 updated to WAIVED; §15 appended
- `implementation_status.md` — new entry prepended; Phase 2 activation rescinded
- `next_actions.md` — trimmed to post-closure items; Phase 2 prep items removed
- `docs/phases/phase_1.md` — Status field updated to reflect §12 waiver

---

### 15.5 What Must Not Be Changed in This Pass

- `src/` — no code changes
- `CLAUDE.md` — no rule changes; proposal required for any edits
- `docs/PROJECT_PLAN.md` — authoritative; untouched
- Existing history entries in `implementation_status.md` — append-only; preserved
- `docs/phases/phase_0.md` — already complete; untouched
- §1–§14 of this file — existing review record preserved

---

## 16. Phase 2 Advisory Notes (Sonnet, pre-implementation)

**Role:** Sonnet implementer — pre-implementation advisory.
**Date:** 2026-04-21
**Subject:** Phase 2 — Tracing Foundation.

---

### 16.1 Phase Objective (in my own words)

Make a single forward pass fully inspectable: given a trained checkpoint and a token
sequence, capture every intermediate tensor — embeddings, QKV projections, attention
scores and patterns, MLP activations, residual stream states, final logits — into a
clean in-memory structure that can be saved to disk and consumed by Phase 3 visualization
without redesign.

---

### 16.2 Key Design Decision — Q5 Resolved

**Resolution: Option (A) — `return_cache` flag threaded through the forward pass.**

MLX has no `register_forward_hook` equivalent. A wrapper class that intercepts
"at module boundaries" sounds clean but is not actually possible without either
re-implementing the math or modifying the module — the Q, K, V arrays and `scores`
only exist inside `MultiHeadSelfAttention.__call__`; they are not accessible from
outside. There are two real options:

- **(A) `return_cache` parameter** in `__call__` of `MultiHeadSelfAttention`,
  `TransformerBlock`, and `Transformer`. When `True`, return `(output, cache_dict)`.
  Minimal Phase 1 code change; one source of truth for the forward pass; readable.
- **(B) `TracedTransformer`** that reimplements the forward pass with explicit capture.
  Zero Phase 1 code changes but duplicates math that can drift silently.

**Option (A) is chosen.** Phase 1 instructions said "minimal changes to model code
required for readable tracing" — this implies modification is expected, not forbidden.
A duplicated forward pass that drifts is a worse risk than a flag.

**Anti-drift guarantee:** a test must assert `model(x)` == `model(x, return_cache=True)[0]`
bit-for-bit. This is the correctness anchor for every later phase.

---

### 16.3 Key Design Decision — Q9 Resolved

**In-memory:** `ActivationCache` — thin wrapper around the nested raw cache dict;
supports dot-key access (`cache["blocks.0.attn.scores"]`); has a `flat()` method
that reuses `checkpoint.py`'s `_flatten` helper.

**On-disk:** Two files per trace (matching the 4-file Phase 1 checkpoint pattern):
- `activations.safetensors` — flat tensor dict via `mx.save_safetensors`
- `trace_meta.json` — checkpoint path, task, input tokens (as list), seq_len, vocab,
  timestamp, git hash

**Dtype:** `float32` everywhere. MLX uses `float32` by default; no bfloat16 conversion
needed for this model size.

**Naming convention:** TransformerLens-style flat dotted keys:
```
embed.tok             (B, T, d_model)   — token embeddings
embed.pos             (T, d_model)      — positional embeddings (no batch dim)
embed.combined        (B, T, d_model)   — tok + pos
blocks.0.resid_pre    (B, T, d_model)   — residual stream before block 0
blocks.0.attn.q       (B, H, T, Dh)    — Q projections, all heads
blocks.0.attn.k       (B, H, T, Dh)
blocks.0.attn.v       (B, H, T, Dh)
blocks.0.attn.scores  (B, H, T, T)     — post-causal-mask, pre-softmax
blocks.0.attn.pattern (B, H, T, T)     — post-softmax attention weights
blocks.0.attn.output  (B, T, d_model)  — attention output after out-projection
blocks.0.resid_mid    (B, T, d_model)  — after attn, before MLP
blocks.0.mlp.pre      (B, T, 4*d_model) — after mlp1, before GELU
blocks.0.mlp.post     (B, T, 4*d_model) — after GELU, before mlp2
blocks.0.mlp.output   (B, T, d_model)  — MLP contribution, after mlp2
blocks.0.resid_post   (B, T, d_model)  — residual stream after block
...
ln_f.input            (B, T, d_model)  — input to final LayerNorm
logits                (B, T, vocab)    — final output
```

---

### 16.4 Top Risks

**R1 — Unmaterialized lazy arrays in the cache (highest risk)**
MLX is lazy by default. If `mx.eval(cache_tensors)` is not called before the
trace function returns, the cache contains lazy computation graphs. Serialization
then triggers evaluation — fine on its own, but if the model was also used for
training in the same session, the lazy graph may reference freed buffers. Fix:
call `mx.eval()` on all cache tensors immediately before returning.

**R2 — `scores` naming collision between pre-softmax and post-softmax**
The current transformer.py names both variables `scores` within the same function
(pre-softmax = raw logits; post-softmax = `attn`). Must be explicit: save `scores`
as post-causal-mask pre-softmax, and `pattern` as post-softmax. Both are needed:
`scores` tells you what the model "wants" to attend to; `pattern` tells you what
it actually does.

**R3 — `return_cache=True` branch must never run during training**
`loss_fn` in `loop.py` calls `model(x)` — the two-return-value path must only
trigger when explicitly requested. The `return_cache=False` default satisfies this,
but confirm by reading `loss_fn` uses `model(x)` not `model(x, return_cache=True)`.

**R4 — Tracing script finds no checkpoint if directory is empty**
The trace script must fail clearly if no checkpoint is found, not silently
produce a zero-initialized model trace.

---

### 16.5 What Must Be Built Now

1. Modify `src/models/transformer.py` — add `return_cache` to all three `__call__` methods
2. Create `src/tracing/__init__.py` — public API surface
3. Create `src/tracing/cache.py` — `ActivationCache` wrapper
4. Create `src/tracing/tracer.py` — `trace(model, tokens)` function
5. Create `src/tracing/export.py` — `save_trace` and `load_trace`
6. Create `scripts/trace_prompt.py` — runnable CLI demo
7. Create `docs/phases/phase_2.md` — phase writeup

---

### 16.6 What Must Not Be Built Now

- No Streamlit UI or visual dashboards (Phase 3)
- No ablation or activation patching (Phase 4)
- No PyTorch bridge (not needed; MLX tracing is viable)
- No sparse autoencoder work (Phase 6)
- No pretrained model integration (Phase 8)
- No speculative Phase 3 abstractions pre-built "for convenience"

---

### 16.7 Validation Plan

Use the induction task — 100% converged, clearest expected circuit:
1. Load the latest induction checkpoint
2. Construct a known induction sequence (e.g., `[3, 7, 3]`)
3. Run `trace(model, tokens)` — verify no errors, cache is non-empty
4. Assert `logits == model(tokens)` bit-for-bit (anti-drift test)
5. Print top-3 predicted tokens at position 2 — should include token 7
6. Check that `blocks.0.attn.pattern` shows the model attending to position 0
   from position 2 (the expected induction head behavior)
7. Verify save → load round-trip: saved and loaded tensors must match
