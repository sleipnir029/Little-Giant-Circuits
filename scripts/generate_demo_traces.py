"""
generate_demo_traces.py — generate a demo trace for every trained task.

Run once before starting the Streamlit app to have traces ready for all tasks:

    python scripts/generate_demo_traces.py

This script creates traces/{task}/demo/ for each task that has a checkpoint.
Tasks without checkpoints are skipped with a warning.

After running this script, the Streamlit app's "Load saved trace" mode will
have content for every task, so you can switch between tasks without clicking
"Run trace" each time.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

import mlx.core as mx

from src.viz.loading import DEMO_PROMPTS, TASKS, load_model
from src.tracing import trace, save_trace


def main() -> None:
    print("Generating demo traces for all trained tasks...")
    print()

    for task in TASKS:
        ckpt_base = _REPO / "checkpoints" / task
        if not ckpt_base.exists() or not any(ckpt_base.iterdir()):
            print(f"  [{task}] SKIP — no checkpoint found at {ckpt_base}")
            continue

        # Find latest checkpoint
        latest_ckpt = sorted(ckpt_base.iterdir(), key=lambda p: p.name)[-1]

        # Check if demo trace already exists
        out_dir = _REPO / "traces" / task / "demo"
        if (out_dir / "activations.safetensors").exists():
            print(f"  [{task}] SKIP — trace already exists at {out_dir}")
            continue

        try:
            model, cfg = load_model(latest_ckpt)
            tokens_list = DEMO_PROMPTS[task]
            tokens = mx.array(tokens_list)[None, :]

            _, cache = trace(model, tokens)
            save_trace(
                cache=cache,
                tokens=tokens[0],
                checkpoint_dir=latest_ckpt,
                task=task,
                out_dir=out_dir,
            )
            print(f"  [{task}] OK — saved to {out_dir}  (tokens: {tokens_list})")

        except Exception as e:
            print(f"  [{task}] ERROR — {e}")

    print()
    print("Done. Start the app with:")
    print("    streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
