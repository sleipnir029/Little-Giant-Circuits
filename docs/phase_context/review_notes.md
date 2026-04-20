# Phase 0 — Opus Review Notes

**Reviewer role:** advisor / architecture critic (not implementer).
**Date:** 2026-04-21
**Subject:** Phase 0 — Foundation and constraints (per `docs/PROJECT_PLAN.md §6`).
**Status at review time:** `CLAUDE.md` drafted, `PROJECT_PLAN.md` drafted, `README.md` drafted, no `src/`, no `docs/phase_context/` files, no `docs/proposals/`, no LICENSE file, no environment docs, no dependency manifest.

---

## 1. Phase Objective

Phase 0 exists to install the **rules of the game** before any model code is written. Its single job is to make Phase 1 safe to start:

- a repo skeleton that matches the plan's intent (not every directory in the README yet),
- a documentation backbone that captures *what is in scope* and *how drift is prevented*,
- a working `CLAUDE.md` that reinforces the learning-first principles,
- the **file-based context workflow** (`docs/phase_context/`) actually in place and usable,
- an environment doc that a reader can follow on an M1 Mac without guessing.

Phase 0 is **not** a feature phase. Nothing a user runs ships in Phase 0. The deliverable is a repository that a new contributor (or a future model session) can walk into cold and understand the constraints within 10 minutes of reading.

---

## 2. Risks

Ordered by likelihood × impact on the project's stated purpose.

### R1 — Scaffolding drift (high)
The strongest temptation in Phase 0 is to "helpfully" scaffold `src/models/`, `src/training/`, `src/tracing/`, etc. with `__init__.py` and placeholder classes because the README lists them. This is exactly the silent scope expansion CLAUDE.md §"Role Discipline" forbids. Empty directories with placeholders *look* productive but commit the project to a layout before we have learned anything from Phase 1.

### R2 — Premature dependency lock-in (high)
Writing a `pyproject.toml` / `requirements.txt` that pins MLX + PyTorch + Streamlit + SAE libs in Phase 0 encodes decisions that should be made when the first real import happens. Worse, it invites installing them and then not using them, which is the "generic LLM engineering repo" failure mode Principle A warns against.

### R3 — Documentation inflation (medium-high)
Phase 0 rewards writing documents. That reward is misleading. Ten more pages of philosophy do not make Phase 1 any easier; they make the context window expensive and increase the chance that `CLAUDE.md`, `PROJECT_PLAN.md`, and `README.md` quietly contradict each other. The PROJECT_PLAN already contains the principles; do not re-derive them.

### R4 — Missing update-proposal infrastructure (medium)
`CLAUDE.md` mandates `docs/proposals/claude_update_<date>.md` as the only legal way to change rules, but no `docs/proposals/` directory exists. The mechanism is referenced but not yet real — a contributor following the rule today has nowhere to put the file. This will silently be violated the first time a change is attempted.

### R5 — MLX / Apple-Silicon bus factor (medium)
The stack is explicitly M1-first. Anyone on Linux/Windows cannot even install MLX. Phase 0 is the right time to *state* this, not fix it. The risk is that without a clear "this project is Apple Silicon, by design" statement in env docs, future contributors or future-you will rationalize PyTorch-everywhere changes.

### R6 — `current_phase.md` drift from reality (medium)
If `current_phase.md` is written once and never updated, the workflow degrades into the chat-memory pattern it was meant to replace. This is a workflow-hygiene risk, not a Phase 0 content risk — but Phase 0 is when the habit is formed.

### R7 — "Phase 0 done" has no concrete criterion (medium)
The PROJECT_PLAN lists Phase 0 deliverables but no acceptance gate. Without one, Phase 0 will end when someone feels tired, not when the foundation is actually adequate. See §6 below for a proposed checklist.

### R8 — README repo-name inconsistency (low, but cosmetic drift signal)
`README.md` shows repo root as `glassbox-playground/` while the project is named `little-giant-circuits`. Small, but it is exactly the kind of unchecked inconsistency that snowballs.

---

## 3. Recommended Scope Boundaries

### In scope for Phase 0

1. **Create `docs/phase_context/` with all five files populated**, even if minimally:
   - `current_phase.md` — declares Phase 0 active, lists exit criteria.
   - `review_notes.md` — this file.
   - `implementation_status.md` — append-only log; starts empty with a header.
   - `open_questions.md` — seeded with the questions in §8 below.
   - `next_actions.md` — the concrete next-step list for Sonnet.
2. **Create `docs/proposals/` directory** with a `.gitkeep` and a one-paragraph `README.md` explaining the proposal workflow already defined in `CLAUDE.md` §"Updating This File". This closes R4.
3. **Add `LICENSE` (Apache-2.0)** per PROJECT_PLAN §4. This is a one-file change with no drift risk.
4. **Add `docs/ENVIRONMENT.md`** stating:
   - Target hardware: Apple Silicon (M1 Air baseline).
   - Python version expectation (recommend 3.11, justify briefly).
   - Package-manager choice is **deferred to Phase 1** — do not decide now.
   - Non-Apple-Silicon users: explicitly out of scope for now.
5. **Add `docs/WORKFLOW.md`** (or fold into CLAUDE_BOOTSTRAP.md if preferred) describing the Opus↔Sonnet phase_context loop in operational terms — "how you actually use these five files day-to-day". Keep under ~60 lines.
6. **Fix the README repo-root-name inconsistency** (R8) — small correction, no proposal needed per CLAUDE.md.
7. **Commit a stub `docs/architecture/`, `docs/theory/`, `docs/phases/`** each with a one-line `README.md` stating what belongs there. These are referenced by README.md so they should exist; keeping them empty prevents R3.

### Out of scope for Phase 0 (do not do)

- Any file under `src/`. No `__init__.py`, no stub module, no type stubs.
- Any dataset generator, even a toy one.
- Any `pyproject.toml`, `requirements.txt`, `uv.lock`, `poetry.lock`, or dependency install.
- Any Streamlit app stub (even `streamlit_app.py` with a placeholder `st.title`).
- Any model code in any framework.
- Any CI configuration, pre-commit hooks, or linting setup. These are worth adding — but they belong in a Phase 0.5 proposal or Phase 1 opener, not silent additions now.
- Any changes to `PROJECT_PLAN.md` content. Structural cleanup (e.g. the stray leading `---` and backtick-fence artifacts at the top of the file) is allowed; semantic changes require a proposal.
- Any rewrite of `CLAUDE.md`. It already reflects the plan. Leave it.

---

## 4. Implementation Guidance for Sonnet

Concrete ordering. Do these in sequence; each step is small.

1. **Create `docs/phase_context/current_phase.md`.** Contents: one-line "Phase 0 — Foundation active", followed by a short list of Phase 0 exit criteria (copy from §6 of this file). End with "Next phase: Phase 1 — Tiny transformer training (not yet started)."
2. **Create `docs/phase_context/implementation_status.md`.** Contents: a single header and an empty append log. Each future entry is a dated bullet: what was built, where, which plan section it satisfies. Do not retroactively log things that were already committed before this file existed — start from now.
3. **Create `docs/phase_context/open_questions.md`.** Seed with the items in §8 below. Format: numbered questions with a one-line "why it matters" each. Mark each as OPEN.
4. **Create `docs/phase_context/next_actions.md`.** Contents: a short ordered list of the very next commits to make, bounded to Phase 0 scope. Remove items as they are completed.
5. **Create `docs/proposals/` with `.gitkeep` and a short `README.md`.** The README restates, in ~10 lines, the proposal workflow from `CLAUDE.md` §"Updating This File (Proposal Mode)". Do not re-derive the rule — cite it.
6. **Create `LICENSE`** — standard Apache-2.0 text, copyright holder matching the git user. This is a single known-good file; do not paraphrase the license.
7. **Create `docs/ENVIRONMENT.md`.** Short. State: Apple Silicon target, Python 3.11 recommendation (or justify another choice), package-manager decision deferred to Phase 1, and that non-Apple-Silicon is out of scope.
8. **Create `docs/WORKFLOW.md`.** Describe how the five `phase_context/` files are used across an Opus→Sonnet→Opus cycle. Keep operational, not philosophical. Cite `PROJECT_PLAN.md §9` rather than restating it.
9. **Create stub `README.md` files** inside `docs/architecture/`, `docs/theory/`, `docs/phases/` — one sentence each, saying what content belongs there. Directories already referenced by root README; make them real and empty.
10. **Fix the `glassbox-playground/` → `little-giant-circuits/` inconsistency** in `README.md` repo-tree block.
11. **Update `docs/phase_context/implementation_status.md`** with a single dated entry summarizing what was done. This closes the loop.

Each of these steps is independently reversible and keeps the diff small. No step requires running any code.

**Anti-guidance:** If at any step Sonnet finds itself writing Python, editing `CLAUDE.md`, or creating a file under `src/`, stop. That is a Phase 1 action and needs to wait.

---

## 5. Documentation Requirements

By end of Phase 0, the following must hold:

- `LICENSE` exists and is Apache-2.0.
- `CLAUDE.md` is unchanged from its current form (or changed only via a landed proposal).
- `PROJECT_PLAN.md` is unchanged semantically (minor top-of-file cleanup allowed).
- All five `docs/phase_context/*.md` files exist and contain at minimum:
  - `current_phase.md`: active phase + exit criteria,
  - `review_notes.md`: this file,
  - `implementation_status.md`: at least one dated entry,
  - `open_questions.md`: at least the seed questions from §8,
  - `next_actions.md`: current list (may be empty once Phase 0 is done, and at that point it should list "start Phase 1 planning" or equivalent).
- `docs/proposals/` exists with its README.
- `docs/ENVIRONMENT.md` and `docs/WORKFLOW.md` exist and are each under ~80 lines.
- `docs/architecture/`, `docs/theory/`, `docs/phases/` each contain a one-line `README.md`.
- `README.md`'s repo-tree block is internally consistent with the project name.

Deliberately **not required** in Phase 0: any dependency manifest, any CI config, any source file, any diagram.

---

## 6. Validation Criteria (Phase 0 "Done" Checklist)

Phase 0 is complete when **all** of the following are true. This is the gate closing R7.

- [ ] All five `docs/phase_context/*.md` files exist and are non-empty.
- [ ] `docs/proposals/` exists with README and `.gitkeep`.
- [ ] `LICENSE` file present and is unmodified Apache-2.0.
- [ ] `docs/ENVIRONMENT.md` present; declares Apple-Silicon scope; defers package-manager choice.
- [ ] `docs/WORKFLOW.md` present; describes the Opus↔Sonnet file-based loop in operational terms.
- [ ] `docs/architecture/README.md`, `docs/theory/README.md`, `docs/phases/README.md` each exist with a one-line purpose statement.
- [ ] No file exists under `src/`.
- [ ] No dependency manifest exists at the repo root.
- [ ] No Streamlit app file exists.
- [ ] Repo-tree in `README.md` matches the actual repository name.
- [ ] `git status` is clean; all Phase 0 changes are committed.
- [ ] A fresh reader of `CLAUDE.md` + `docs/phase_context/current_phase.md` can state in one paragraph what Phase 1 will and will not do.

No automated test suite is needed to validate Phase 0 — the checklist is the test. Running `ls` and reading five files is the validation.

An independent Opus review pass after implementation should confirm these items and check for silent additions (especially any `src/` files, any hidden `requirements.txt`, any new dependencies).

---

## 7. What Not to Do in This Phase

Hard "no" list. If an action matches any of these, it is out of scope for Phase 0.

- Do **not** create `src/` or any subdirectory under it.
- Do **not** write any `.py` file anywhere in the repo.
- Do **not** introduce any dependency manifest (`pyproject.toml`, `requirements*.txt`, `uv.lock`, `poetry.lock`, `setup.py`, `environment.yml`).
- Do **not** install MLX, PyTorch, Streamlit, or any other runtime dependency. No `uv add`, no `pip install`.
- Do **not** create a Streamlit app, even as a placeholder.
- Do **not** add CI workflows, pre-commit hooks, linters, formatters, or type checkers.
- Do **not** write toy-task generators or sample datasets.
- Do **not** modify `CLAUDE.md` outside the proposal mechanism.
- Do **not** make semantic edits to `PROJECT_PLAN.md`; structural / typographic fixes only.
- Do **not** rename the project, relicense, or change the stack choice.
- Do **not** add `.gitkeep` files to future `src/` subdirectories "to prepare".
- Do **not** collapse the five phase_context files into one "for convenience" — the separation is load-bearing.
- Do **not** add a CONTRIBUTING.md, CODE_OF_CONDUCT.md, or SECURITY.md in Phase 0. They are reasonable later; they are not a foundation concern.

If any of these feel tempting mid-task, that is the drift signal `CLAUDE.md` was written to catch. Stop and raise the question in `open_questions.md` instead.

---

## 8. Seed Open Questions (for `open_questions.md`)

These are unresolved decisions surfaced by this review. They should live in `open_questions.md` and be answered *before* or *at the start of* Phase 1, not now.

1. **Package manager:** `uv`, `poetry`, `pip + venv`, or conda?
   *Why it matters:* affects lockfile format, reproducibility story, and how the MLX + PyTorch coexistence is expressed.
2. **PyTorch device target:** MPS, CPU-only, or both?
   *Why it matters:* determines whether PyTorch interpretability bridges can run sizable traces on the M1 Air or must stay small.
3. **Python version floor:** 3.11 or 3.12?
   *Why it matters:* MLX versions track closely to CPython releases; picking too aggressive a floor locks out mlx-lm versions.
4. **Checkpoint format:** MLX-native (`.safetensors` via mlx), PyTorch-native, or a neutral `.safetensors` layer?
   *Why it matters:* Phase 5 (checkpoint evolution) and Phase 8 (pretrained bridge) both depend on this.
5. **Tracing framework:** custom MLX hooks, PyTorch hooks, or NNsight-style?
   *Why it matters:* Phase 2 design hinges on this; wrong choice leaks across Phases 3, 4, 6, 7.
6. **Streamlit vs. alternatives:** is Streamlit actually the right choice for layerwise-logit and attention-map views, or will it become a bottleneck?
   *Why it matters:* Principle C says viz is core — locking into a framework whose interaction model fights the task would be expensive to undo.
7. **Repository-name mismatch:** README shows `glassbox-playground/`, project is `little-giant-circuits`. Pick one and update the other.
   *Why it matters:* Small, but it is a visible drift signal.
8. **Phase 0.5?** Should CI / formatting / pre-commit be a small dedicated phase between 0 and 1, or absorbed into Phase 1?
   *Why it matters:* affects what "Phase 0 done" means and whether Phase 1 opens with tooling friction.

None of these need to be answered to finish Phase 0. They need to be *written down* so Phase 1 does not start by re-deriving them.

---

## 9. One-Paragraph Summary for Sonnet

Phase 0 is a documentation-and-scaffolding phase with a surprisingly narrow scope. Build the `docs/phase_context/` loop, create the `docs/proposals/` directory, add an Apache-2.0 `LICENSE`, write a short environment doc and a short workflow doc, stub the three empty `docs/` subdirectories referenced by the README, fix the repo-name inconsistency, and stop. Do not write Python. Do not pin dependencies. Do not scaffold `src/`. The validation is the checklist in §6, not a test suite. When the checklist is green, append a dated entry to `implementation_status.md` and hand back to Opus for an independent verification pass.
