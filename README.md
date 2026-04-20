# Little-Giant-Circuits

_"I no longer just use language models. I can see what they are doing."_

**Little-Giant-Circuits** is a research + educational project for learning how small language models actually work from the inside.

The goal is not just to build an LLM project, but to **understand**:
- how tiny transformers learn during training,
- how information flows during inference,
- which internal components matter,
- how interventions change outputs,
- and why interpretability is often more about **features and circuits** than isolated neurons.

This project is built for a **mixed audience**:
- curious beginners,
- ML engineers,
- students learning LLM internals,
- and researchers who want a clean, public, reproducible playground.

The project is designed for **Apple Silicon (MacBook M1 Air)** using an **MLX-first + PyTorch interpretability bridge** approach:
- **MLX / mlx-lm** for fast local training and inference on Apple hardware,
- **PyTorch** where interpretability tooling is stronger,
- **Streamlit** for visual exploration,
- and a workflow that emphasizes **learning over blind implementation**.

---

## Core Philosophy

This repo is not a “just make it work” coding project.

It is a **glass box**:
- every phase should make the model more visible,
- every build step should improve understanding,
- every tool should help answer **why** a model behaved a certain way.

We are intentionally avoiding drift into:
- generic chatbot building,
- premature scaling,
- opaque model wrappers,
- or “pretty dashboard first, understanding later.”

The priority is:

1. **train tiny models**
2. **inspect internal activations**
3. **localize causal components**
4. **intervene on internals**
5. **track how learning emerges over training**
6. **only then move toward small pretrained models**

---

## Main Objectives

### 1. Learn how tiny transformers learn
We start with toy tasks where the ground-truth behavior is known:
- key-value retrieval
- induction/copying
- modular arithmetic
- bracket matching
- simple factual lookup
- sorting / reversal

These tasks let us connect:
- dataset structure,
- training dynamics,
- weight updates,
- activation patterns,
- and final outputs.

### 2. Build a forward-pass microscope
For each prompt, we want to inspect:
- attention maps
- neuron activations
- MLP outputs
- residual stream states
- layerwise logit evolution

### 3. Move from observation to causality
We do not want only correlation.

We want to test:
- zero ablation
- mean ablation
- activation patching
- runtime steering
- feature suppression / amplification

### 4. Understand learning over time
We save checkpoints during training and compare:
- accuracy growth
- head importance
- emergence of useful representations
- when specific computations become visible

### 5. Prefer interpretable representations over naive neuron-only thinking
Single neurons matter sometimes, but meaning is often distributed.

This repo treats:
- neurons,
- heads,
- residual streams,
- sparse features,
- and circuits

as different levels of analysis.

---

## Why “Little-Giant-Circuits”?

Because the point is to open the model and inspect it, not treat it like a black box.

Other candidate names that fit the same spirit:
- Neuron Safari
- Token Anatomy Lab
- Signal Under Glass
- Prompt to Pulse
- Little Giant Circuits
- The Curious Transformer

---

## Tech Stack

### Core
- **Python**
- **MLX**
- **mlx-lm**
- **PyTorch**
- **Streamlit**

### Interpretability / Analysis
- custom hooks / tracing
- PyTorch inspection utilities
- optional NNsight-style workflow where useful
- sparse autoencoder experiments later

### Visualization
- Streamlit dashboards
- structured experiment logging
- side-by-side run comparison

---

## Project Scope

### Phase 1 — tiny models from scratch
Train tiny transformers on synthetic tasks.

### Phase 2 — internal tracing
Record attention, activations, residuals, and logits.

### Phase 3 — visualization
Build a Streamlit microscope for prompt-level inspection.

### Phase 4 — causal analysis
Ablation, patching, and controlled interventions.

### Phase 5 — checkpoint evolution
Study how internal computation emerges across training.

### Phase 6 — sparse features
Train small sparse autoencoders and compare features vs neurons.

### Phase 7 — runtime editing lab
Interactively modify activations and observe behavior changes.

### Phase 8 — small pretrained bridge
Only after toy-model interpretability works reliably.

---

## Repository Structure

```text
little-giant-circuits/
├── README.md
├── LICENSE
├── CLAUDE.md
├── CLAUDE_BOOTSTRAP.md
├── pyproject.toml          ← added Phase 1
├── requirements.txt        ← added Phase 1
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── ENVIRONMENT.md      ← added Phase 0
│   ├── WORKFLOW.md         ← added Phase 0
│   ├── architecture/
│   ├── theory/
│   ├── phases/
│   ├── phase_context/
│   └── proposals/          ← added Phase 0
├── src/                    ← added Phase 1
│   ├── models/
│   ├── training/
│   ├── datasets/
│   ├── tracing/            ← Phase 2
│   ├── interventions/      ← Phase 4
│   ├── sae/                ← Phase 6
│   ├── viz/                ← Phase 3
│   └── utils/
├── checkpoints/            ← created during training
├── runs/                   ← created during training
├── data/
│   ├── generated/
│   └── processed/
├── experiments/
├── notebooks/
└── app/
    └── streamlit_app.py    ← Phase 3