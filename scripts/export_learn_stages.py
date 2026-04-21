"""
CLI: export React Learn Mode JSON packages for all tasks.

Usage:
    python scripts/export_learn_stages.py [--tasks induction kv_retrieval ...]

Reads demo traces from traces/{task}/demo/ and writes JSON packages to
learn_data/{task}/demo.json. Also writes learn_data/manifest.json.

Run this once after generating demo traces:
    python scripts/generate_demo_traces.py
    python scripts/export_learn_stages.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.viz.export_stages import export_stages
from src.viz.loading import TASKS


def _find_trace_dirs(task: str) -> list[Path]:
    """Return trace dirs for a task that have activations.safetensors."""
    base = _REPO / "traces" / task
    if not base.exists():
        return []
    return sorted(
        [p for p in base.iterdir() if (p / "activations.safetensors").exists()],
        key=lambda p: p.name,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export React Learn Mode JSON packages.")
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=TASKS,
        choices=TASKS,
        help="Tasks to export (default: all 6).",
    )
    parser.add_argument(
        "--out-dir",
        default=str(_REPO / "learn_data"),
        help="Output directory for JSON packages (default: learn_data/).",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_entries = []
    total_exported = 0
    total_skipped = 0

    for task in args.tasks:
        trace_dirs = _find_trace_dirs(task)
        if not trace_dirs:
            print(f"  [{task}] no traces found — skipping")
            total_skipped += 1
            continue

        for trace_dir in trace_dirs:
            trace_id = trace_dir.name
            out_path = out_dir / task / f"{trace_id}.json"

            print(f"  [{task}/{trace_id}] exporting...", end=" ", flush=True)
            try:
                package = export_stages(trace_dir, out_path)
                n_stages = len(package["stages"])
                n_tokens = package["n_tokens"]
                print(f"ok ({n_stages} stages, {n_tokens} tokens) → {out_path.relative_to(_REPO)}")
                manifest_entries.append({
                    "task": task,
                    "trace_id": trace_id,
                    "path": f"{task}/{trace_id}.json",
                    "n_tokens": n_tokens,
                    "n_layers": package["n_layers"],
                    "n_stages": n_stages,
                })
                total_exported += 1
            except Exception as exc:
                print(f"FAILED: {exc}")
                total_skipped += 1

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packages": manifest_entries,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nmanifest → {manifest_path.relative_to(_REPO)}")
    print(f"exported: {total_exported}  skipped/failed: {total_skipped}")


if __name__ == "__main__":
    main()
