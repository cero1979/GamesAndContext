# Contextual Benefit-Loss Classifiers and Games

[![Reproduce results](https://github.com/cero1979/GamesAndContext/actions/workflows/reproduce.yml/badge.svg)](https://github.com/cero1979/GamesAndContext/actions/workflows/reproduce.yml)

Reproducibility package for the contextual benefit-loss classification research
program. The repository contains the affine contextual model, finite-game
benchmarks, deterministic experiments, tests, notebook, generated result tables,
and publication-quality result figures.

The article source, compiled manuscript, and journal submission files are kept as
local working files only and are intentionally ignored by Git.

The three social-domain payoff tables are **synthetic benchmarks**, not empirical
estimates. They illustrate formal possibilities and must not be interpreted as
evidence about actual firms, classrooms, or sport teams.

## Current scope

The package has two complementary layers. The current mathematical layer studies
contextual classifiers induced by invertible affine maps: transport identities,
composition, holonomy compatibility, finite-label feasibility, and robustness to
perturbations. The retained finite-game layer reproduces the earlier benchmark
enumerations, equilibrium audits, and trajectory diagnostics. Those enumerations
are computational checks and examples; they are not presented as substitutes for
the analytical results.

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
calculations still use double precision; theorem-audit residuals certified below
their explicit `1e-12` tolerance are stored as exact zero, and reported results
use at most six decimal places.

For a faster code-only check:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m context_games.reproduce --output-dir results
```

## Repository map

- `src/context_games/contextual_classifier.py`: affine contexts, transports,
  holonomy checks, finite labels, and contextual robustness radii.
- `src/context_games/`: benchmark game model, experiments, and reproduction CLI.
- `tests/`: regression tests and computational theorem audits.
- `notebooks/`: thin presentation notebook; it imports the tested package.
- `results/`: generated CSV tables and publication-quality figures.
- `CITATION.cff`: machine-readable repository citation metadata.
- `.github/workflows/reproduce.yml`: clean-environment reproduction check.

## Claim-to-artifact map

| Mathematical or computational claim | Tested implementation | Generated artifact |
| --- | --- | --- |
| Affine evaluation and transport composition identities | `tests/test_contextual_classifier.py` | `results/contextual_classifier_audit.csv` |
| Positive-diagonal cycle compatibility and holonomy recovery | `tests/test_contextual_classifier.py` | `results/contextual_classifier_audit.csv` |
| Finite strict labels as linear inequalities | `src/context_games/contextual_classifier.py` | `results/contextual_classifier_audit.csv` |
| Exact contextual robustness radii under three norms | `tests/test_contextual_classifier.py` | `results/contextual_classifier_audit.csv` |
| Label changes along continuous context paths | `src/context_games/experiments.py` | `results/context_path_events.csv` |
| Finite-game configurations, equilibria, and perturbations | `tests/test_theorems.py` | Remaining CSV and PDF files in `results/` |

## Main audits

- Affine transports satisfy the exact evaluation identity and the groupoid
  composition law.
- A quarter-turn cycle is rejected by the positive-diagonal holonomy criterion;
  a nondegenerate positive cycle recovers its reference and boundary directions.
- Finite strict labels are represented as an open system of linear inequalities.
- Contextual robustness radii are checked under the one, Euclidean, and sup norms.
- Feature weights reproduce every benchmark payoff exactly.
- Class maps, margins, pure equilibria, and trajectory distances are regression-tested.
- Increasing opponent-contingent payoff maps that fix zero preserve both class
  maps and pure incentives; harmless offsets are tested to change class meaning.
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
