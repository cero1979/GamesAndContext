# Contextual Comparability, Benefit-Loss Classifiers and Games

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

The latest methodological revision adds reference-recovery conditioning,
reference-centred parameter bounds, finite strict-label identified sets, and
independently specified synthetic institutional transports. Its failure cases
distinguish rejection of a declared classifier from incompatibility of every
full-rank classifier. These are deterministic stress tests, not empirical
validation. The final snapshot retains these calculations and adds
signature-first presentation, an editable geometric figure, and five additional
regression tests. See the [final reproduction guide](docs/qq_final_reproducibility.md).
The [previous snapshot](docs/qq_reproducibility.md) remains available unchanged.

## Reproduce the latest comparability diagnostics

Use a separate environment for the new snapshot, audited with CPython 3.12.14:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-qq-lock.txt
.venv/bin/python scripts/run_qq_final_audit.py --output-dir results/reproduced
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

Full figure generation also requires `pdflatex`, `standalone` and TikZ (audited
with TeX Live 2020). Add `--skip-figure` when LaTeX is unavailable; the Python
diagnostics, five tables and two diagnostic figures are still regenerated.
Use a fresh output directory to avoid mixing generations.

The suite has **48 tests**: 29 retained regressions, 14 methodological diagnostic
tests and five final-presentation checks. The complete generator writes 16
files: six CSV datasets, an institutional-case JSON file, five TeX tables,
three vector figures and a provenance manifest. The committed final snapshot is
in `results/qq_final`; the manifest records dependency versions and source/output
hashes. All 16 files reproduced byte-identically from the separately packaged
anonymous snapshot in the audited environment; identical bytes are not promised
across all platforms or TeX versions.

Useful entry points are [conditioning](results/qq_final/conditioning.csv),
[finite-label identification](results/qq_final/strict_label_identification.csv),
[institutional transport](results/qq_final/institutional_transport.csv),
[centred robustness](results/qq_final/centred_robustness.csv), and the
[contextual fan figure](results/qq_final/figure_contextual_fans_final.pdf).
A single surviving grid
candidate is not point identification: the analysis includes a distinct
feasible off-grid witness. Residual tolerances are numerical, not statistical.

## Reproduce the retained game and notebook results

Validated with CPython 3.12.13 on macOS and in GitHub Actions.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/run_all.py
```

The final command runs the test suite, regenerates the retained result tables
and figures outside `results/qq`, and executes the notebook into
`results/executed_notebook.ipynb` without changing
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
- `src/context_games/qq_audit.py`: methodological stress tests and numerical artifact generation.
- `scripts/run_qq_final_audit.py`: final presentation and full figure generation.
- `figures/contextual_fans_final.tex`: editable geometric figure, with tested signature coordinates.
- `results/qq_final/`: current 16-file result snapshot, including provenance.
- `docs/qq_final_reproducibility.md`: final reproduction guide, also used in the separate anonymous archive.
- `scripts/run_qq_audit.py`, `results/qq/`: preserved previous diagnostic snapshot.
- `docs/qq_reproducibility.md`: detailed assumptions and interpretation of the numerical diagnostics.
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
| Reference conditioning and small-intercept recovery error | `tests/test_qq_audit.py` | `results/qq_final/conditioning.csv` |
| Finite candidate grids versus continuous identified sets | `tests/test_qq_audit.py` | `results/qq_final/strict_label_identification.csv` |
| Exogenous transport failure, noncommuting routes and a defective cycle | `tests/test_qq_audit.py` | `results/qq_final/institutional_case.json`, `results/qq_final/institutional_transport.csv` |
| Reference-centred finite perturbation bounds | `tests/test_qq_audit.py` | `results/qq_final/centred_robustness.csv` |
| Running evaluations, signature coordinates and strategic/evaluative separation | `tests/test_qq_final_presentation.py` | `results/qq_final/table_running_labels.tex`, `figures/contextual_fans_final.tex` |
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

`requirements-lock.txt` pins the retained numerical and notebook environment.
The original CI job regenerates those artifacts under Linux and fails if they
differ from the committed versions. A separate CI job installs
`requirements-qq-lock.txt`, runs all 48 tests, and regenerates both methodological
snapshots in separate temporary directories, including LaTeX compilation of the
final geometric figure. That job checks successful generation; it does not assert
cross-platform byte identity for these snapshots.

The new published designs are deterministic without random draws; randomised
inequality tests use seed `20260911`. The retained payoff audit uses seed
`20260622`. No external or confidential data are used. Manuscripts, cover
letters and editorial audits remain outside the tracked repository.

This public repository is attributed and is **not anonymous**. For double-anonymous
review, use the separately prepared Online Resource 1 archive, not this repository
or an automatic mirror that retains citation metadata or Git history.
