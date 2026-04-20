# Environment

## Target Hardware

**Apple Silicon (M1 Air baseline).** This project is built for Apple Silicon and uses MLX as its primary training framework. MLX is Apple-native and does not run on Linux or Windows. This is a deliberate constraint, not an oversight.

Non-Apple-Silicon users: this project is currently out of scope for your hardware. This may change in later phases if a convincing case is made through the proposal process, but do not assume it will.

## Python Version

**Recommended: Python 3.11.**

Reasoning:
- MLX and mlx-lm versions track CPython releases closely. Using 3.11 ensures broad compatibility with stable MLX releases as of early 2026.
- 3.12 is likely compatible but has not been tested on this project yet.
- 3.13 is not recommended — mlx-lm compatibility is unverified.

This recommendation is not yet enforced by a version file or CI check. That enforcement comes in Phase 1 when the first dependency manifest is created.

## Package Manager

**Decision deferred to Phase 1.** See `docs/phase_context/open_questions.md` Q1.

Candidates: `uv`, `poetry`, `pip + venv`. The choice affects lockfile format and how MLX + PyTorch coexistence is expressed. It will be decided when the first real import is needed, not before.

Do not install any packages yet. Phase 0 has no Python code and no runtime dependencies.

## Core Dependencies (anticipated, not yet installed)

These will be pinned in Phase 1 once the package manager is chosen:

| Library | Role | Framework |
|---------|------|-----------|
| `mlx` | tensor ops, training | Apple-native |
| `mlx-lm` | language model utilities | Apple-native |
| `torch` | interpretability bridge | PyTorch |
| `streamlit` | visualization dashboards | neutral |

## MLX + PyTorch Coexistence

The project uses both MLX and PyTorch. They serve different roles:

- **MLX**: training, local inference, Apple-native performance.
- **PyTorch**: interpretability workflows (hooks, patching, compatibility with tools like TransformerLens or nnsight).

Data moves between them as needed. Checkpoint format for this bridge is an open question (see `open_questions.md` Q4). The rule from `CLAUDE.md` and `PROJECT_PLAN.md §5`: prefer MLX unless the interpretability workflow specifically needs PyTorch.

## Initial Setup (Phase 1)

Instructions will be added here when Phase 1 introduces the first dependency manifest and `src/` tree. For now:

```
# Nothing to install. Phase 0 has no Python code.
```
