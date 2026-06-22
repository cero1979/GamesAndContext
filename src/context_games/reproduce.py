"""Command-line entry point for all deterministic experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

from .experiments import run_all


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    run_all(args.output_dir)
    print(f"Reproduction complete: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
