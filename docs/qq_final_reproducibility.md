# Online Resource 1: contextual-comparability diagnostics

This anonymous snapshot contains synthetic mathematical diagnostics, not
empirical observations. The complete proofs remain in the main manuscript.
No author metadata, public repository links or Git history is included.

## Reproduce

Use CPython 3.12; the audited environment is CPython 3.12.14 with the exact
packages in requirements-qq-lock.txt. To compile the geometric figure, install
pdflatex with the standalone and TikZ packages (tested with TeX Live 2020).

    python3.12 -m venv .venv
    .venv/bin/python -m pip install -r requirements-qq-lock.txt
    .venv/bin/python scripts/run_qq_final_audit.py --output-dir results/reproduced
    PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v

Use --skip-figure on the generation command when LaTeX is unavailable. The
Python diagnostics, tables and two diagnostic figures are still regenerated;
the supplied geometric figure remains inspectable as PDF and editable TeX.
Use a fresh output directory to avoid mixing generations.

The suite contains 48 tests. The published designs use no random draws;
randomised inequality and game-perturbation tests use seed 20260911. Retained
game regression tests use their own explicitly fixed designs and seed.

## Contents

- Six CSV files give the running example, conditioning, finite-label feasible
  sets and grid candidates, institutional transports and centred robustness.
- institutional_case.json gives the prescribed synthetic rules and exact
  rational certificate for the defective reporting cycle.
- Five generated TeX tables supply all numerical tables in the article.
- Three vector PDFs supply the geometric illustration and diagnostic figures.
- figures/contextual_fans_final.tex is the editable geometric source. Its
  point, boundary and signature coordinates are covered by unit tests.
- provenance.json records dependency versions and hashes of code, tests,
  figure source and all 15 generated artifacts. Together they form 16 files.

The wrapper reuses the previous numerical generator and changes only the
running table's presentation, the primary figure labels and final provenance.
The compact game example is covered by a separate regression test.

## Interpretation and limits

Finite candidate grids are not continuous identified sets; a distinct feasible
off-grid witness remains even when one grid point survives. Reference recovery
can be ill-conditioned while a fixed outcome has a large classification margin.
The centred parameter bound retains the second-order error term.

Replacing the redistribution rule rejects the declared appraisal charter but
not every classifier. Retaining both routes gives a noncommuting pair of cycles.
The separate reporting shear is not diagonalisable despite positive eigenvalues;
its obstruction uses exact rational arithmetic, not numerical multiplicity.

The restrictions concern ordered, oriented appraisals on the full affine
domain. Residual magnitudes depend on fixed scales; tolerance 1e-12 is numerical,
not a significance threshold. No external validation or causal claim follows.
Byte-identical reproduction was checked in the audited environment, not
promised across all operating systems or TeX versions. No network access is
needed after installing the Python and TeX dependencies.
