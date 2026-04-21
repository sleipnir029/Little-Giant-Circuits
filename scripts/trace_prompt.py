"""
trace_prompt.py — trace a trained checkpoint on a prompt and inspect the activations.

Usage:
    # Trace the latest induction checkpoint with the default induction demo prompt:
    python scripts/trace_prompt.py --task induction

    # Trace a specific checkpoint:
    python scripts/trace_prompt.py --task induction --checkpoint checkpoints/induction/0002000

    # Trace with a custom token sequence:
    python scripts/trace_prompt.py --task induction --tokens 3 7 1 5 3 7 1

    # Save the trace to disk:
    python scripts/trace_prompt.py --task induction --save traces/induction/demo

What this script shows
-----------------------
For each layer and each attention head, it prints the attention pattern (rows =
query positions, columns = key positions). For a well-trained induction model you
should see at least one head in layer 1 (0-indexed) where query position i attends
strongly back to i - (half), the position where the same token appeared in the first
half. This is the induction circuit.

The script also prints top-3 predicted tokens at each position, the full activation
cache key inventory, and a per-head attention pattern summary.
"""

import argparse
import json
import sys
from pathlib import Path

# Add repo root to path so imports work from any CWD
_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

import mlx.core as mx
import numpy as np

from src.models.transformer import Transformer
from src.tracing import ActivationCache, load_trace, save_trace, trace
from src.utils.checkpoint import load
from src.utils.config import ModelConfig


# ---------------------------------------------------------------------------
# Default demo prompts per task (hand-crafted, known-good sequences)
# ---------------------------------------------------------------------------
DEMO_PROMPTS: dict[str, list[int]] = {
    # Induction: full 15-token input for the seq_len=16 trained model.
    # Format: [prefix(8) | prefix(8)][:-1] for next-token prediction.
    # Induction circuit fires at positions 8-14 (second half).
    # At pos 8 (tok=3), the model should predict tok=7 (what followed 3 at pos 0).
    "induction": [3, 7, 1, 5, 8, 2, 4, 6, 3, 7, 1, 5, 8, 2, 4],
    # KV retrieval: [k1,v1, k2,v2, k3,v3, query_key] (seq_len=7 = 8-1)
    "kv_retrieval": [5, 11, 8, 14, 3, 9, 5],
    # Modular arith: single pair [a, b] — model predicts (a+b)%13
    "modular_arith": [4, 7],
    # Bracket matching: a short bracket sequence
    "bracket_match": [1, 1, 2, 1, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 2],
    # Factual lookup: [subject] — model predicts attribute
    "factual_lookup": [5],
    # Sorting: [t1, t2, t3, t4, SEP] — model predicts reversed half
    "sorting": [8, 3, 15, 6, 31],
}


def find_latest_checkpoint(task: str) -> Path:
    base = _REPO / "checkpoints" / task
    if not base.exists():
        raise FileNotFoundError(
            f"No checkpoint directory found for task '{task}' at {base}\n"
            f"Run: python src/training/train.py --task {task}"
        )
    steps = sorted(base.iterdir(), key=lambda p: p.name)
    if not steps:
        raise FileNotFoundError(f"No checkpoint subdirectories in {base}")
    return steps[-1]


def build_model(checkpoint_dir: Path) -> tuple[Transformer, dict]:
    cfg_raw = json.loads((checkpoint_dir / "config.json").read_text())
    mcfg = ModelConfig(**cfg_raw["model"])
    model = Transformer(
        vocab_size=mcfg.vocab_size,
        d_model=mcfg.d_model,
        n_layers=mcfg.n_layers,
        n_heads=mcfg.n_heads,
        seq_len=mcfg.seq_len,
    )
    metrics = load(model, checkpoint_dir)
    return model, cfg_raw


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_attention_pattern(name: str, pattern: np.ndarray, threshold: float = 0.1) -> None:
    """Print a T×T attention pattern as a grid. Strong weights (>threshold) shown as '#'."""
    T = pattern.shape[0]
    print(f"\n  {name}  (rows=query, cols=key, '#'={threshold:.0%}+ weight)")
    header = "       " + " ".join(f"{j:2d}" for j in range(T))
    print(header)
    for i in range(T):
        row = " ".join("##" if pattern[i, j] >= threshold else "  " for j in range(T))
        print(f"  q={i:2d}: {row}  | max_key={pattern[i].argmax():2d} ({pattern[i].max():.2f})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trace a trained checkpoint on a prompt.")
    parser.add_argument("--task", required=True, choices=list(DEMO_PROMPTS.keys()), help="Task name")
    parser.add_argument("--checkpoint", type=Path, default=None, help="Checkpoint dir (default: latest)")
    parser.add_argument("--tokens", type=int, nargs="+", default=None, help="Custom token sequence")
    parser.add_argument("--save", type=Path, default=None, help="Save trace to this directory")
    parser.add_argument("--topk", type=int, default=3, help="Top-k predictions to show (default 3)")
    args = parser.parse_args()

    # Resolve checkpoint
    checkpoint_dir = args.checkpoint or find_latest_checkpoint(args.task)
    print(f"Checkpoint: {checkpoint_dir}")

    # Build model
    model, cfg = build_model(checkpoint_dir)
    print(f"Model: vocab={cfg['model']['vocab_size']}, d_model={cfg['model']['d_model']}, "
          f"n_layers={cfg['model']['n_layers']}, n_heads={cfg['model']['n_heads']}")

    # Resolve tokens
    raw_tokens = args.tokens if args.tokens is not None else DEMO_PROMPTS[args.task]
    tokens = mx.array(raw_tokens)[None, :]  # (1, T)
    print(f"Input tokens ({len(raw_tokens)}): {raw_tokens}")

    # -----------------------------------------------------------------------
    # Anti-drift check: verify traced logits match plain model(tokens)
    # -----------------------------------------------------------------------
    plain_logits = model(tokens)
    traced_logits, cache = trace(model, tokens)

    mx.eval(plain_logits, traced_logits)
    plain_np = np.array(plain_logits)
    traced_np = np.array(traced_logits)

    if not np.allclose(plain_np, traced_np, atol=1e-5):
        print("\n[ERROR] Anti-drift check FAILED: traced logits differ from plain forward pass!")
        print(f"  max diff = {np.abs(plain_np - traced_np).max():.2e}")
        sys.exit(1)
    print("\nAnti-drift check PASSED: traced logits == model(tokens) (max diff < 1e-5)")

    # -----------------------------------------------------------------------
    # Cache inventory
    # -----------------------------------------------------------------------
    print_section("Activation Cache Keys")
    for key in cache.keys():
        shape = tuple(cache[key].shape)
        print(f"  {key:<45s} {str(shape)}")

    # -----------------------------------------------------------------------
    # Top-k predictions at each position
    # -----------------------------------------------------------------------
    print_section(f"Top-{args.topk} Predictions at Each Position")
    T = len(raw_tokens)
    logits_sq = traced_np[0]  # (T, vocab)
    for t in range(T):
        top_idx = np.argsort(logits_sq[t])[::-1][:args.topk]
        top_probs = np.exp(logits_sq[t][top_idx]) / np.exp(logits_sq[t]).sum()
        pred_str = ", ".join(f"tok={i} ({p:.2%})" for i, p in zip(top_idx, top_probs))
        actual_next = str(raw_tokens[t + 1]) if t + 1 < len(raw_tokens) else "?"
        print(f"  pos {t:2d} | next_actual={actual_next:>3s} | top-{args.topk}: {pred_str}")

    # -----------------------------------------------------------------------
    # Attention patterns — per layer, per head
    # -----------------------------------------------------------------------
    n_layers = cfg["model"]["n_layers"]
    n_heads = cfg["model"]["n_heads"]

    print_section("Attention Patterns")
    for layer in range(n_layers):
        pattern_key = f"blocks.{layer}.attn.pattern"
        pattern_np = np.array(cache[pattern_key])[0]  # (H, T, T)
        for head in range(n_heads):
            print_attention_pattern(
                f"Layer {layer}, Head {head}",
                pattern_np[head],
                threshold=0.15,
            )

    # -----------------------------------------------------------------------
    # Residual stream norms (a quick summary of information flow)
    # -----------------------------------------------------------------------
    print_section("Residual Stream L2 Norms (mean over tokens)")
    print(f"  {'key':<45s} {'mean_norm':>10s}")
    embed_np = np.array(cache["embed.combined"])[0]  # (T, d_model)
    print(f"  {'embed.combined':<45s} {np.linalg.norm(embed_np, axis=-1).mean():>10.4f}")
    for layer in range(n_layers):
        for stage in ("resid_pre", "resid_mid", "resid_post"):
            key = f"blocks.{layer}.{stage}"
            arr = np.array(cache[key])[0]  # (T, d_model)
            print(f"  {key:<45s} {np.linalg.norm(arr, axis=-1).mean():>10.4f}")

    # -----------------------------------------------------------------------
    # Optional: save trace
    # -----------------------------------------------------------------------
    if args.save:
        out_path = save_trace(
            cache=cache,
            tokens=tokens[0],
            checkpoint_dir=checkpoint_dir,
            task=args.task,
            out_dir=args.save,
        )
        print(f"\nTrace saved to: {out_path}")

        # Verify round-trip
        loaded_cache, loaded_meta = load_trace(out_path)
        key = "blocks.0.attn.pattern"
        orig = np.array(cache[key])
        reloaded = np.array(loaded_cache[key])
        if np.allclose(orig, reloaded, atol=1e-5):
            print("Save/load round-trip check PASSED")
        else:
            print(f"Save/load round-trip check FAILED (max diff: {np.abs(orig - reloaded).max():.2e})")

    print("\nDone.")


if __name__ == "__main__":
    main()
