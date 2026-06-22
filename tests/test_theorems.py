from __future__ import annotations

import itertools
import unittest

import numpy as np

from context_games.experiments import (
    exhaustive_configuration_audit,
    rectangular_configuration_audit,
)
from context_games.model import (
    ContextGame,
    opponent_contingent_affine_game,
    opponent_contingent_payoff_transform,
    perturbed_game,
    simulate,
)


GAMMA_DIAMOND = ContextGame(
    "gamma_diamond",
    "Gamma diamond",
    ("G", "P"),
    ("U", "R"),
    {("G", "U"): (1, 4), ("G", "R"): (-2, 2), ("P", "U"): (-1, -3), ("P", "R"): (3, -1)},
)


class ConfigurationTests(unittest.TestCase):
    def test_exhaustive_joint_preservation_sign_grid(self) -> None:
        profiles = (("G", "U"), ("G", "R"), ("P", "U"), ("P", "R"))
        changed_by_offsets = 0

        def best_response_signature(game: ContextGame) -> tuple[tuple[str, ...], ...]:
            return tuple(
                [game.pure_best_responses(0, column) for column in game.columns]
                + [game.pure_best_responses(1, row) for row in game.rows]
            )

        for index, coordinates in enumerate(itertools.product((-1.0, 1.0), repeat=8)):
            payoffs = {
                profile: (coordinates[2 * k], coordinates[2 * k + 1])
                for k, profile in enumerate(profiles)
            }
            game = ContextGame(f"sign-grid-{index}", "Sign-grid game", ("G", "P"), ("U", "R"), payoffs)
            transformed = opponent_contingent_payoff_transform(
                game,
                actor_transforms={"U": lambda x: x**3, "R": lambda x: 3.0 * x**3},
                affected_transforms={"G": lambda y: 2.0 * y**3, "P": lambda y: y**3},
            )
            shifted = opponent_contingent_affine_game(
                game,
                actor_scales={"U": 1.0, "R": 1.0},
                affected_scales={"G": 1.0, "P": 1.0},
                actor_offsets={"U": 2.0, "R": 2.0},
                affected_offsets={"G": 2.0, "P": 2.0},
            )

            self.assertEqual(transformed.classes(), game.classes())
            self.assertEqual(best_response_signature(transformed), best_response_signature(game))
            self.assertEqual(best_response_signature(shifted), best_response_signature(game))
            changed_by_offsets += shifted.classes() != game.classes()

        self.assertEqual(changed_by_offsets, 255)

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
        audit = exhaustive_configuration_audit().iloc[0]
        self.assertEqual(audit.games, 390625)
        self.assertEqual(audit.shared_row_pairs, 0)
        self.assertEqual(audit.shared_column_dominance_failures, 0)
        self.assertGreater(audit.diagonal_pairs, 0)
        self.assertGreater(audit.strict_diagonal_welfare_dominated_pairs, 0)

    def test_rectangular_grids_have_no_counterexample(self) -> None:
        audit = rectangular_configuration_audit(values=(-1, 1)).set_index("shape")
        self.assertEqual(audit.loc["2x3", "games"], 4096)
        self.assertEqual(audit.loc["3x2", "games"], 4096)
        self.assertEqual(audit.loc["2x3", "I_M_equilibrium_pairs"], 1152)
        self.assertEqual(audit.loc["3x2", "I_M_equilibrium_pairs"], 3072)
        self.assertTrue((audit.shared_actor_action_pairs == 0).all())
        self.assertTrue((audit.shared_affected_action_dominance_failures == 0).all())
        self.assertTrue((audit.disjoint_action_pairs > 0).all())


if __name__ == "__main__":
    unittest.main()
