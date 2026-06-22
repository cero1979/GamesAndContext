# Context-Dependent Benefit-Loss Games

Reproducibility package for the manuscript targeting *Mathematical Social
Sciences*. The repository separates the mathematical model, deterministic
experiments, tests, notebook, generated results, and submission files.

The three social-domain payoff tables are **synthetic benchmarks**, not empirical
estimates. They illustrate formal possibilities and must not be interpreted as
evidence about actual firms, classrooms, or sport teams.

## Reproduce

Validated with CPython 3.12.13 on macOS and in GitHub Actions.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/run_all.py
```

The final command runs the test suite, regenerates all result tables and figures,
and executes the notebook into `results/executed_notebook.ipynb` without changing
the source notebook. Figures are rendered once with Matplotlib's non-interactive
`Agg` backend; notebook execution does not overwrite generated artifacts. CSV
floating-point fields are serialized to 12 significant digits so harmless
last-bit differences in platform math libraries do not alter the archive. All
calculations still use double precision, and reported results use at most six
decimal places.

For a faster code-only check:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m context_games.reproduce --output-dir results
```

## Compile the manuscript

The main source imports `finite_game_results.tex` and `feature_appendix.tex` from
the same directory. With a standard TeX Live installation:

```bash
cd manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error context_dependent_benefit_loss_games_v09.tex
```

The committed PDF is built from those three versioned sources and the vector
figures in `results/`.

## Repository map

- `src/context_games/`: model, benchmark specification, experiments, and CLI.
- `tests/`: regression tests and computational theorem audits.
- `notebooks/`: thin presentation notebook; it imports the tested package.
- `results/`: generated CSV tables and publication-quality figures.
- `manuscript/`: modular LaTeX source, technical appendix, and compiled manuscript.
- `submission/`: journal-specific highlights and disclosure statements.
- `docs/reviewer_audit.md`: hostile-review checklist and current disposition.
- `.github/workflows/reproduce.yml`: clean-environment reproduction check.

## Main audits

- Feature weights reproduce every benchmark payoff exactly.
- Class maps, margins, pure equilibria, and trajectory distances are regression-tested.
- The configuration theorem is exhaustively checked on all `5^8 = 390,625`
  `2x2` games with coordinates in `{-2, -1, 0, 1, 2}`.
- Its finite-game extension is checked on all `2 * 3^12 = 1,062,882`
  rectangular `2x3` and `3x2` games with coordinates in `{-2, -1, 1}`.
- Exact open-ball radii distinguish class-map and complete pure-NE-set robustness.
- The open robustness ball for `Gamma-diamond` is checked at all 256 vertices;
  a separate test confirms that radius `3/4` itself is not included.
- Seeded payoff perturbations distinguish class robustness from equilibrium robustness.
- Horizon diagnostics report one-step residuals and finite-horizon changes.

## Reproducibility status

`requirements-lock.txt` pins the complete numerical and notebook environment used
for the archived results. CI installs that lock, regenerates the package under Linux,
and fails if any committed result differs. The computations are deterministic except
for the explicitly seeded payoff audit (`20260622`); no external or confidential data
are used.
