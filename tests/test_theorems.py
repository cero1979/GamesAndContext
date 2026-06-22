from __future__ import annotations

import itertools
import unittest

import numpy as np

from context_games.experiments import exhaustive_dichotomy_audit
from context_games.model import ContextGame, perturbed_game, simulate


GAMMA_DIAMOND = ContextGame(
    "gamma_diamond",
    "Gamma diamond",
    ("G", "P"),
    ("U", "R"),
    {("G", "U"): (1, 4), ("G", "R"): (-2, 2), ("P", "U"): (-1, -3), ("P", "R"): (3, -1)},
)


class DichotomyTests(unittest.TestCase):
    def test_gamma_diamond(self) -> None:
        self.assertEqual(set(GAMMA_DIAMOND.pure_nash(strict=True)), {("G", "U"), ("P", "R")})
        self.assertEqual(GAMMA_DIAMOND.classes()[("G", "U")], "I")
        self.assertEqual(GAMMA_DIAMOND.classes()[("P", "R")], "M")
        self.assertGreater(GAMMA_DIAMOND.welfare(("G", "U")), GAMMA_DIAMOND.welfare(("P", "R")))
        self.assertFalse(GAMMA_DIAMOND.pareto_dominates(("G", "U"), ("P", "R")))

    def test_certified_open_ball(self) -> None:
        radius = 0.749
        for signs in itertools.product((-1, 1), repeat=8):
            game = perturbed_game(GAMMA_DIAMOND, radius * np.asarray(signs))
            self.assertEqual(set(game.pure_nash(strict=True)), {("G", "U"), ("P", "R")})
            self.assertEqual(game.classes()[("G", "U")], "I")
            self.assertEqual(game.classes()[("P", "R")], "M")
            self.assertGreater(game.welfare(("G", "U")), game.welfare(("P", "R")))
            self.assertFalse(game.pareto_dominates(("G", "U"), ("P", "R")))

    def test_radius_boundary_is_not_included(self) -> None:
        perturbation = np.asarray((-0.75, -0.75, 0, 0, 0, 0, 0.75, 0.75))
        game = perturbed_game(GAMMA_DIAMOND, perturbation)
        self.assertEqual(game.welfare(("G", "U")), game.welfare(("P", "R")))

    def test_malicious_strict_equilibrium_attracts_locally(self) -> None:
        for p0, q0 in ((0.2, 0.2), (0.1, 0.3), (0.3, 0.1)):
            trajectory = simulate(GAMMA_DIAMOND, p0=p0, q0=q0, horizon=200)
            p, q = trajectory.iloc[-1][["p", "q"]]
            self.assertLess(p, 1e-3)
            self.assertLess(q, 1e-3)

    def test_exhaustive_grid_has_no_counterexample(self) -> None:
        audit = exhaustive_dichotomy_audit().iloc[0]
        self.assertEqual(audit.games, 390625)
        self.assertEqual(audit.shared_row_pairs, 0)
        self.assertEqual(audit.shared_column_dominance_failures, 0)
        self.assertGreater(audit.diagonal_pairs, 0)
        self.assertGreater(audit.strict_diagonal_welfare_dominated_pairs, 0)


if __name__ == "__main__":
    unittest.main()
