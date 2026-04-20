
---

# `PROJECT_PLAN.md`

```markdown
# Little-Giant-Circuits — Project Plan

## 1. Purpose

This project exists to learn how language models work internally through building, tracing, visualizing, and intervening on small transformer models.

The primary objective is **understanding**, not just implementation.

Every phase must support these questions:
1. What is the model doing?
2. Why is it doing that?
3. Which internal parts matter?
4. What changes when we intervene?
5. How does learning emerge over training?

---

## 2. Non-Negotiable Principles

### Principle A — Learning first
This must not become a generic LLM engineering repo.  
Code serves understanding.

### Principle B — Small models first
We start with tiny transformers and toy tasks before moving to pretrained models.

### Principle C — Visualization is core, not optional
Interpretability and visualization are central deliverables, not polish.

### Principle D — Causal analysis over passive observation
Heatmaps alone are not enough.  
Ablation, patching, and intervention must be part of the system.

### Principle E — Stable plan, controlled evolution
The project should evolve, but not drift from the main educational goal.

---

## 3. Recommended Repo Identity

### Preferred Repo Name
**little-giant-circuits**

### Project Title
**Little-Giant-Circuits**

### Short Description
A research + educational lab for training tiny transformers, visualizing their internals, and learning how language models work through tracing, intervention, and mechanistic analysis.

### Alternative Name Ideas
- neuron-safari
- token-anatomy-lab
- signal-under-glass
- prompt-to-pulse
- little-giant-circuits
- the-curious-transformer

---

## 4. Recommended License

**Apache-2.0**

### Why
Apache-2.0 is recommended over MIT because:
- it is still permissive,
- it is common in technical open-source work,
- and it includes an explicit patent grant.

This is better for a public research/engineering repo.

---

## 5. Stack Strategy

### Main stack
- **MLX-first**
- **PyTorch interpretability bridge**
- **Streamlit**
- Python-based experimentation

### Why
- MLX is a strong fit for Apple Silicon and your M1 Air
- PyTorch gives better support for interpretability workflows
- Streamlit is fast for building interactive local visual tools

### Rule
Use MLX by default for:
- tiny transformer training
- local inference
- Apple-native performance

Use PyTorch when needed for:
- tracing convenience
- ablation/patching workflows
- compatibility with interpretability tooling

---

## 6. High-Level Build Sequence

## Phase 0 — Foundation and constraints
Create project skeleton, documentation backbone, development rules, and `CLAUDE.md`.

### Deliverables
- repo structure
- docs structure
- initial `CLAUDE.md`
- environment docs
- development workflow docs

### Must answer
- what is in scope
- what is out of scope
- how drift is prevented

---

## Phase 1 — Tiny transformer training
Train tiny transformers from scratch on synthetic tasks.

### Tasks
- key-value retrieval
- induction/copying
- modular arithmetic
- bracket matching
- simple factual lookup
- sorting / reversal

### Deliverables
- dataset generators
- tokenization pipeline
- tiny transformer in MLX
- training loop
- checkpoint saving
- metrics logging

### Learning outcomes
- understand next-token learning in a small setting
- connect training objective to behavior
- observe learning progression through checkpoints

---

## Phase 2 — Prompt tracing and activation capture
Add tracing so a single prompt can be inspected layer by layer.

### Capture
- embeddings
- attention scores
- attention patterns
- head outputs
- MLP pre/post activations
- residual stream states
- logits across layers

### Deliverables
- activation cache system
- prompt runner
- trace export format
- comparison-ready data structures

### Learning outcomes
- understand forward-pass computation
- see how information transforms across layers
- identify early signs of answer formation

---

## Phase 3 — Streamlit visualization system
Build the main educational UI.

### Views
- token-by-layer heatmap
- attention map browser
- neuron activation explorer
- residual stream summaries
- layerwise logit evolution
- side-by-side comparison between runs

### Deliverables
- Streamlit app
- modular visual components
- run browser
- experiment comparison mode

### Learning outcomes
- translate raw tensors into understandable views
- compare prompt behavior
- build intuition for transformer internals

---

## Phase 4 — Causal intervention system
Move beyond observation into controlled experiments.

### Interventions
- zero ablation
- mean ablation
- activation patching
- component suppression
- component amplification

### Deliverables
- intervention library
- patching experiment runner
- quantitative effect measurements
- visual before/after comparisons

### Learning outcomes
- distinguish “active” from “causal”
- test which components matter
- understand how internal changes affect outputs

---

## Phase 5 — Learning over training
Track how internal computation emerges.

### Tasks
- compare checkpoints
- analyze evolution of head importance
- track logit formation over time
- measure when target information becomes visible

### Deliverables
- checkpoint comparison tools
- emergence plots
- training-timeline visualizations

### Learning outcomes
- study how the model learns, not only what it knows at the end
- identify when useful internal structure appears

---

## Phase 6 — Sparse features and representation analysis
Add sparse autoencoder experiments on tiny models.

### Focus
- compare raw neurons vs learned sparse features
- identify prompt-selective features
- test feature interventions

### Deliverables
- activation collection pipeline
- small SAE training workflow
- feature browser
- feature intervention support

### Learning outcomes
- understand why neuron-only interpretation is often insufficient
- explore distributed representations more cleanly

---

## Phase 7 — Runtime editing lab
Create an interactive lab for internal manipulation.

### Controls
- choose layer/head/neuron/feature
- ablate or patch
- clamp or amplify
- rerun prompt
- compare output changes

### Deliverables
- interactive edit panel
- output comparison report
- reproducible experiment logging

### Learning outcomes
- connect internal interventions to output behavior
- observe controllable vs unstable modifications

---

## Phase 8 — Small pretrained model bridge
Only after toy-model interpretability is solid.

### Purpose
Test whether the methods developed on tiny models partially transfer to a small pretrained open model.

### Constraints
- keep scope small
- do not let pretrained-model work dominate the repo
- only adopt methods that still support learning

### Learning outcomes
- understand what scales and what breaks
- compare toy-model clarity with real-model complexity

---

## 7. Toy Tasks

All six should be included.

### 1. Key-value retrieval
Tests storage and lookup.

### 2. Induction/copying
Tests sequential pattern continuation.

### 3. Modular arithmetic
Tests algorithmic transformation.

### 4. Bracket matching
Tests structured dependency.

### 5. Simple factual lookup
Tests symbolic association.

### 6. Sorting / reversal
Tests ordered transformation.

### Rule
Each task must include:
- generator
- sample data
- explanation
- expected behavior
- evaluation metric

---

## 8. Visual Priorities

All are important and should be implemented over time:

1. attention maps
2. neuron activations
3. residual stream views
4. layerwise logit evolution
5. activation patching comparison
6. feature/SAE browser
7. checkpoint-over-training evolution

### Build order recommendation
1. attention maps
2. layerwise logit evolution
3. neuron activation explorer
4. run comparison
5. patching comparison
6. checkpoint evolution
7. feature browser

---

## 9. Sonnet + Opus Workflow

## Desired behavior
- **Opus** critiques the phase plan and reviews outcomes
- **Sonnet** implements phase-by-phase

## Real constraint
In practice, model switching causes context loss and token waste.

## Solution
Use a **file-based context system** instead of relying on live conversational continuity.

### Required files
- `docs/phase_context/current_phase.md`
- `docs/phase_context/review_notes.md`
- `docs/phase_context/implementation_status.md`
- `docs/phase_context/open_questions.md`
- `docs/phase_context/next_actions.md`

### Workflow
1. Set active phase in `current_phase.md`
2. Ask Opus to critique the phase and write recommendations into `review_notes.md`
3. Switch to Sonnet
4. Sonnet reads:
   - `CLAUDE.md`
   - `PROJECT_PLAN.md`
   - current phase files
5. Sonnet implements and writes progress into `implementation_status.md`
6. Ask Opus to review result against plan
7. Any proposed rule changes go into proposal docs, not directly into `CLAUDE.md`

### Why this works
This preserves project memory in the repo itself rather than depending on chat memory.

---

## 10. CLAUDE.md Policy

### Role of `CLAUDE.md`
`CLAUDE.md` should act as a persistent local operating manual for the project.

It must:
- reinforce the educational purpose
- prevent drift
- force explanations
- require verification
- require doc updates
- require caution when adding features

### Strict-to-moderate means
- do not change project direction without approval
- may improve internals and code structure if aligned with goals
- may propose expansions, but not silently adopt them

---

## 11. CLAUDE.md Update Mechanism

Use **proposal mode**.

### Rule
`CLAUDE.md` must not be rewritten casually during implementation.

### Update workflow
1. Agent detects need for rule change
2. Agent creates `docs/proposals/claude_update_<date>.md`
3. Proposal explains:
   - current issue
   - proposed change
   - benefit
   - risk of drift
4. Human reviews
5. Only then update `CLAUDE.md`

This protects the plan while still allowing growth.

---

## 12. Prompt Strategy for Claude Code

Prompts should be sequential and cumulative.

### Requirements
- each phase prompt must build on previous work
- each phase prompt must include both:
  - implementation instructions for Sonnet
  - advisory/review instructions for Opus
- prompts must force explanation, not just code generation
- prompts must force documentation and tests

### Important constraint
Because switching models in one live session is awkward, prompts should assume the file-based workflow above.

---

## 13. Prompt Templates by Phase

## Template A — Opus Advisor Prompt

Use this before implementation.

```text
You are Opus acting as research advisor and architecture reviewer for the Little-Giant-Circuits project.

Your job is NOT to implement code. Your job is to critique the current phase plan, identify risks, suggest improvements, and protect the project from drifting away from its main learning goal.

Read and use:
- README.md
- docs/PROJECT_PLAN.md
- CLAUDE.md
- docs/phase_context/current_phase.md
- docs/phase_context/open_questions.md
- docs/phase_context/implementation_status.md (if it exists)
- docs/phase_context/review_notes.md (if it exists)

Your priorities:
1. Protect the educational + research purpose of the project
2. Ensure visualization and interpretation remain first-class
3. Ensure any implementation remains understandable to a learner
4. Identify hidden complexity, drift risk, and technical debt
5. Recommend a minimal but strong scope for this phase

Write your output to:
- docs/phase_context/review_notes.md

Your review must include:
- phase objective
- risks
- recommended scope boundaries
- implementation guidance for Sonnet
- documentation requirements
- tests or validation criteria
- what not to do in this phase