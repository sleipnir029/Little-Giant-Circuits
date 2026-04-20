"""
Training entry point.

Usage:
    python src/training/train.py --task induction
    python src/training/train.py --task induction --steps 3000 --d_model 64

Trains a tiny transformer on a single toy task.
Checkpoints saved to: checkpoints/{task}/{step:07d}/
Training log saved to: runs/{task}/{timestamp}/train_log.txt
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import mlx.optimizers as optim
import numpy as np
from datetime import timezone

# Ensure repo root is on path when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.datasets import factual_lookup, induction
from src.models.transformer import Transformer
from src.training.loop import compute_accuracy, get_batch, make_train_step
from src.utils.checkpoint import save as save_checkpoint
from src.utils.config import ModelConfig, TrainConfig

TASK_MODULES = {
    "induction": induction,
    "factual_lookup": factual_lookup,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train a tiny transformer on a toy task")
    p.add_argument("--task", default="induction", choices=list(TASK_MODULES))
    p.add_argument("--d_model", type=int, default=64)
    p.add_argument("--n_layers", type=int, default=2)
    p.add_argument("--n_heads", type=int, default=4)
    p.add_argument("--seq_len", type=int, default=16)
    p.add_argument("--vocab_size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--steps", type=int, default=2000)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--n_train", type=int, default=4096)
    p.add_argument("--checkpoint_every", type=int, default=100)
    p.add_argument("--eval_every", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    model_cfg = ModelConfig(
        vocab_size=args.vocab_size,
        d_model=args.d_model,
        n_layers=args.n_layers,
        n_heads=args.n_heads,
        seq_len=args.seq_len,
    )
    train_cfg = TrainConfig(
        task=args.task,
        lr=args.lr,
        steps=args.steps,
        batch_size=args.batch_size,
        n_train=args.n_train,
        checkpoint_every=args.checkpoint_every,
        eval_every=args.eval_every,
        seed=args.seed,
    )

    task_mod = TASK_MODULES[args.task]
    inputs, targets = task_mod.generate(
        n_samples=args.n_train,
        seq_len=args.seq_len,
        vocab_size=args.vocab_size,
        seed=args.seed,
    )

    model = Transformer(
        vocab_size=model_cfg.vocab_size,
        d_model=model_cfg.d_model,
        n_layers=model_cfg.n_layers,
        n_heads=model_cfg.n_heads,
        seq_len=model_cfg.seq_len,
    )

    optimizer = optim.Adam(learning_rate=train_cfg.lr)
    train_step = make_train_step(model)
    rng = np.random.default_rng(args.seed)

    # Set up run log
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path("runs") / args.task / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "train_log.txt"

    checkpoint_base = Path("checkpoints") / args.task

    header = (
        f"task={args.task} d_model={args.d_model} n_layers={args.n_layers} "
        f"n_heads={args.n_heads} seq_len={args.seq_len} vocab={args.vocab_size} "
        f"lr={args.lr} steps={args.steps} batch={args.batch_size} seed={args.seed}"
    )
    print(header)
    print("-" * 70)

    with log_path.open("w") as log:
        log.write(header + "\n")
        log.write("step,loss,accuracy\n")

        t0 = time.time()
        for step in range(1, args.steps + 1):
            x, y = get_batch(inputs, targets, args.batch_size, rng)
            loss = train_step(optimizer, x, y)

            if step % args.eval_every == 0:
                x_eval, y_eval = get_batch(inputs, targets, 256, rng)
                acc = compute_accuracy(model, x_eval, y_eval)
                elapsed = time.time() - t0
                line = f"step={step:5d}  loss={loss:.4f}  acc={acc:.3f}  ({elapsed:.1f}s)"
                print(line)
                log.write(f"{step},{loss:.6f},{acc:.6f}\n")
                log.flush()

            if step % args.checkpoint_every == 0:
                ckpt_dir = checkpoint_base / f"{step:07d}"
                save_checkpoint(
                    model=model,
                    checkpoint_dir=ckpt_dir,
                    model_cfg=model_cfg.to_dict(),
                    train_cfg=train_cfg.to_dict(),
                    step=step,
                    loss=loss,
                    accuracy=acc,
                    task=args.task,
                )
                print(f"  → checkpoint saved: {ckpt_dir}")

    # Final evaluation using task-specific evaluator
    final_metrics = task_mod.evaluate(
        model=model,
        inputs=inputs,
        targets=targets,
        seq_len=args.seq_len,
    )
    print("-" * 70)
    print("Final evaluation:")
    for k, v in final_metrics.items():
        print(f"  {k}: {v:.4f}")
    print(f"Run log: {log_path}")


if __name__ == "__main__":
    main()
