"""Synthetic, theorem-directed stress tests for contextual comparability.

These calculations are not empirical estimates or exhaustive identified sets.
The independently specified institutional rules are deliberately stylised.
"""

from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np

from .contextual_classifier import (
    AffineContext,
    AffineMap,
    analyze_cycle,
    contextual_radius,
    finite_label_inequalities,
)

SEED = 20260911


def unit_row_matrix(angle_degrees: float) -> np.ndarray:
    """Two unit normals with a nondegenerate angle in (0, 180) degrees."""
    if not 0.0 < angle_degrees < 180.0:
        raise ValueError("angle_degrees must be strictly between 0 and 180")
    theta = np.deg2rad(angle_degrees)
    return np.array([[1.0, 0.0], [np.cos(theta), np.sin(theta)]])


def conditioning_formula(angle_degrees: float) -> tuple[float, float, float]:
    """Return |det|, sigma_min and kappa_2 without small-angle cancellation.

    AA^T has eigenvalues 1 +/- cos(theta). The half-angle evaluation
    avoids subtracting nearly equal floating-point values near collinearity.
    """
    unit_row_matrix(angle_degrees)
    theta = np.deg2rad(min(angle_degrees, 180.0 - angle_degrees))
    sigma_min = np.sqrt(2.0) * np.sin(theta / 2.0)
    sigma_max = np.sqrt(2.0) * np.cos(theta / 2.0)
    return float(np.sin(theta)), float(sigma_min), float(sigma_max / sigma_min)


def reference_error_bound(
    matrix: np.ndarray,
    reference: np.ndarray,
    delta_matrix: np.ndarray,
    delta_intercept: np.ndarray,
) -> float:
    """Euclidean absolute bound for (A+dA)^-1 (Ar+db) - r.

    Requires ||A^-1 dA||_2 < 1, a sufficient nonsingularity condition.
    """
    inverse = np.linalg.inv(matrix)
    q = float(np.linalg.norm(inverse @ delta_matrix, ord=2))
    if q >= 1.0:
        raise ValueError("the sufficient perturbation condition is not satisfied")
    return float(
        np.linalg.norm(inverse, ord=2)
        / (1.0 - q)
        * (
            np.linalg.norm(delta_intercept)
            + np.linalg.norm(delta_matrix, ord=2) * np.linalg.norm(reference)
        )
    )


def centred_score_bound(
    appraisal: np.ndarray,
    reference: np.ndarray,
    outcome: np.ndarray,
    delta_appraisal: np.ndarray,
    delta_reference: np.ndarray,
    *,
    norm: float = 2,
) -> float:
    """Finite parameter-error bound, including the second-order cross term."""
    dual = {1: np.inf, 2: 2, np.inf: 1}.get(norm)
    if dual is None:
        raise ValueError("norm must be 1, 2, or numpy.inf")
    delta_norm = np.linalg.norm(delta_appraisal, ord=dual)
    return float(
        delta_norm * np.linalg.norm(outcome - reference, ord=norm)
        + (np.linalg.norm(appraisal, ord=dual) + delta_norm)
        * np.linalg.norm(delta_reference, ord=norm)
    )


def running_example_rows() -> list[dict]:
    """Recompute every row of the submitted manuscript's running table."""
    context = AffineContext(np.array([[1, -1], [1, 1]]), np.array([1, 0]))
    rows = []
    for point, label in zip([(3, 0), (0, 2), (0, -2), (-1, 0)], "IHMD"):
        score = context.evaluate(point)
        rows.append(dict(x1=point[0], x2=point[1], e1=float(score[0]),
                         e2=float(score[1]), s1=int(np.sign(score[0])),
                         s2=int(np.sign(score[1])), legacy_label=label))
    return rows


def conditioning_rows() -> list[dict]:
    """Worst-direction intercept error with a fixed classification margin."""
    rows = []
    reference = np.array([1.0, 1.0])
    outcome = reference + np.array([2.0, 2.0])
    error_size = 1e-6
    for angle in (90.0, 30.0, 10.0, 1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001):
        matrix = unit_row_matrix(angle)
        left, singular, _ = np.linalg.svd(matrix)
        delta_intercept = error_size * left[:, -1]
        intercept = matrix @ reference
        recovered = np.linalg.solve(matrix, intercept + delta_intercept)
        det, sigma, condition = conditioning_formula(angle)
        bound = reference_error_bound(matrix, reference, np.zeros((2, 2)), delta_intercept)
        rows.append(dict(angle_degrees=angle, abs_determinant=det,
                         sigma_min=sigma, condition_number=condition,
                         intercept_error_norm=error_size,
                         reference_error=float(np.linalg.norm(recovered - reference)),
                         reference_error_bound=bound,
                         outcome_margin=contextual_radius(AffineContext(matrix, reference), outcome),
                         relative_formula_error=float(abs(sigma - singular[-1]) / singular[-1])))
    return rows


def strict_label_grid() -> tuple[list[dict], list[dict]]:
    """Finite candidate-grid diagnostics, not the complete identified set.

    Normalisation fixes ||a||_2=1. The grid contains the true parameters.
    Nested strict-labelled samples narrow the candidate set but do not
    identify a continuous parameter exactly, even if one grid point remains.
    """
    deviations = np.array([
        [-2, -1], [-1, -2], [2, 1], [1, 2],
        [1.5, -1], [-1.5, 1], [1, -1.5], [-1, 1.5],
        [1, -.9], [-1, .9], [.9, -1], [-.9, 1],
        [1, -.99], [-1, .99], [.99, -1], [-.99, 1],
    ])
    points = deviations + np.array([1.0, 1.0])
    true_appraisal = np.array([1.0, 1.0]) / np.sqrt(2.0)
    true_intercept = np.sqrt(2.0)
    labels = np.sign(deviations @ true_appraisal).astype(int)
    angles = np.linspace(-45.0, 135.0, 361)
    intercept_offsets = np.linspace(-1.0, 1.0, 101)
    phi, offset = np.meshgrid(angles, intercept_offsets, indexing="ij")
    parameters = np.column_stack((np.cos(np.deg2rad(phi.ravel())),
                                  np.sin(np.deg2rad(phi.ravel())),
                                  true_intercept + offset.ravel()))
    summaries, candidates = [], []
    for size in (4, 8, 12, 16):
        constraints = finite_label_inequalities(points[:size], labels[:size])
        feasible = np.all(constraints @ parameters.T > 1e-12, axis=0)
        selected_angles = phi.ravel()[feasible]
        selected_offsets = offset.ravel()[feasible]
        # An explicit open parameter ball gives a continuous, off-grid witness.
        theta = np.r_[true_appraisal, true_intercept]
        slacks = constraints @ theta
        radius = float(np.min(slacks) / (2 * np.max(np.linalg.norm(constraints, axis=1))))
        nearby_angle = np.pi / 4 + radius / 2
        nearby = np.array([np.cos(nearby_angle), np.sin(nearby_angle), true_intercept])
        nearby_slack = float(np.min(constraints @ nearby))
        summaries.append(dict(n_labels=size, grid_total=len(parameters),
                              feasible_grid_candidates=int(feasible.sum()),
                              angle_min=float(selected_angles.min()),
                              angle_max=float(selected_angles.max()),
                              intercept_offset_min=float(selected_offsets.min()),
                              intercept_offset_max=float(selected_offsets.max()),
                              certified_open_ball_radius=radius,
                              distinct_normalised_witness_angle_degrees=float(np.rad2deg(nearby_angle)),
                              witness_minimum_strict_slack=nearby_slack))
        for angle, b_offset in zip(selected_angles, selected_offsets):
            candidates.append(dict(n_labels=size, angle_degrees=float(angle),
                                   intercept_offset=float(b_offset)))
    return summaries, candidates


def nilpotent_shear_certificate(epsilon: Fraction = Fraction(1, 20)) -> dict:
    """Exact rational Jordan obstruction for K=I+epsilon [[1,1],[-1,-1]]."""
    nilpotent = [[epsilon, epsilon], [-epsilon, -epsilon]]
    square = [[sum(nilpotent[i][k] * nilpotent[k][j] for k in range(2))
               for j in range(2)] for i in range(2)]
    nonzero = any(value != 0 for row in nilpotent for value in row)
    square_zero = all(value == 0 for row in square for value in row)
    return dict(epsilon=str(epsilon), nilpotent_nonzero=nonzero,
                nilpotent_square_zero=square_zero,
                minimal_polynomial="(z-1)^2" if nonzero else "z-1",
                any_full_rank_classifier_possible=not (nonzero and square_zero))


def institutional_case(epsilon: float = 0.05) -> tuple[dict, list[dict]]:
    """Rules act on baseline-centred resource deviations, not fitted labels."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive to construct a strict witness")
    appraisal = np.array([[1.0, 1.0], [-1.0, 1.0]])
    references = [np.array([1.0, 1.0]), np.array([2.0, 1.0]), np.array([2.0, 2.0])]
    contexts = [AffineContext(appraisal, reference) for reference in references]
    funding = np.array([[1.5, .5], [.5, 1.5]])
    redistribution = np.array([[.75, .25], [.25, .75]])
    shift = np.array([[1.0, 1.0], [-1.0, -1.0]])

    def centred_map(matrix: np.ndarray, source: int, target: int) -> AffineMap:
        return AffineMap(matrix, references[target] - matrix @ references[source])

    ab = centred_map(funding, 0, 1)
    bc = centred_map(redistribution, 1, 2)
    bc_perturbed = centred_map(redistribution + epsilon * shift, 1, 2)
    ca = centred_map(np.eye(2), 2, 0)
    coherent = ca.compose(bc).compose(ab)
    perturbed = ca.compose(bc_perturbed).compose(ab)
    source_point = references[1] + np.linalg.solve(appraisal, [1.0, epsilon])
    cycle_point = ab.inverse()(source_point)
    inverse_appraisal = np.linalg.inv(appraisal)
    rows = []
    for name, source, target, transport, point in (
        ("Funding", 0, 1, ab, cycle_point),
        ("Redistribution", 1, 2, bc, source_point),
        ("Altered redistribution", 1, 2, bc_perturbed, source_point),
        ("Coherent intervention cycle", 0, 0, coherent, cycle_point),
        ("Altered intervention cycle", 0, 0, perturbed, cycle_point),
    ):
        multiplier = appraisal @ transport.linear @ inverse_appraisal
        residual = float(np.linalg.norm(multiplier - np.diag(np.diag(multiplier)), ord="fro"))
        before = contexts[source].evaluate(point)
        after = contexts[target].evaluate(transport(point))
        rows.append(dict(scenario=name, off_diagonal_residual=residual,
                         reference_residual=float(np.linalg.norm(transport(references[source]) - references[target])),
                         before_1=float(before[0]), before_2=float(before[1]),
                         after_1=float(after[0]), after_2=float(after[1]),
                         same_signature=bool(np.array_equal(np.sign(before), np.sign(after)))))
    details = dict(
        synthetic=True, epsilon=epsilon,
        coordinate_units="fixed calibrated thousands of common monetised net-resource units",
        coordinate_meanings=["implementing institution", "affected population"],
        appraisal_meanings=["aggregate surplus", "population-minus-institution surplus"],
        appraisal_matrix=appraisal.tolist(), references=[r.tolist() for r in references],
        funding_matrix=funding.tolist(), redistribution_matrix=redistribution.tolist(),
        altered_redistribution_matrix=bc_perturbed.linear.tolist(),
        witness_at_B=source_point.tolist(), witness_at_A=cycle_point.tolist(),
        coherent_cycle_linear=coherent.linear.tolist(), coherent_cycle_offset=coherent.offset.tolist(),
        altered_cycle_linear=perturbed.linear.tolist(), altered_cycle_offset=perturbed.offset.tolist(),
        coherent_cycle_any_classifier_admissible=analyze_cycle(coherent).admissible,
        altered_cycle_any_classifier_admissible=analyze_cycle(perturbed).admissible,
        coherent_reference=analyze_cycle(coherent).reference.tolist(),
        warning="Altered intervention rejects declared appraisals, not every possible appraisal frame.",
        separate_reporting_cycle=nilpotent_shear_certificate(),
    )
    return details, rows


def robustness_rows() -> list[dict]:
    appraisal = np.array([[1.0, 1.0], [-1.0, 1.0]])
    reference = np.array([1.0, 1.0])
    outcome = np.array([1.225, 1.275])
    delta_reference = np.array([.001, -.001])
    delta_appraisal = np.array([[.002, -.001], [.001, .002]])
    rows = []
    for k in range(2):
        row, delta_row = appraisal[k], delta_appraisal[k]
        before = float(row @ (outcome - reference))
        after = float((row + delta_row) @ (outcome - reference - delta_reference))
        bound = centred_score_bound(row, reference, outcome, delta_row, delta_reference)
        rows.append(dict(appraisal=k + 1, original_score=before, perturbed_score=after,
                         absolute_score_change=abs(after - before), centred_bound=bound,
                         sign_certified=bool(bound < abs(before)),
                         euclidean_outcome_margin=abs(before) / float(np.linalg.norm(row))))
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _num(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) >= 1e4 or abs(value) < 1e-3:
        base, exponent = f"{value:.3e}".split("e")
        return rf"{base}\times 10^{{{int(exponent)}}}"
    return f"{value:.4g}"


def _table(path: Path, columns: str, header: str, body: list[str], caption: str, label: str) -> None:
    text = ("% Generated by scripts/run_qq_audit.py; do not edit by hand.\n"
            "\\begin{table}[tbp]\n\\centering\n\\small\n\\setlength{\\tabcolsep}{4pt}\n"
            f"\\begin{{tabular}}{{{columns}}}\n\\toprule\n{header}\\\\\n\\midrule\n"
            + "\\\\\n".join(body) + "\\\\\n\\bottomrule\n\\end{tabular}\n"
            + f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\end{{table}}\n")
    path.write_text(text, encoding="utf-8")


def generate(output: Path) -> dict:
    """Generate CSV, TeX, vector figures and content-hashed provenance."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output.mkdir(parents=True, exist_ok=True)
    running = running_example_rows()
    conditioning = conditioning_rows()
    identification, candidates = strict_label_grid()
    case, transports = institutional_case()
    robustness = robustness_rows()
    datasets = dict(running_labels=running, conditioning=conditioning,
                    strict_label_identification=identification,
                    strict_label_grid_candidates=candidates,
                    institutional_transport=transports, centred_robustness=robustness)
    for name, rows in datasets.items():
        _write_csv(output / f"{name}.csv", rows)
    (output / "institutional_case.json").write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")

    _table(output / "table_running_labels.tex", "cccc",
           r"Outcome \(x\) & \(E_C(x)\) & Signature & Legacy class",
           [rf"\(({r['x1']},{r['x2']})\) & \(({r['e1']:g},{r['e2']:g})\) & "
            rf"\(({'+' if r['s1'] > 0 else '-'},{'+' if r['s2'] > 0 else '-'})\) & \({r['legacy_label']}\)" for r in running],
           "Recomputed running-example outcomes; the names are legacy labels, not types of people.",
           "tab:running-labels")
    selected = [r for r in conditioning if r["angle_degrees"] in (90, 10, 1, .1, .001, .00001)]
    _table(output / "table_conditioning.tex", "rrrrr",
           r"\(\theta\) (degrees) & \(|\det A|\) & \(\kappa_2(A)\) & \(\|\Delta r\|_2\) & \(\rho_C(x)\)",
           [" & ".join(rf"\({_num(r[k])}\)" for k in
                       ("angle_degrees", "abs_determinant", "condition_number", "reference_error", "outcome_margin")) for r in selected],
           r"Synthetic identification stress test. Rows of \(A\) have unit norm; \(r=(1,1)\), \(x=r+(2,2)\). An intercept perturbation of norm \(10^{-6}\) is aligned with the least left singular direction, so the recovery error attains \(10^{-6}/\sigma_{\min}(A)\) up to round-off. A large fixed-outcome margin does not ensure stable reference recovery.",
           "tab:qq-conditioning")
    _table(output / "table_strict_identification.tex", "rrrrr",
           r"Labels & \shortstack{Grid\\candidates} & \shortstack{Angle range\\(degrees)} & \shortstack{Intercept\\offset range} & \shortstack{Off-grid\\slack}",
           [rf"{r['n_labels']} & {r['feasible_grid_candidates']} & "
            rf"\([{r['angle_min']:g},{r['angle_max']:g}]\) & "
            rf"\([{r['intercept_offset_min']:.2f},{r['intercept_offset_max']:.2f}]\) & "
            rf"\({_num(r['witness_minimum_strict_slack'])}\)" for r in identification],
           r"Synthetic strict-label identification on a fixed grid of 36,461 normalised candidates. Angles have spacing \(0.5\) degrees and intercept offsets spacing \(0.02\). Reported ranges concern surviving grid candidates, not the complete continuous identified set. A distinct normalised off-grid candidate has positive strict slack in every row, including when only one grid candidate survives.",
           "tab:qq-identification")
    _table(output / "table_institutional_transport.tex", "lrrr",
           r"Rule or cycle & \shortstack{Off-diagonal\\residual} & \shortstack{Initial\\second score} & \shortstack{Final\\second score}",
           [rf"{r['scenario']} & \({_num(r['off_diagonal_residual'])}\) & "
            rf"\({_num(r['before_2'])}\) & \({_num(r['after_2'])}\)" for r in transports],
           r"Synthetic institutional rules with \(\varepsilon=0.05\). Residual is \(\|R-\operatorname{diag}(R)\|_F\), \(R=A_DBA_C^{-1}\), in the fixed appraisal scales. The first score is positive throughout. Alteration replaces redistribution: it reverses the second sign for the declared classifier, without excluding every alternative frame.",
           "tab:qq-transports")
    _table(output / "table_centred_robustness.tex", "rrrrr",
           r"Appraisal & Original score & Score change & Centred bound & Outcome margin",
           [rf"{r['appraisal']} & " + " & ".join(rf"\({_num(r[k])}\)" for k in
            ("original_score", "absolute_score_change", "centred_bound", "euclidean_outcome_margin")) for r in robustness],
           r"Synthetic finite-perturbation audit at \(x=(1.225,1.275)\), \(r=(1,1)\), with \(\Delta r=(0.001,-0.001)\), \(\Delta a_1=(0.002,-0.001)\), and \(\Delta a_2=(0.001,0.002)\). Both bounds, including the cross term, are smaller than the corresponding absolute original score and therefore certify sign preservation.",
           "tab:qq-robustness")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "pdf.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.bbox": "tight"})
    angles = np.geomspace(1e-5, 90, 350)
    formulas = np.array([conditioning_formula(t) for t in angles])
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.0), constrained_layout=True)
    axes[0].loglog(angles, formulas[:, 2], color="#24577A")
    axes[0].set(xlabel="Angle between unit normals (degrees)", ylabel="Euclidean condition number", title="A. Boundary geometry")
    axes[1].loglog(angles, 1e-6 / formulas[:, 1], color="#A0412C", label="Worst-direction reference error")
    axes[1].axhline(2, color="#24577A", linestyle="--", label="Fixed-outcome margin = 2")
    axes[1].set(xlabel="Angle between unit normals (degrees)", ylabel="Euclidean distance", title="B. Small intercept error, unstable reference")
    axes[1].legend(fontsize=7, loc="lower left")
    for ax in axes:
        ax.grid(True, which="major", alpha=.2)
    fig.savefig(output / "figure_qq_conditioning.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.0, 3.6), constrained_layout=True)
    for size, color in zip((4, 8, 12, 16), ("#D5DCE1", "#7598B2", "#24577A", "#A0412C")):
        records = [r for r in candidates if r["n_labels"] == size]
        ax.scatter([r["angle_degrees"] for r in records], [r["intercept_offset"] for r in records],
                   s=8 if size < 16 else 25, color=color, linewidths=0, label=f"{size} strict labels")
    ax.set(xlabel="Normalised appraisal angle (degrees)", ylabel="Intercept offset from true value", title="Synthetic candidate grids, not continuous identified sets")
    ax.legend(fontsize=8)
    fig.savefig(output / "figure_qq_identified_sets.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)

    root = Path(__file__).resolve().parents[2]
    source_paths = sorted((root / "src/context_games").glob("*.py"))
    source_paths += sorted((root / "tests").glob("test_*.py"))
    source_paths += [root / "scripts/run_qq_audit.py", root / "requirements-qq-lock.txt"]
    provenance = dict(
        description="Deterministic synthetic theorem-directed stress tests, not empirical data",
        seed=SEED, random_generation_used=False,
        seed_note="Reserved fixed seed; current published designs are deterministic and use no random draws.",
        python=platform.python_version(),
        packages={name: importlib.metadata.version(name) for name in ("numpy", "matplotlib", "pandas")},
        tolerance=1e-12,
        exact_certificate="The reporting-cycle Jordan obstruction uses fractions.Fraction, not floating eigenvalue multiplicity.",
        source_sha256={str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        outputs_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(output.iterdir()) if p.is_file() and p.name != "provenance.json"},
        reproduction_command="python scripts/run_qq_audit.py --output-dir results/qq",
        warnings=["Finite candidate grids do not exhaust continuous identified sets.",
                  "Intervention cycles can be nonidentity while preserving signs; pure coordinate recoding must be path independent.",
                  "A residual is not a statistical significance test or an empirical estimate."],
    )
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("results/qq"))
    args = parser.parse_args()
    provenance = generate(args.output_dir)
    print(f"Generated {len(provenance['outputs_sha256'])} synthetic audit artifacts in {args.output_dir}")


if __name__ == "__main__":
    main()
