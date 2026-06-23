# Mathematical Social Sciences submission manifest

Checked against the journal's official [Guide for
Authors](https://www.sciencedirect.com/journal/mathematical-social-sciences/publish/guide-for-authors)
on 2026-06-22.

## Editorial Manager uploads

| Upload item | Repository file(s) | Status |
|---|---|---|
| Manuscript source | `manuscript/context_dependent_benefit_loss_games_v09.tex`, `manuscript/finite_game_results.tex`, `manuscript/feature_appendix.tex` | CAS double-column source with author, ORCID, affiliation, address, and email; telephone and declarations remain |
| Review PDF | `manuscript/context_dependent_benefit_loss_games_v09.pdf` | Generated from the sources |
| Highlights | `submission/highlights.txt` | Ready; five bullets, each at most 85 characters |
| Figure: strategy trajectories | `results/strategy_trajectories.pdf` | Ready; vector PDF |
| Figure: class masses | `results/class_masses.pdf` | Ready; vector PDF |
| Figure: payoff perturbations | `results/payoff_perturbation_robustness.pdf` | Ready; vector PDF |
| LaTeX-native figures | Embedded TikZ source in the main manuscript | Permitted as editable text graphics |
| Declaration of interests | Elsevier declarations-tool `.doc` or `.docx` | Author action required |
| Research data and software | Public repository plus versioned archival DOI | DOI required before submission |
| Graphical abstract | Not supplied | Optional |

## Source dependencies

The manuscript also requires `manuscript/cas-dc.cls`,
`manuscript/cas-common.sty`, and the CAS `manuscript/thumbnails/` assets, copied
without modification from the author-supplied Elsevier CAS 2.4 bundle, plus the
vector PDFs in `results/`. Tables are editable LaTeX and should not be uploaded
as images. The repository contains no third-party artwork requiring permission.
`CITATION.cff` supplies machine-readable author, ORCID, and repository metadata;
add the archival DOI when minted.

## Final human gate

Complete `title-page-information.txt` and `author-declarations-template.txt`, add
the archival DOI, confirm the AI disclosure, and ensure that metadata entered in
Editorial Manager exactly matches the manuscript.
