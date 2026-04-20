# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Little-Giant-Circuits is a research + education lab for understanding how small
transformers work internally — training tiny models from scratch, tracing
forward passes, and running causal interventions (ablation, patching, steering).
**Understanding is the deliverable, not a working chatbot.** Code serves
interpretability; treat this as a glass-box playground, not a product.

Authoritative scope and sequencing live in `docs/PROJECT_PLAN.md`. Read it
before proposing new work.

## Non-Negotiable Principles (from PROJECT_PLAN §2)

- **Learning first** — do not let this drift into generic LLM engineering.
- **Small models first** — tiny transformers + toy tasks before any pretrained
  model work (pretrained bridge is Phase 8, gated).
- **Visualization is core, not polish** — Streamlit views are deliverables.
- **Causal over passive** — heatmaps alone are insufficient; ablation and
  patching are required parts of the system, not optional extras.
- **Controlled evolution** — the plan evolves, but not silently; see Update
  Mechanism below.

## Stack Rule (from PROJECT_PLAN §5)

- **MLX-first** for tiny-transformer training and local inference on Apple
  Silicon (M1 Air target).
- **PyTorch bridge** only where interpretability tooling is stronger (tracing,
  patching, SAE work). Do not reintroduce PyTorch for things MLX handles fine.
- **Streamlit** for visualization dashboards.

When a task could be done in either framework, prefer MLX unless the
interpretability workflow specifically needs PyTorch.

## Phase Gating

Phases 0–8 are defined in `docs/PROJECT_PLAN.md §6`. The project progresses
phase-by-phase; **do not jump ahead**. Do not start Phase N+1 work while Phase N
deliverables are incomplete. If a task seems to require future-phase machinery,
raise it instead of building it opportunistically.

Current phase: Phase 0 (foundation — repo skeleton, docs backbone, `CLAUDE.md`).
No `src/` tree exists yet; directories listed in `README.md` under Repository
Structure are the target layout, not the current state.

## File-Based Context Workflow (from PROJECT_PLAN §9)

Project memory lives in the repo, not in chat history. When the following
files exist under `docs/phase_context/`, read them at the start of any
non-trivial task:

- `current_phase.md` — which phase is active
- `review_notes.md` — Opus critique of the current phase
- `implementation_status.md` — what has been built
- `open_questions.md` — unresolved decisions
- `next_actions.md` — immediate next steps

When implementing, append progress to `implementation_status.md`. When a
question is unresolved, write it to `open_questions.md` rather than guessing.

## Role Discipline

Default workflow for non-trivial changes:
1. **Plan** — write or update a short task plan before coding.
2. **Implement** — follow the approved plan; no silent scope expansion.
3. **Review** — review must be independent from implementation; do not
   self-approve code you just wrote.

Prefer directness over politeness in reviews. Surface uncertainty. Do not
claim work is production-ready without evidence (tests run, outputs
inspected, scope check).

## Updating This File (Proposal Mode)

`CLAUDE.md` must not be rewritten casually during implementation. To change
any rule here:

1. Create `docs/proposals/claude_update_<YYYY-MM-DD>.md` describing: current
   issue, proposed change, benefit, drift risk.
2. Wait for human review.
3. Only then edit `CLAUDE.md`.

Small corrections (typos, broken links) do not need a proposal.

## Toy Tasks in Scope (Phase 1)

Key-value retrieval, induction/copying, modular arithmetic, bracket matching,
simple factual lookup, sorting/reversal. Each task must ship with a generator,
sample data, explanation, expected behavior, and an evaluation metric.

## Out of Scope (unless a proposal changes it)

- Generic chatbot / assistant building.
- Pretrained-model work before Phase 8.
- "Pretty dashboard first, understanding later" UI work.
- Opaque model wrappers that hide internals.

## Build / Test Commands

None yet — Phase 0 repo has no Python package or test suite. Commands will be
added here once Phase 1 introduces `src/` and a dependency manifest. Do not
invent commands; update this section via proposal when tooling lands.
