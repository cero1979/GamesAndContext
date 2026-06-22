"""Core definitions for finite two-player benefit-loss games.

The core module is deliberately independent of the manuscript benchmarks.  This
keeps theorem checks and alternative calibrations from depending on notebook
state or plotting code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, TypeAlias

import numpy as np
import pandas as pd

Profile: TypeAlias = tuple[str, str]
Payoff: TypeAlias = tuple[float, float]


def classify(x: float, y: float) -> str:
    """Return the manuscript's benefit-loss class, including its D0 convention."""
    if x > 0 and y > 0:
        return "I"
    if x < 0 and y > 0:
        return "H"
    if x > 0 and y < 0:
        return "M"
    if x <= 0 and y < 0:
        return "D"
    return "boundary"


def axis_margin(payoff: Payoff) -> float:
    return float(min(abs(payoff[0]), abs(payoff[1])))


@dataclass(frozen=True)
class ContextGame:
    """A finite contextual game with actor and affected-side payoffs."""

    key: str
    label: str
    rows: tuple[str, ...]
    columns: tuple[str, ...]
    payoffs: Mapping[Profile, Payoff]

    def __post_init__(self) -> None:
        if len(self.rows) < 2 or len(self.columns) < 2:
            raise ValueError(f"{self.key}: each player must have at least two actions")
        if len(set(self.rows)) != len(self.rows) or len(set(self.columns)) != len(self.columns):
            raise ValueError(f"{self.key}: action labels must be unique for each player")
        expected = {(a, b) for a in self.rows for b in self.columns}
        if set(self.payoffs) != expected:
            raise ValueError(f"{self.key}: payoff keys do not match the finite profile set")
        for profile, payoff in self.payoffs.items():
            if len(payoff) != 2 or not all(np.isfinite(value) for value in payoff):
                raise ValueError(f"{self.key}: payoff at {profile} must contain two finite values")

    @property
    def profiles(self) -> tuple[Profile, ...]:
        return tuple((a, b) for a in self.rows for b in self.columns)

    def classes(self) -> dict[Profile, str]:
        return {profile: classify(*self.payoffs[profile]) for profile in self.profiles}

    def payoff_matrix(self, player: int) -> np.ndarray:
        if player not in (0, 1):
            raise ValueError("player must be 0 (actor) or 1 (affected side)")
        return np.asarray(
            [[self.payoffs[(a, b)][player] for b in self.columns] for a in self.rows],
            dtype=float,
        )

    def pure_nash(self, *, strict: bool = False) -> tuple[Profile, ...]:
        actor = self.payoff_matrix(0)
        affected = self.payoff_matrix(1)
        equilibria: list[Profile] = []
        for i, a in enumerate(self.rows):
            for j, b in enumerate(self.columns):
                actor_advantages = [
                    actor[i, j] - actor[k, j] for k in range(len(self.rows)) if k != i
                ]
                affected_advantages = [
                    affected[i, j] - affected[i, k] for k in range(len(self.columns)) if k != j
                ]
                actor_ok = min(actor_advantages) > 0 if strict else min(actor_advantages) >= 0
                affected_ok = (
                    min(affected_advantages) > 0 if strict else min(affected_advantages) >= 0
                )
                if actor_ok and affected_ok:
                    equilibria.append((a, b))
        return tuple(equilibria)

    def _require_2x2(self) -> None:
        """Reject calls to the benchmark dynamics outside their stated domain."""
        if len(self.rows) != 2 or len(self.columns) != 2:
            raise ValueError(f"{self.key}: this population-dynamics operation requires a 2x2 game")

    def welfare(self, profile: Profile) -> float:
        return float(sum(self.payoffs[profile]))

    def pareto_dominates(self, better: Profile, worse: Profile) -> bool:
        x1, y1 = self.payoffs[better]
        x2, y2 = self.payoffs[worse]
        return x1 >= x2 and y1 >= y2 and (x1 > x2 or y1 > y2)

    def profile_distribution(self, p: float, q: float) -> dict[Profile, float]:
        self._require_2x2()
        a0, a1 = self.rows
        b0, b1 = self.columns
        return {
            (a0, b0): p * q,
            (a0, b1): p * (1.0 - q),
            (a1, b0): (1.0 - p) * q,
            (a1, b1): (1.0 - p) * (1.0 - q),
        }

    def class_masses(self, p: float, q: float) -> dict[str, float]:
        masses = {key: 0.0 for key in ("I", "H", "M", "D", "boundary")}
        classes = self.classes()
        for profile, probability in self.profile_distribution(p, q).items():
            masses[classes[profile]] += probability
        return masses

    def expected_welfare(self, p: float, q: float) -> float:
        distribution = self.profile_distribution(p, q)
        return float(sum(prob * self.welfare(profile) for profile, prob in distribution.items()))

    def payoff_gaps(self, p: float, q: float) -> tuple[float, float]:
        self._require_2x2()
        actor = self.payoff_matrix(0)
        affected = self.payoff_matrix(1)
        actor_gap = q * (actor[0, 0] - actor[1, 0]) + (1.0 - q) * (
            actor[0, 1] - actor[1, 1]
        )
        affected_gap = p * (affected[0, 0] - affected[0, 1]) + (1.0 - p) * (
            affected[1, 0] - affected[1, 1]
        )
        return float(actor_gap), float(affected_gap)


def multiplicative_weights_step(
    game: ContextGame, p: float, q: float, eta: float = 0.45
) -> tuple[float, float]:
    """One discrete exponential-replicator (multiplicative-weights) update."""
    game._require_2x2()
    if eta <= 0:
        raise ValueError("eta must be positive")
    if not (0.0 <= p <= 1.0 and 0.0 <= q <= 1.0):
        raise ValueError("p and q must lie in [0, 1]")

    actor = game.payoff_matrix(0)
    affected = game.payoff_matrix(1)
    actor_scores = eta * np.asarray(
        [q * actor[0, 0] + (1 - q) * actor[0, 1], q * actor[1, 0] + (1 - q) * actor[1, 1]]
    )
    affected_scores = eta * np.asarray(
        [
            p * affected[0, 0] + (1 - p) * affected[1, 0],
            p * affected[0, 1] + (1 - p) * affected[1, 1],
        ]
    )
    actor_scores -= actor_scores.max()
    affected_scores -= affected_scores.max()
    actor_weights = np.asarray([p, 1 - p]) * np.exp(actor_scores)
    affected_weights = np.asarray([q, 1 - q]) * np.exp(affected_scores)
    return (
        float(actor_weights[0] / actor_weights.sum()),
        float(affected_weights[0] / affected_weights.sum()),
    )


def simulate(
    game: ContextGame,
    *,
    p0: float = 0.5,
    q0: float = 0.5,
    eta: float = 0.45,
    horizon: int = 50,
) -> pd.DataFrame:
    game._require_2x2()
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    rows: list[dict[str, float | int]] = []
    p, q = float(p0), float(q0)
    for t in range(horizon + 1):
        rows.append({"t": t, "p": p, "q": q})
        if t < horizon:
            p, q = multiplicative_weights_step(game, p, q, eta)
    return pd.DataFrame(rows)


def structural_sensitivity(first: ContextGame, second: ContextGame) -> float:
    if first.rows != second.rows or first.columns != second.columns:
        raise ValueError("games must share a strategic form")
    first_classes = first.classes()
    second_classes = second.classes()
    changed = sum(first_classes[p] != second_classes[p] for p in first.profiles)
    return changed / len(first.profiles)


def class_map_robustness_radius(game: ContextGame) -> float:
    """Supremal open sup-norm radius certified by distance to the payoff axes."""
    return min(axis_margin(game.payoffs[profile]) for profile in game.profiles)


def equilibrium_set_robustness_radius(game: ContextGame) -> float:
    """Exact open sup-norm radius preserving the full pure-Nash set.

    A unilateral payoff difference changes by at most twice the coordinate-wise
    perturbation radius.  An equilibrium survives while all of its advantages
    stay non-negative.  A non-equilibrium stays out while at least one negative
    advantage remains negative.
    """
    actor = game.payoff_matrix(0)
    affected = game.payoff_matrix(1)
    equilibria = set(game.pure_nash())
    profile_radii: list[float] = []
    for i, a in enumerate(game.rows):
        for j, b in enumerate(game.columns):
            profile = (a, b)
            advantages = [
                actor[i, j] - actor[k, j] for k in range(len(game.rows)) if k != i
            ] + [
                affected[i, j] - affected[i, k]
                for k in range(len(game.columns))
                if k != j
            ]
            if profile in equilibria:
                profile_radii.append(min(advantages) / 2.0)
            else:
                negative_slacks = [-advantage for advantage in advantages if advantage < 0]
                if not negative_slacks:
                    raise AssertionError(
                        "non-equilibrium profile has no negative deviation advantage"
                    )
                profile_radii.append(max(negative_slacks) / 2.0)
    return float(min(profile_radii))


def trajectory_distance(
    first: ContextGame,
    second: ContextGame,
    *,
    p0: float = 0.5,
    q0: float = 0.5,
    eta: float = 0.45,
    horizon: int = 50,
) -> float:
    def distributions(game: ContextGame) -> np.ndarray:
        trajectory = simulate(game, p0=p0, q0=q0, eta=eta, horizon=horizon)
        return np.asarray(
            [
                [game.profile_distribution(float(row.p), float(row.q))[p] for p in game.profiles]
                for row in trajectory.itertuples()
            ]
        )

    first_dist = distributions(first)
    second_dist = distributions(second)
    return float(np.mean(0.5 * np.abs(first_dist - second_dist).sum(axis=1)))


def perturbed_game(game: ContextGame, perturbation: Iterable[float]) -> ContextGame:
    values = np.asarray(tuple(perturbation), dtype=float)
    expected_coordinates = 2 * len(game.profiles)
    if values.shape != (expected_coordinates,):
        raise ValueError(f"payoff perturbation must have {expected_coordinates} coordinates")
    payoffs: dict[Profile, Payoff] = {}
    for index, profile in enumerate(game.profiles):
        x, y = game.payoffs[profile]
        payoffs[profile] = (x + values[2 * index], y + values[2 * index + 1])
    return ContextGame(game.key, game.label, game.rows, game.columns, payoffs)
