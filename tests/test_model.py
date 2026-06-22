from __future__ import annotations

import itertools
import unittest

import numpy as np

from context_games.benchmarks import BENCHMARKS, EXPECTED_PAYOFFS
from context_games.model import (
    ContextGame,
    class_map_robustness_radius,
    classify,
    equilibrium_set_robustness_radius,
    perturbed_game,
    simulate,
    structural_sensitivity,
    trajectory_distance,
)


RECTANGULAR_GAME = ContextGame(
    "rectangular",
    "Rectangular test game",
    ("A", "B"),
    ("L", "C", "R"),
    {
        ("A", "L"): (3.0, 3.0),
        ("A", "C"): (-1.0, 1.0),
        ("A", "R"): (2.0, -1.0),
        ("B", "L"): (1.0, -1.0),
        ("B", "C"): (2.0, 2.0),
        ("B", "R"): (-1.0, 1.0),
    },
)


class ClassificationTests(unittest.TestCase):
    def test_boundary_convention(self) -> None:
        self.assertEqual(classify(1, 1), "I")
        self.assertEqual(classify(-1, 1), "H")
        self.assertEqual(classify(1, -1), "M")
        self.assertEqual(classify(-1, -1), "D")
        self.assertEqual(classify(0, -1), "D")
        self.assertEqual(classify(0, 1), "boundary")

    def test_feature_weights_reproduce_payoffs(self) -> None:
        for key, expected in EXPECTED_PAYOFFS.items():
            self.assertEqual(BENCHMARKS[key].payoffs, expected)


class FiniteGameTests(unittest.TestCase):
    def test_rectangular_equilibria_and_exact_radii(self) -> None:
        self.assertEqual(RECTANGULAR_GAME.pure_nash(), (("A", "L"), ("B", "C")))
        self.assertEqual(
            RECTANGULAR_GAME.pure_nash(strict=True), (("A", "L"), ("B", "C"))
        )
        self.assertEqual(class_map_robustness_radius(RECTANGULAR_GAME), 1.0)
        self.assertEqual(equilibrium_set_robustness_radius(RECTANGULAR_GAME), 0.5)

        vertices = itertools.product((-1.0, 1.0), repeat=12)
        self.assertTrue(
            all(
                perturbed_game(RECTANGULAR_GAME, 0.49 * np.asarray(vertex)).pure_nash()
                == RECTANGULAR_GAME.pure_nash()
                for vertex in vertices
            )
        )
        vertices = itertools.product((-1.0, 1.0), repeat=12)
        self.assertTrue(
            any(
                perturbed_game(RECTANGULAR_GAME, 0.51 * np.asarray(vertex)).pure_nash()
                != RECTANGULAR_GAME.pure_nash()
                for vertex in vertices
            )
        )

    def test_population_dynamics_reject_rectangular_game(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires a 2x2 game"):
            simulate(RECTANGULAR_GAME)


class BenchmarkTests(unittest.TestCase):
    def test_classes_and_equilibria(self) -> None:
        self.assertEqual(BENCHMARKS["business"].classes()[("P", "U")], "M")
        self.assertEqual(BENCHMARKS["classroom"].classes()[("P", "U")], "D")
        self.assertEqual(BENCHMARKS["sport"].classes()[("P", "U")], "I")
        self.assertEqual(BENCHMARKS["business"].pure_nash(), (("G", "U"), ("P", "U")))
        self.assertEqual(BENCHMARKS["classroom"].pure_nash(), (("G", "U"),))
        self.assertEqual(BENCHMARKS["sport"].pure_nash(), (("G", "U"),))

    def test_structural_sensitivity(self) -> None:
        self.assertEqual(structural_sensitivity(BENCHMARKS["business"], BENCHMARKS["classroom"]), 0.5)
        self.assertEqual(structural_sensitivity(BENCHMARKS["business"], BENCHMARKS["sport"]), 0.25)
        self.assertEqual(structural_sensitivity(BENCHMARKS["classroom"], BENCHMARKS["sport"]), 0.5)

    def test_exact_robustness_radii(self) -> None:
        for game in BENCHMARKS.values():
            self.assertEqual(class_map_robustness_radius(game), 1.0)
        self.assertEqual(equilibrium_set_robustness_radius(BENCHMARKS["business"]), 0.0)
        self.assertEqual(equilibrium_set_robustness_radius(BENCHMARKS["classroom"]), 0.5)
        self.assertEqual(equilibrium_set_robustness_radius(BENCHMARKS["sport"]), 0.5)

    def test_robustness_radii_against_all_box_vertices(self) -> None:
        vertices = tuple(itertools.product((-1.0, 1.0), repeat=8))
        for game in BENCHMARKS.values():
            original_classes = game.classes()
            self.assertTrue(
                all(perturbed_game(game, 0.99 * np.asarray(v)).classes() == original_classes for v in vertices)
            )
            self.assertTrue(
                any(perturbed_game(game, 1.01 * np.asarray(v)).classes() != original_classes for v in vertices)
            )
        for key in ("classroom", "sport"):
            game = BENCHMARKS[key]
            original_ne = game.pure_nash()
            self.assertTrue(
                all(perturbed_game(game, 0.49 * np.asarray(v)).pure_nash() == original_ne for v in vertices)
            )
            self.assertTrue(
                any(perturbed_game(game, 0.51 * np.asarray(v)).pure_nash() != original_ne for v in vertices)
            )
        business = BENCHMARKS["business"]
        self.assertTrue(
            any(
                perturbed_game(business, 1e-6 * np.asarray(v)).pure_nash() != business.pure_nash()
                for v in vertices
            )
        )

    def test_equilibrium_radius_edge_cases(self) -> None:
        matching_pennies = ContextGame(
            "matching-pennies",
            "Matching pennies",
            ("T", "B"),
            ("L", "R"),
            {
                ("T", "L"): (1.0, -1.0),
                ("T", "R"): (-1.0, 1.0),
                ("B", "L"): (-1.0, 1.0),
                ("B", "R"): (1.0, -1.0),
            },
        )
        flat = ContextGame(
            "flat",
            "Flat",
            ("T", "B"),
            ("L", "R"),
            {profile: (0.0, 0.0) for profile in (("T", "L"), ("T", "R"), ("B", "L"), ("B", "R"))},
        )
        self.assertEqual(matching_pennies.pure_nash(), ())
        self.assertEqual(equilibrium_set_robustness_radius(matching_pennies), 1.0)
        self.assertEqual(len(flat.pure_nash()), 4)
        self.assertEqual(equilibrium_set_robustness_radius(flat), 0.0)

        vertices = tuple(itertools.product((-1.0, 1.0), repeat=8))
        self.assertTrue(
            all(not perturbed_game(matching_pennies, 0.99 * np.asarray(v)).pure_nash() for v in vertices)
        )
        self.assertTrue(
            any(perturbed_game(matching_pennies, 1.01 * np.asarray(v)).pure_nash() for v in vertices)
        )
        self.assertTrue(
            any(perturbed_game(flat, 1e-6 * np.asarray(v)).pure_nash() != flat.pure_nash() for v in vertices)
        )

    def test_baseline_trajectory_regression(self) -> None:
        trajectory = simulate(BENCHMARKS["business"])
        p, q = trajectory.iloc[-1][["p", "q"]]
        self.assertTrue(np.isclose(p, 0.59696655, atol=1e-7))
        self.assertTrue(np.isclose(q, 1.0, atol=1e-7))
        self.assertTrue(
            np.isclose(BENCHMARKS["business"].class_masses(float(p), float(q))["M"], 0.40303345, atol=1e-7)
        )

    def test_dynamic_distance_regression(self) -> None:
        self.assertTrue(
            np.isclose(
                trajectory_distance(BENCHMARKS["business"], BENCHMARKS["classroom"]),
                0.38459481,
                atol=1e-7,
            )
        )


if __name__ == "__main__":
    unittest.main()
