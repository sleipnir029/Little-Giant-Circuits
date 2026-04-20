
---

# `CLAUDE_BOOTSTRAP.md`

```markdown
# Little-Giant-Circuits — Claude Bootstrap Guide

This document defines how `CLAUDE.md` should be created, how Claude Code should be used on this repo, and how the project should stay aligned with its learning-first goal as it evolves.

This file is not the final `CLAUDE.md`.  
It is the plan used to create and maintain it.

---

## 1. Why This Exists

This project has a high drift risk.

Without strong guardrails, Claude Code may gradually optimize for:
- shipping more code,
- adding unnecessary features,
- polishing interfaces too early,
- or silently changing the project into a general ML engineering repo.

That would damage the main purpose:
> learn how LLMs work internally through building and interpretation.

So `CLAUDE.md` must act as a persistent operating manual that keeps the project aligned.

---

## 2. What `CLAUDE.md` Must Do

The final `CLAUDE.md` should:

1. remind the agent that this is a **research + educational** project
2. prioritize **understanding over implementation speed**
3. keep **visualization and interpretation** as first-class requirements
4. prevent scope drift
5. require documentation and explanation
6. require file-based context updates
7. force explicit proposals before major plan changes

---

## 3. Recommended `CLAUDE.md` Structure

The first version of `CLAUDE.md` should contain the following sections:

### A. Project identity
- repo name
- mission
- target audience
- Apple Silicon constraints
- stack policy

### B. Core project principles
- learning first
- small models first
- visualization is core
- causal analysis over passive inspection
- no silent scope expansion

### C. Workflow rules
- read key docs before acting
- phase-based implementation only
- update status files
- document what changed
- do not rewrite plan casually

### D. Build priorities
- toy tasks before pretrained models
- MLX-first, PyTorch bridge only when needed
- Streamlit for first interface
- simple inspectable code

### E. Documentation rules
- explain what, why, and how
- add runnable docs
- explain internal choices
- record limitations

### F. Proposal system
- how changes to `CLAUDE.md` are proposed
- how roadmap changes are proposed
- what counts as “too large to silently implement”

### G. File-based memory
- required phase context files
- required status updates
- what Opus writes
- what Sonnet writes

---

## 4. Initial `CLAUDE.md` Draft Content

Below is the recommended starter content for `CLAUDE.md`.

---

# Suggested `CLAUDE.md`

```markdown
# CLAUDE.md

## Project Mission

This repository is a research + educational project for learning how language models work internally by training tiny transformers, tracing their computations, visualizing their internals, and testing interventions.

The goal is not only to build working code.  
The goal is to make the model understandable.

---

## Core Principles

1. **Learning first**
   - Prefer clarity over speed
   - Prefer explanation over abstraction
   - Prefer inspectable code over clever code

2. **Small models first**
   - Start with tiny transformers and toy tasks
   - Do not jump early into pretrained models
   - Earn complexity through understanding

3. **Visualization is core**
   - Visualization and interpretation are not optional
   - Every major phase should support better inspection

4. **Causal analysis matters**
   - Observation alone is not enough
   - Prioritize ablation, patching, and intervention where relevant

5. **Do not drift**
   - Do not add features that shift the project away from understanding LLM internals
   - Do not silently broaden the scope
   - Proposed improvements must be documented if they affect project direction

---

## Stack Policy

- Use **MLX-first** for tiny model training and local Apple Silicon performance
- Use **PyTorch** when interpretability tooling or tracing workflows require it
- Use **Streamlit** for the first visualization interface
- Keep dependencies minimal and justified

---

## Before Starting Any Work

Always read:
- `README.md`
- `docs/PROJECT_PLAN.md`
- `docs/phase_context/current_phase.md`
- `docs/phase_context/review_notes.md` if it exists
- `docs/phase_context/open_questions.md`
- `docs/phase_context/implementation_status.md` if it exists

Do not begin implementation without checking the active phase and current constraints.

---

## Implementation Rules

1. Work phase-by-phase
2. Do not implement beyond the active phase unless explicitly asked
3. Prefer modular code
4. Prefer transparent naming
5. Add meaningful comments where they help understanding
6. Keep visual interpretability in mind while building model internals
7. Add or update documentation with each meaningful implementation step

---

## Documentation Requirements

For each phase, document:
- what was built
- why it was built this way
- how it works
- how to run it
- how to verify it
- what limitations remain

Code changes without documentation are incomplete.

---

## Required Status Updates

After meaningful implementation work, update:

- `docs/phase_context/implementation_status.md`
- `docs/phase_context/next_actions.md`
- `docs/phase_context/open_questions.md` when needed

Implementation status should include:
- completed items
- remaining items
- design decisions
- risks
- suggested next steps

---

## Opus / Sonnet Workflow

- **Opus** acts as advisor and reviewer
- **Sonnet** acts as implementation lead

Because chat context can be unstable across model switches, the project uses file-based context.

Required context files:
- `docs/phase_context/current_phase.md`
- `docs/phase_context/review_notes.md`
- `docs/phase_context/implementation_status.md`
- `docs/phase_context/open_questions.md`
- `docs/phase_context/next_actions.md`

Opus should write critique and guidance into review notes.  
Sonnet should read those notes and implement accordingly.

---

## Change Control

Do not rewrite `CLAUDE.md` directly unless explicitly instructed or unless a reviewed proposal exists.

If you believe `CLAUDE.md` should change, create a proposal file in:
- `docs/proposals/`

Proposal must include:
- current problem
- proposed change
- reason
- expected benefit
- risk of drift

---

## What Not To Do

- Do not turn this into a generic chatbot project
- Do not prioritize polish over interpretability
- Do not add large pretrained-model workflows too early
- Do not introduce unnecessary complexity
- Do not silently expand the scope
- Do not replace educational clarity with convenience wrappers

---

## Success Condition

A phase is successful if it improves the user’s ability to understand:
- what the model learned,
- how it processes a prompt,
- which internal parts matter,
- and how internal changes affect outputs.