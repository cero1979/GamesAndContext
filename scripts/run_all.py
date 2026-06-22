#!/usr/bin/env python3
"""Rebuild results, run tests, and execute the notebook without modifying it."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "reproduce_context_dependent_benefit_loss_games_v09.ipynb"
EXECUTED_NOTEBOOK = ROOT / "results" / "executed_notebook.ipynb"


def main() -> int:
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    subprocess.run(
        [sys.executable, "-m", "context_games.reproduce", "--output-dir", str(ROOT / "results")],
        cwd=ROOT,
        check=True,
    )
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=900,
        kernel_name=notebook.metadata.get("kernelspec", {}).get("name", "python3"),
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    EXECUTED_NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, EXECUTED_NOTEBOOK)
    print(f"All checks passed; executed notebook written to {EXECUTED_NOTEBOOK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
