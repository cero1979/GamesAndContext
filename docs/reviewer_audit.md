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
| The business malicious equilibrium depends on an exact payoff tie. | Central dynamic result can be mistaken for robust. | Addressed: exact pure-NE radius is zero, the perturbation audit reports failure almost surely, and the dynamic claim is explicitly non-robust. |
| The diagonal theorem conflates diagonal position with robust strict inequalities. | Overstated theorem. | Addressed: sharing neither action is necessary; in `2x2` this means diagonal, while strict inequalities separately certify robust coexistence. |
| The claimed radius `3/4` was described without making the open ball explicit. | Boundary counterexample. | Addressed in theorem text and by tests below, at, and above the open-ball boundary. |
| The dynamic update was called logit-replicator and linked to quantal response. | Terminological and citation mismatch. | Addressed: renamed exponential replicator / multiplicative weights and tied to primary learning literature. |
| A perturbation satisfying only `X(G,U)>X(P,U)` was used to claim global convergence. | False without restrictions on the other payoff entries. | Addressed: the claim is restricted to the stated one-coordinate perturbation family. |
| Seven features encode only four profiles. | Saturated, non-identified representation can fit arbitrary payoffs. | Addressed: non-identification is explicit and the feature layer is described only as an auditable parameterization. |
| Means and standard deviations summarized a deterministic factorial grid. | Suggests a sampling interpretation. | Addressed: replaced by design extrema and labeled as non-inferential. |
| The empirical protocol prescribed 30-60 participants without power analysis. | Methodologically indefensible generic sample size. | Addressed: sample size must follow a preregistered estimand and power or precision analysis. |
| Abstract and keywords violate journal limits. | Desk-rejection risk. | Addressed: the abstract is below 250 words and seven keywords are supplied. |
| Code/data were not deposited or cited. | Violates the journal's Option C research-data policy. | GitHub package prepared; archive DOI must be minted before submission. |
| “Strategic stability” was used descriptively despite its technical refinement meaning. | Terminological confusion with Kohlberg--Mertens stability. | Addressed: title and claims use class robustness and equilibrium persistence; the distinction is explicit and primary sources are cited. |
| The exhaustive grid omitted zero payoffs and weak best-response ties. | Audit avoided class boundaries and an important source of degeneracy. | Addressed: all `5^8 = 390,625` games on `{-2,-1,0,1,2}` are enumerated. |
| Monte Carlo rates were the main evidence for payoff robustness. | A finite random sample cannot certify a neighborhood. | Addressed: exact class-map and pure-NE-set radii are derived and tested; simulation is retained only as a distribution-specific illustration. |
| The principal equilibrium results were stated only for `2x2` games. | Apparent dependence on the benchmark dimension weakens novelty and external mathematical scope. | Addressed: the exact pure-NE-set radius and configuration theorem now cover arbitrary finite two-player games; exhaustive `2x3` and `3x2` audits exercise the extension. |
| The executed notebook regenerated figures under `matplotlib_inline`. | The notebook silently overwrote CLI figures with backend-dependent binaries. | Addressed: figure generation occurs once in the tested CLI with the `Agg` backend; the notebook reads the archived rectangular audit and no longer overwrites artifacts. |

## Residual scientific risks

1. The formal results are elementary in several sections. The paper should lead
   with the configuration theorem and robustness distinction, and compress
   tautological partition/category material.
2. The benchmarks are constructed examples. Claims about real institutions must
   remain conditional and illustrative until calibrated data exist.
3. The framework remains adjacent to, rather than a replacement for, models that
   derive relational utility from norms or identify category-dependent preferences
   from stochastic choice; this boundary is now explicit and cites recent MSS work.
4. An anonymous repository or archival release is still needed for review, with
   a persistent identifier added to the data-availability statement.
5. Author identities, affiliations, funding, CRediT roles, conflicts, and final AI
   disclosure require author input before submission.
