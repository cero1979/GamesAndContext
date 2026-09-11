# Contextual comparability: reproducibility for the QQ revision

This snapshot supplies synthetic, theorem-directed diagnostics. It contains
no empirical observations and makes no statistical validation claim.
The earlier game experiments are separate from the new contextual-comparability
stress tests. The original manuscript and original results were not overwritten.

## Reproduce

Use CPython 3.12. The audited environment was CPython 3.12.14.

    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements-qq-lock.txt
    python scripts/run_qq_audit.py --output-dir results/qq
    PYTHONPATH=src python -m unittest discover -s tests -v

The current suite has 43 tests, including legacy regressions and 14 tests
of the new diagnostics. The published generation is deterministic; the
randomised inequality tests use seed 20260911. No network access is needed
after installing the dependencies.

## Outputs and interpretation

- running_labels.csv: all four running-example scores, including the
  correction (0,-2) to (1,-3).
- conditioning.csv: determinant, smallest singular value, condition number,
  reference-recovery error/bound and the fixed outcome margin.
- strict_label_identification.csv: diagnostics for nested samples.
  Candidate-grid counts are not continuous identified sets; a separate,
  distinct normalised off-grid witness remains feasible.
- institutional_case.json and institutional_transport.csv: prescribed
  synthetic budget/funding/redistribution rules, exact and altered maps,
  witnesses and an exact rational certificate for the reporting shear.
- centred_robustness.csv: finite perturbations including the second-order
  term; row-specific margins differ from the minimum signature margin.
- Five generated TeX tables and two vector PDF figures supply the numerical
  material in the revised manuscript.
- provenance.json: dependency versions and SHA-256 hashes of source files,
  tests, lock file and outputs. No author metadata or identifying Git commit
  is required to reproduce this snapshot.

The altered redistribution **replaces** the original rule. It rejects the
declared appraisal charter but not every alternative classifier. Retaining
both routes simultaneously is a different design: the two cycles do not
commute and no common full-rank classifier exists. The independent reporting
shear is defective even though its eigenvalues are positive; its exact
nilpotent certificate must not be replaced by an unqualified numerical
eigenvalue check.

All analytic restrictions concern the full affine outcome space with ordered
and oriented appraisals. Tolerance 1e-12 is numerical, not statistical.
Material units and appraisal normalisation must be fixed before interpreting
condition numbers or residual magnitudes.

## Packages

The author-local manuscript source and PDF are intentionally not included in
the public code tree. A separate anonymous manuscript ZIP contains the single
main TeX file, Springer class and vector figures. The anonymous reproducibility
ZIP contains this README, code, tests, lock file and generated outputs.
Local editorial audits, author details and the cover letter are not reviewer
supplementary files.
