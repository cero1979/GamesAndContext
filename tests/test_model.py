from __future__ import annotations

import unittest

import numpy as np

from context_games.benchmarks import BENCHMARKS, EXPECTED_PAYOFFS
from context_games.model import classify, simulate, structural_sensitivity, trajectory_distance


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
