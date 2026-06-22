#!/usr/bin/env python3
"""Build the thin, presentation-oriented reproducibility notebook."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "notebooks" / "reproduce_context_dependent_benefit_loss_games_v09.ipynb"


def main() -> int:
    notebook = nbf.v4.new_notebook()
    notebook.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    notebook.metadata["language_info"] = {"name": "python", "version": "3.12"}
    notebook.cells = [
        nbf.v4.new_markdown_cell(
            "# Reproducing context-dependent benefit-loss games\n\n"
            "This notebook is a readable interface to the tested `context_games` package. "
            "The model and theorem checks live in `src/` and `tests/`; no result depends on hidden notebook state."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import platform\n"
            "import matplotlib\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "from context_games.benchmarks import BENCHMARKS\n"
            "from context_games.experiments import (baseline_tables, convergence_diagnostics, "
            "exhaustive_configuration_audit, perturbation_audit, robustness_radii, "
            "sensitivity_grid, sensitivity_grid_summary)\n\n"
            "RESULTS = Path('results')\n"
            "print({'python': platform.python_version(), 'numpy': np.__version__, "
            "'pandas': pd.__version__, 'matplotlib': matplotlib.__version__})"
        ),
        nbf.v4.new_markdown_cell("## 1. Payoffs, classes, and equilibria"),
        nbf.v4.new_code_cell(
            "tables = baseline_tables()\n"
            "display(tables['payoff_table'])\n"
            "display(tables['class_table'])\n"
            "display(tables['pure_nash'])"
        ),
        nbf.v4.new_markdown_cell("## 2. Baseline dynamics and finite-horizon diagnostics"),
        nbf.v4.new_code_cell("display(tables['final_values'])\ndisplay(convergence_diagnostics())"),
        nbf.v4.new_markdown_cell(
            "The horizon check reports the one-step residual and the change relative to the previous horizon. "
            "It guards against reporting an arbitrary finite iterate as a converged result."
        ),
        nbf.v4.new_markdown_cell("## 3. Deterministic design over initial conditions and intensities"),
        nbf.v4.new_code_cell(
            "grid = sensitivity_grid()\n"
            "display(sensitivity_grid_summary(grid))\n"
            "grid.head()"
        ),
        nbf.v4.new_markdown_cell(
            "The design points are not random observations. Ranges are therefore reported instead of "
            "standard errors or inferential summaries."
        ),
        nbf.v4.new_markdown_cell("## 4. Payoff-perturbation audit"),
        nbf.v4.new_code_cell(
            "display(robustness_radii())\n"
            "perturbations = perturbation_audit()\n"
            "display(perturbations)"
        ),
        nbf.v4.new_markdown_cell(
            "For the business benchmark, the class map is locally robust but the original two-equilibrium "
            "set is not: continuous perturbations break the exact actor indifference with probability one."
        ),
        nbf.v4.new_markdown_cell("## 5. Exhaustive finite audit of the configuration theorem"),
        nbf.v4.new_code_cell(
            "display(exhaustive_configuration_audit())\n"
            "display(pd.read_csv(RESULTS / 'rectangular_configuration_audit.csv'))"
        ),
        nbf.v4.new_markdown_cell(
            "All $5^8=390{,}625$ games with payoff coordinates in $\\{-2,-1,0,1,2\\}$ are checked. "
            "The finite-game extension is also checked on all $2\\cdot3^{12}=1{,}062{,}882$ "
            "rectangular $2\\times3$ and $3\\times2$ games over $\\{-2,-1,1\\}$. "
            "These are finite computational audits, not replacements for the proofs."
        ),
        nbf.v4.new_markdown_cell("## 6. Archived tables and figures"),
        nbf.v4.new_code_cell(
            "sorted(path.name for path in RESULTS.iterdir() if path.is_file())"
        ),
    ]
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, DESTINATION)
    print(f"Wrote {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
