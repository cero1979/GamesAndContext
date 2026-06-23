# MSS pre-submission checklist

Verified against the official [*Mathematical Social Sciences* Guide for
Authors](https://www.sciencedirect.com/journal/mathematical-social-sciences/publish/guide-for-authors)
on 2026-06-22.

## Complete

- Manuscript uses the official Elsevier CAS 2.4 `cas-dc` class in double-column,
  author-year mode; the exact class, support file, and CAS thumbnail assets are
  versioned locally.
- Title, author, ORCID, affiliation, abstract, and keywords use native CAS syntax.
- Manuscript is editable modular LaTeX and compiles without undefined references.
- Abstract is 198 words (maximum: 250).
- Seven English keywords are supplied (allowed: 1-7).
- Five highlights are supplied; every line is at most 85 characters.
- Citations and the alphabetized reference list use the journal's author-year style.
- Tables are editable, use `booktabs`, and contain no vertical rules.
- Every figure is cited and captioned; external figures are publication-quality
  vector PDF and LaTeX-native text graphics remain editable in the source.
- Sections and subsections are numbered; the appendix uses lettered numbering.
- Code, synthetic inputs, tests, notebook, and generated outputs are versioned.
- A data-and-code statement and an AI-assistance declaration are in the manuscript.
- The complete Python 3.12 environment is pinned and exercised by CI.
- `submission/submission-manifest.md` maps repository files to Editorial Manager
  upload items.

## Author action required before submission

- Confirm the author's preferred spelling and supply a direct telephone number.
  The name, ORCID, affiliation, postal address, and email are already present;
  MSS uses single-anonymized review.
- Add the CRediT contribution statement confirmed by the author.
- Add the funding statement and sponsor role, or the journal's no-funding statement.
- Complete Elsevier's declarations tool and upload its `.doc` or `.docx` output.
- Confirm and, if necessary, edit the Codex disclosure with the author.
- Select a repository license for code and manuscript materials; no legal license
  has been assumed on the authors' behalf.
- Create a versioned archival release (for example, Zenodo), mint a DOI, and replace
  the provisional GitHub-only wording in the data statement.
- Add the archival DOI to the existing `CITATION.cff`.
- Confirm that the author approves the public repository and any preprint posting.
- Upload each external figure as a separate source file.
- Run a final human spelling and grammar review after author metadata is inserted.

## Editorial risk still requiring scholarly judgment

- The benchmarks remain synthetic; no claim of external validity should be added.
- The editor may still judge the formal contribution too elementary. The revision
  therefore leads with a joint semantic/strategic preservation characterization,
  exact robustness radii, and the equilibrium-configuration theorem, while
  compressing definitional material and expressly delimiting prior art.
- A domain expert should independently check the proof and the literature review
  before submission; computational audits reduce but do not eliminate proof risk.
