"""Deterministic experiments and computational theorem audits."""

from __future__ import annotations

import itertools
from collections.abc import Iterable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .benchmarks import BENCHMARKS, CONTEXTS, PROFILES
from .contextual_classifier import (
    AffineContext,
    AffineMap,
    analyze_cycle,
    contextual_radius,
    finite_label_inequalities,
    finite_label_slacks,
    transport_identity_error,
)
from .model import (
    ContextGame,
    axis_margin,
    class_map_robustness_radius,
    equilibrium_set_robustness_radius,
    perturbed_game,
    simulate,
    structural_sensitivity,
    trajectory_distance,
)

DEFAULT_SEED = 20260622
PDF_METADATA = {"Creator": "context_games 0.10.0", "CreationDate": None, "ModDate": None}
CSV_FLOAT_FORMAT = "%.12g"
AUDIT_ZERO_TOLERANCE = 1e-12


def _certified_zero(value: float, *, tolerance: float = AUDIT_ZERO_TOLERANCE) -> float:
    """Normalize platform-level residuals after an explicit tolerance check."""
    return 0.0 if abs(value) <= tolerance else value


def _write_result_csv(table: pd.DataFrame, path: Path, *, index: bool = False) -> None:
    """Serialize reported numbers independently of last-bit libm differences."""
    table.to_csv(
        path,
        index=index,
        float_format=CSV_FLOAT_FORMAT,
        lineterminator="\n",
    )


def baseline_tables() -> dict[str, pd.DataFrame]:
    payoff_rows = []
    class_rows = []
    margin_rows = []
    equilibrium_rows = []
    final_rows = []
    for profile in PROFILES:
        payoff_rows.append({"profile": str(profile), **{c: BENCHMARKS[c].payoffs[profile] for c in CONTEXTS}})
        class_rows.append({"profile": str(profile), **{c: BENCHMARKS[c].classes()[profile] for c in CONTEXTS}})
        margin_rows.append({"profile": str(profile), **{c: axis_margin(BENCHMARKS[c].payoffs[profile]) for c in CONTEXTS}})
    for key in CONTEXTS:
        game = BENCHMARKS[key]
        equilibrium_rows.append({"context": key, "pure_nash": ";".join(map(str, game.pure_nash()))})
        trajectory = simulate(game)
        p, q = (float(v) for v in trajectory.iloc[-1][["p", "q"]])
        masses = game.class_masses(p, q)
        final_rows.append(
            {
                "context": key,
                "p50": p,
                "q50": q,
                "E50_W": game.expected_welfare(p, q),
                **{f"Pr50_{c}": masses[c] for c in ("I", "H", "M", "D", "boundary")},
            }
        )
    sensitivity = pd.DataFrame(index=CONTEXTS, columns=CONTEXTS, dtype=float)
    distance = pd.DataFrame(index=CONTEXTS, columns=CONTEXTS, dtype=float)
    for first in CONTEXTS:
        for second in CONTEXTS:
            sensitivity.loc[first, second] = structural_sensitivity(BENCHMARKS[first], BENCHMARKS[second])
            distance.loc[first, second] = trajectory_distance(BENCHMARKS[first], BENCHMARKS[second])
    return {
        "payoff_table": pd.DataFrame(payoff_rows),
        "class_table": pd.DataFrame(class_rows),
        "axis_margins": pd.DataFrame(margin_rows),
        "pure_nash": pd.DataFrame(equilibrium_rows),
        "final_values": pd.DataFrame(final_rows),
        "structural_sensitivity": sensitivity,
        "dynamic_trajectory_distances": distance,
    }


def sensitivity_grid(horizon: int = 50) -> pd.DataFrame:
    eta_grid = (0.05, 0.15, 0.45, 1.0, 1.5)
    initial_grid = ((0.2, 0.2), (0.2, 0.8), (0.5, 0.5), (0.8, 0.2), (0.8, 0.8))
    rows = []
    for key in CONTEXTS:
        game = BENCHMARKS[key]
        for eta in eta_grid:
            for p0, q0 in initial_grid:
                trajectory = simulate(game, p0=p0, q0=q0, eta=eta, horizon=horizon)
                p, q = (float(v) for v in trajectory.iloc[-1][["p", "q"]])
                masses = game.class_masses(p, q)
                rows.append(
                    {
                        "context": key,
                        "eta": eta,
                        "p0": p0,
                        "q0": q0,
                        f"p{horizon}": p,
                        f"q{horizon}": q,
                        f"E{horizon}_W": game.expected_welfare(p, q),
                        **{f"Pr{horizon}_{c}": masses[c] for c in ("I", "H", "M", "D")},
                    }
                )
    return pd.DataFrame(rows)


def sensitivity_grid_summary(detail: pd.DataFrame, horizon: int = 50) -> pd.DataFrame:
    """Summarize a deterministic design by extrema, not sampling statistics."""
    columns = (f"p{horizon}", f"q{horizon}", f"E{horizon}_W", f"Pr{horizon}_I", f"Pr{horizon}_M", f"Pr{horizon}_D")
    rows = []
    for key in CONTEXTS:
        subset = detail[detail.context == key]
        row: dict[str, str] = {"context": key}
        for column in columns:
            row[f"{column}_range"] = f"[{subset[column].min():.6f}, {subset[column].max():.6f}]"
        rows.append(row)
    return pd.DataFrame(rows)


def convergence_diagnostics() -> pd.DataFrame:
    rows = []
    for key in CONTEXTS:
        game = BENCHMARKS[key]
        previous: tuple[float, float] | None = None
        for horizon in (25, 50, 100, 200, 500):
            trajectory = simulate(game, horizon=horizon)
            p, q = (float(v) for v in trajectory.iloc[-1][["p", "q"]])
            next_state = simulate(game, p0=p, q0=q, horizon=1).iloc[-1]
            rows.append(
                {
                    "context": key,
                    "horizon": horizon,
                    "p": p,
                    "q": q,
                    "step_residual": max(abs(float(next_state.p) - p), abs(float(next_state.q) - q)),
                    "change_from_previous_horizon": np.nan if previous is None else max(abs(p - previous[0]), abs(q - previous[1])),
                }
            )
            previous = (p, q)
    return pd.DataFrame(rows)


def perturbation_audit(draws: int = 2000, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Audit class and equilibrium claims under continuous payoff perturbations."""
    rng = np.random.default_rng(seed)
    rows = []
    for key in CONTEXTS:
        game = BENCHMARKS[key]
        original_classes = game.classes()
        original_ne = set(game.pure_nash())
        for radius in (0.25, 0.50, 0.75, 0.99, 1.01, 1.50):
            class_preserved = 0
            equilibrium_set_preserved = 0
            malicious_ne_present = 0
            coexisting_intelligent_malicious_ne = 0
            for perturbation in rng.uniform(-radius, radius, size=(draws, 8)):
                perturbed = perturbed_game(game, perturbation)
                classes = perturbed.classes()
                equilibria = set(perturbed.pure_nash())
                class_preserved += classes == original_classes
                equilibrium_set_preserved += equilibria == original_ne
                malicious = {profile for profile in equilibria if classes[profile] == "M"}
                intelligent = {profile for profile in equilibria if classes[profile] == "I"}
                malicious_ne_present += bool(malicious)
                coexisting_intelligent_malicious_ne += bool(malicious and intelligent)
            rows.append(
                {
                    "context": key,
                    "radius": radius,
                    "draws": draws,
                    "seed": seed,
                    "class_map_preserved_rate": class_preserved / draws,
                    "equilibrium_set_preserved_rate": equilibrium_set_preserved / draws,
                    "malicious_ne_rate": malicious_ne_present / draws,
                    "coexisting_I_M_ne_rate": coexisting_intelligent_malicious_ne / draws,
                }
            )
    return pd.DataFrame(rows)


def robustness_radii() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "context": key,
                "class_map_radius": class_map_robustness_radius(BENCHMARKS[key]),
                "pure_nash_set_radius": equilibrium_set_robustness_radius(BENCHMARKS[key]),
            }
            for key in CONTEXTS
        ]
    )


def contextual_classifier_audit() -> pd.DataFrame:
    """Closed-form checks for the contextual representation theorems."""
    first = AffineContext(
        np.asarray([[1.0, 0.25], [-0.2, 1.0]]),
        np.asarray([0.5, -1.0]),
    )
    second = AffineContext(
        np.asarray([[0.8, -0.1], [0.3, 1.2]]),
        np.asarray([-0.25, 0.75]),
    )
    third = AffineContext(
        np.asarray([[1.1, 0.4], [-0.3, 0.9]]),
        np.asarray([1.25, 0.2]),
    )
    first_scale = np.diag([2.0, 3.0])
    second_scale = np.diag([0.5, 4.0])
    first_transport = first.transport_to(second, first_scale)
    second_transport = second.transport_to(third, second_scale)
    composite = second_transport.compose(first_transport)
    direct = first.transport_to(third, second_scale @ first_scale)

    identifying_context = AffineContext(
        np.asarray([[1.0, 1.0], [1.0, -1.0]]),
        np.asarray([0.5, -0.25]),
    )
    identifying_cycle = identifying_context.transport_to(
        identifying_context, np.diag([2.0, 3.0])
    )
    identifying_analysis = analyze_cycle(identifying_cycle)
    rotation_analysis = analyze_cycle(
        AffineMap(np.asarray([[0.0, -1.0], [1.0, 0.0]]), np.zeros(2))
    )

    radius_context = AffineContext(
        np.asarray([[1.0, -1.0], [1.0, 1.0]]),
        np.zeros(2),
    )
    radius_error = abs(
        contextual_radius(radius_context, np.asarray([3.0, 1.0]), norm=2)
        - np.sqrt(2.0)
    )

    outcomes = np.asarray(
        [[2.0, 1.0], [-1.0, 2.0], [2.0, -3.0], [-2.0, -2.0]]
    )
    labels = np.sign(outcomes[:, 0]).astype(int)
    constraints = finite_label_inequalities(outcomes, labels)
    minimum_slack = float(
        np.min(finite_label_slacks(constraints, np.asarray([1.01, 0.001, 0.001])))
    )
    reference_error = (
        np.inf
        if identifying_analysis.reference is None
        else float(
            np.max(
                np.abs(
                    identifying_analysis.reference
                    - identifying_context.reference
                )
            )
        )
    )

    rows = [
        {
            "audit": "exact_transport_identity",
            "theorem": "transport",
            "value": _certified_zero(
                transport_identity_error(
                    first, second, first_transport, first_scale
                )
            ),
            "relation": "<=",
            "threshold": AUDIT_ZERO_TOLERANCE,
        },
        {
            "audit": "transport_composition",
            "theorem": "groupoid",
            "value": _certified_zero(
                float(
                    max(
                        np.max(np.abs(composite.linear - direct.linear)),
                        np.max(np.abs(composite.offset - direct.offset)),
                    )
                )
            ),
            "relation": "<=",
            "threshold": AUDIT_ZERO_TOLERANCE,
        },
        {
            "audit": "rotation_cycle_obstruction",
            "theorem": "holonomy",
            "value": float(rotation_analysis.admissible),
            "relation": "==",
            "threshold": 0.0,
        },
        {
            "audit": "cycle_reference_recovery",
            "theorem": "cycle_identification",
            "value": _certified_zero(reference_error),
            "relation": "<=",
            "threshold": AUDIT_ZERO_TOLERANCE,
        },
        {
            "audit": "euclidean_margin_sharp_value",
            "theorem": "robustness",
            "value": _certified_zero(radius_error),
            "relation": "<=",
            "threshold": AUDIT_ZERO_TOLERANCE,
        },
        {
            "audit": "finite_label_open_slack",
            "theorem": "set_identification",
            "value": minimum_slack,
            "relation": ">",
            "threshold": 0.0,
        },
    ]
    result = pd.DataFrame(rows)
    result["passed"] = [
        row.value <= row.threshold
        if row.relation == "<="
        else row.value > row.threshold
        if row.relation == ">"
        else row.value == row.threshold
        for row in result.itertuples()
    ]
    return result


def context_path_events() -> pd.DataFrame:
    """Exact transversal events for a moving-reference benchmark."""
    outcomes = {
        "left": np.asarray([-1.0, 1.0]),
        "middle": np.asarray([0.5, -1.0]),
        "right": np.asarray([2.0, 1.0]),
    }
    return pd.DataFrame(
        [
            {
                "outcome": label,
                "appraisal": 1,
                "crossing_t": float(outcome[0]),
                "score_derivative": -1.0,
                "transversal": True,
            }
            for label, outcome in outcomes.items()
        ]
    )


def _configuration_counts(games: Iterable[ContextGame]) -> dict[str, int]:
    counts = {
        "games": 0,
        "I_M_equilibrium_pairs": 0,
        "shared_actor_action_pairs": 0,
        "shared_affected_action_pairs": 0,
        "shared_affected_action_dominance_failures": 0,
        "disjoint_action_pairs": 0,
        "strict_disjoint_welfare_dominated_pairs": 0,
    }
    for game in games:
        counts["games"] += 1
        equilibria = game.pure_nash()
        classes = game.classes()
        strict_equilibria: set[tuple[str, str]] | None = None
        for first, second in itertools.combinations(equilibria, 2):
            if {classes[first], classes[second]} != {"I", "M"}:
                continue
            counts["I_M_equilibrium_pairs"] += 1
            intelligent = first if classes[first] == "I" else second
            malicious = second if intelligent == first else first
            if intelligent[0] == malicious[0]:
                counts["shared_actor_action_pairs"] += 1
            elif intelligent[1] == malicious[1]:
                counts["shared_affected_action_pairs"] += 1
                if not (
                    game.pareto_dominates(intelligent, malicious)
                    and game.welfare(intelligent) > game.welfare(malicious)
                ):
                    counts["shared_affected_action_dominance_failures"] += 1
            else:
                counts["disjoint_action_pairs"] += 1
                if strict_equilibria is None:
                    strict_equilibria = set(game.pure_nash(strict=True))
                if (
                    intelligent in strict_equilibria
                    and malicious in strict_equilibria
                    and game.welfare(intelligent) > game.welfare(malicious)
                ):
                    counts["strict_disjoint_welfare_dominated_pairs"] += 1
    return counts


def exhaustive_configuration_audit(values: tuple[int, ...] = (-2, -1, 0, 1, 2)) -> pd.DataFrame:
    """Exhaustively check the 2x2 theorem on a 390,625-game integer grid."""
    def games() -> Iterable[ContextGame]:
        for coordinates in itertools.product(values, repeat=8):
            payoffs = {
                profile: (float(coordinates[2 * i]), float(coordinates[2 * i + 1]))
                for i, profile in enumerate(PROFILES)
            }
            yield ContextGame("grid", "grid", ("G", "P"), ("U", "R"), payoffs)

    generic = _configuration_counts(games())
    return pd.DataFrame(
        [
            {
                "payoff_values": "[" + ";".join(map(str, values)) + "]",
                "games": generic["games"],
                "I_M_equilibrium_pairs": generic["I_M_equilibrium_pairs"],
                "shared_row_pairs": generic["shared_actor_action_pairs"],
                "shared_column_pairs": generic["shared_affected_action_pairs"],
                "shared_column_dominance_failures": generic[
                    "shared_affected_action_dominance_failures"
                ],
                "diagonal_pairs": generic["disjoint_action_pairs"],
                "strict_diagonal_welfare_dominated_pairs": generic[
                    "strict_disjoint_welfare_dominated_pairs"
                ],
            }
        ]
    )


def exhaustive_dichotomy_audit(values: tuple[int, ...] = (-2, -1, 0, 1, 2)) -> pd.DataFrame:
    """Compatibility wrapper for the legacy audit name."""
    return exhaustive_configuration_audit(values)


def rectangular_configuration_audit(
    values: tuple[int, ...] = (-2, -1, 1),
    shapes: tuple[tuple[int, int], ...] = ((2, 3), (3, 2)),
) -> pd.DataFrame:
    """Check the finite-game configuration theorem beyond the 2x2 benchmark."""
    rows = []
    for row_count, column_count in shapes:
        row_actions = tuple(f"r{i}" for i in range(row_count))
        column_actions = tuple(f"c{j}" for j in range(column_count))
        profiles = tuple(itertools.product(row_actions, column_actions))

        def games() -> Iterable[ContextGame]:
            for coordinates in itertools.product(values, repeat=2 * len(profiles)):
                payoffs = {
                    profile: (float(coordinates[2 * i]), float(coordinates[2 * i + 1]))
                    for i, profile in enumerate(profiles)
                }
                yield ContextGame(
                    "rectangular-grid",
                    "rectangular grid",
                    row_actions,
                    column_actions,
                    payoffs,
                )

        rows.append(
            {
                "shape": f"{row_count}x{column_count}",
                "payoff_values": "[" + ";".join(map(str, values)) + "]",
                **_configuration_counts(games()),
            }
        )
    return pd.DataFrame(rows)


def make_figures(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for key in CONTEXTS:
        trajectory = simulate(BENCHMARKS[key])
        axes[0].plot(trajectory.t, trajectory.p, label=BENCHMARKS[key].label)
        axes[1].plot(trajectory.t, trajectory.q, label=BENCHMARKS[key].label)
    axes[0].set_title("Probability of constructive guidance G")
    axes[1].set_title("Probability of engaged uptake U")
    for axis in axes:
        axis.set_xlabel("Iteration")
        axis.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("Probability")
    axes[1].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "strategy_trajectories.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    for axis, key in zip(axes, CONTEXTS):
        game = BENCHMARKS[key]
        trajectory = simulate(game)
        masses = pd.DataFrame([{"t": int(row.t), **game.class_masses(row.p, row.q)} for row in trajectory.itertuples()])
        for class_name in ("I", "H", "M", "D"):
            axis.plot(masses.t, masses[class_name], label=class_name)
        axis.set_title(game.label)
        axis.set_xlabel("Iteration")
        axis.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("Class mass")
    axes[-1].legend(loc="center right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "class_masses.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)

    perturbations = perturbation_audit()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharex=True)
    for key in CONTEXTS:
        subset = perturbations[perturbations.context == key]
        axes[0].plot(subset.radius, subset.class_map_preserved_rate, marker="o", label=key)
        axes[1].plot(subset.radius, subset.equilibrium_set_preserved_rate, marker="o", label=key)
    axes[0].set_title("Class-map retention")
    axes[1].set_title("Original equilibrium-set retention")
    for axis in axes:
        axis.set_xlabel(r"Perturbation radius $\delta$")
        axis.set_ylim(-0.03, 1.03)
        axis.grid(alpha=0.25)
    axes[0].set_ylabel("Share of perturbations")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "payoff_perturbation_robustness.pdf", bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)


def run_all(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in baseline_tables().items():
        _write_result_csv(
            table,
            output_dir / f"{name}.csv",
            index=name not in {"structural_sensitivity", "dynamic_trajectory_distances"},
        )
    detail = sensitivity_grid()
    _write_result_csv(detail, output_dir / "sensitivity_grid_detail.csv")
    _write_result_csv(
        sensitivity_grid_summary(detail), output_dir / "sensitivity_grid_summary.csv"
    )
    _write_result_csv(convergence_diagnostics(), output_dir / "convergence_diagnostics.csv")
    _write_result_csv(perturbation_audit(), output_dir / "payoff_perturbation_audit.csv")
    _write_result_csv(robustness_radii(), output_dir / "robustness_radii.csv")
    _write_result_csv(
        contextual_classifier_audit(), output_dir / "contextual_classifier_audit.csv"
    )
    _write_result_csv(context_path_events(), output_dir / "context_path_events.csv")
    _write_result_csv(
        exhaustive_configuration_audit(), output_dir / "exhaustive_configuration_audit.csv"
    )
    _write_result_csv(
        rectangular_configuration_audit(), output_dir / "rectangular_configuration_audit.csv"
    )
    make_figures(output_dir)
