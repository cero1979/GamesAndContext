# Hostile-review audit

This checklist records objections that could materially affect correctness,
interpretation, or reproducibility. It is intentionally stricter than a normal
copy edit.

## Critical findings and disposition

| Finding | Risk | Disposition |
|---|---|---|
| The original repository contained only a 17-byte README. | No public reproducibility package. | Addressed on the revision branch with package, tests, CI, notebook, and results. |
| The notebook duplicated the model and was the only source of truth. | Hidden state and untestable theorem checks. | Addressed: logic moved to `src/context_games`; notebook imports it. |
| `run_all.py` rewrote the source notebook in place. | Reproduction creates unexplained diffs. | Addressed: executed notebook is written to an ignored result artifact. |
| The business malicious equilibrium depends on an exact payoff tie. | Central dynamic result can be mistaken for robust. | Addressed computationally; manuscript wording still requires revision. |
| The diagonal theorem conflates diagonal position with robust strict inequalities. | Overstated theorem. | Manuscript correction required: diagonal position is necessary, not sufficient. |
| The claimed radius `3/4` was described without making the open ball explicit. | Boundary counterexample. | Test added; manuscript must use `||Delta||_infinity < 3/4`. |
| The dynamic update was called logit-replicator and linked to quantal response. | Terminological and citation mismatch. | Rename to exponential replicator / multiplicative weights and cite appropriate primary literature. |
| A perturbation satisfying only `X(G,U)>X(P,U)` was used to claim global convergence. | False without restrictions on the other payoff entries. | Restrict claim to the one-coordinate perturbation family or add sufficient gap conditions. |
| Seven features encode only four profiles. | Saturated, non-identified representation can fit arbitrary payoffs. | State non-identification explicitly; do not present features as evidence against arbitrariness. |
| Means and standard deviations summarized a deterministic factorial grid. | Suggests a sampling interpretation. | Replaced in code by min-max ranges; manuscript table requires update. |
| The empirical protocol prescribed 30-60 participants without power analysis. | Methodologically indefensible generic sample size. | Remove fixed sample size; require preregistered estimand and power/precision analysis. |
| Abstract and keywords violate journal limits. | Desk-rejection risk. | Submission files and manuscript revision required. |
| Code/data were not deposited or cited. | Violates the journal's Option C research-data policy. | GitHub package prepared; archive DOI must be minted before submission. |

## Residual scientific risks

1. The formal results are elementary in several sections. The paper should lead
   with the configuration theorem and robustness distinction, and compress
   tautological partition/category material.
2. The benchmarks are constructed examples. Claims about real institutions must
   remain conditional and illustrative until calibrated data exist.
3. The current literature review is dated and does not yet position the dynamic
   rule or context-dependent preferences precisely enough.
4. An anonymous repository or archival release is still needed for review, with
   a persistent identifier added to the data-availability statement.
5. Author identities, affiliations, funding, CRediT roles, conflicts, and final AI
   disclosure require author input before submission.
