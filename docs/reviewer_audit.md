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
| The executed notebook regenerated figures under `matplotlib_inline`. | The notebook silently overwrote CLI figures with backend-dependent binaries. | Addressed: figure generation occurs once with `Agg`; publication figures are vector PDF, platform-dependent PNG duplicates were removed, and the notebook no longer overwrites artifacts. |
| Raw double-precision CSV output differed across platforms in the 16th decimal place. | Exact artifact verification failed despite numerically equivalent calculations. | Addressed: all CSV floats use a tested 12-significant-digit serialization while calculations remain double precision. |
| Package metadata claimed untested Python 3.11 compatibility while the archive used Python 3.12. | Users could expect support outside the validated environment. | Addressed: package metadata, `.python-version`, README, and SHA-pinned CI all specify CPython 3.12.13. |
| The main finite-game theorems appeared only after elementary partition and saturated feature sections. | Editors could miss the contribution or read the paper as an overextended taxonomy. | Addressed: a self-contained main-results section now follows the model immediately; benchmark analysis only applies it, and the non-identified feature layer is an appendix. |
| The manuscript could be read as claiming that context-dependent utility in games was new. | Direct conflict with social context games, relational utility, and category-dependent preference. | Addressed: the abstract, introduction, literature review, and conclusion expressly disclaim that priority claim and distinguish the Cipolla-specific comparative object. |
| Social context games and payoff-transformation characterizations were omitted. | A hostile referee could allege unacknowledged prior art. | Addressed: Ashlagi--Krysta--Tennenholtz and Tewolde--Conitzer are cited and compared at the level of primitives and preservation questions. |
| Class preservation and strategic preservation were juxtaposed but not jointly characterized. | The framework could look like renamed standard game theory. | Addressed: a new theorem proves that, within the opponent-contingent separable family, universal preservation of both structures is equivalent to strictly increasing transformations that fix zero; the affine corollary excludes offsets, and code tests both sides. |
| Immediate consequences of definitions were presented as lengthy propositions. | Poor contribution-to-length ratio amplified the triviality objection. | Addressed: partition, welfare, and boundary observations are compressed; theorem status is reserved for substantive preservation, radius, and configuration results. |

## Residual scientific risks

1. The contextual valuation primitive remains deliberately elementary. The paper
   now disclaims novelty for that primitive and locates its contribution in the
   joint class/incentive characterization, exact radii, and configuration theorem.
   An editor may still judge those results insufficiently deep.
2. The benchmarks are constructed examples. Claims about real institutions must
   remain conditional and illustrative until calibrated data exist.
3. The framework remains adjacent to social context games, norm-derived utility,
   strategic-equivalence transformations, and category-dependent preferences.
   The revised priority claim is narrower and explicit, but a systematic review
   cannot prove that no uncited paper studies the same Cipolla-specific combination.
4. An anonymous repository or archival release is still needed for review, with
   a persistent identifier added to the data-availability statement.
5. Author identities, affiliations, funding, CRediT roles, conflicts, and final AI
   disclosure require author input before submission.
