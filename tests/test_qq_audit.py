from __future__ import annotations

from fractions import Fraction
import unittest

import numpy as np

from context_games.contextual_classifier import AffineMap, analyze_cycle
from context_games.qq_audit import (
    centred_score_bound,
    conditioning_formula,
    conditioning_rows,
    institutional_case,
    nilpotent_shear_certificate,
    reference_error_bound,
    robustness_rows,
    running_example_rows,
    strict_label_grid,
    unit_row_matrix,
)


class QualityQuantityAuditTests(unittest.TestCase):
    def test_every_running_table_row_is_correct(self) -> None:
        rows = running_example_rows()
        self.assertEqual([(r["e1"], r["e2"]) for r in rows],
                         [(2, 2), (-3, 1), (1, -3), (-2, -2)])
        self.assertEqual([(r["s1"], r["s2"]) for r in rows],
                         [(1, 1), (-1, 1), (1, -1), (-1, -1)])

    def test_rotation_pi_is_rejected_for_negative_real_eigenvalues(self) -> None:
        analysis = analyze_cycle(AffineMap(-np.eye(2), np.zeros(2)))
        self.assertFalse(analysis.admissible)
        self.assertEqual(analysis.eigenvalues, (-1 + 0j, -1 + 0j))

    def test_rotation_identity_is_admissible_but_reflection_is_not(self) -> None:
        self.assertTrue(analyze_cycle(AffineMap(np.eye(2), np.zeros(2))).admissible)
        self.assertFalse(analyze_cycle(AffineMap(np.diag([1, -1]), np.zeros(2))).admissible)

    def test_conditioning_formula_matches_svd_and_gram_eigenvalues(self) -> None:
        for angle in (.001, .1, 10, 45, 90, 135, 170, 179.999):
            matrix = unit_row_matrix(angle)
            determinant, sigma, condition = conditioning_formula(angle)
            singular = np.linalg.svd(matrix, compute_uv=False)
            self.assertAlmostEqual(determinant, abs(np.linalg.det(matrix)), places=12)
            np.testing.assert_allclose(sigma, singular[-1], rtol=1e-10)
            np.testing.assert_allclose(condition, np.linalg.cond(matrix), rtol=1e-10)
            cosine = abs(np.cos(np.deg2rad(angle)))
            np.testing.assert_allclose(np.linalg.eigvalsh(matrix @ matrix.T),
                                       [1 - cosine, 1 + cosine], atol=1e-14)
            if .1 <= angle <= 179.9:
                np.testing.assert_allclose(condition, np.sqrt((1 + cosine) / (1 - cosine)), rtol=1e-10)

    def test_extreme_conditioning_does_not_reduce_fixed_outcome_margin(self) -> None:
        rows = conditioning_rows()
        self.assertGreater(rows[-1]["reference_error"], 1)
        self.assertGreater(rows[-1]["condition_number"], 1e7)
        for row in rows:
            self.assertAlmostEqual(row["outcome_margin"], 2, places=12)
            np.testing.assert_allclose(row["reference_error"], row["reference_error_bound"], rtol=2e-9, atol=1e-12)

    def test_general_reference_perturbation_bound(self) -> None:
        rng = np.random.default_rng(20260911)
        for angle in (80, 30, 5, 1):
            matrix = unit_row_matrix(angle)
            reference = rng.normal(size=2)
            delta_matrix = rng.normal(size=(2, 2)) * 1e-5
            delta_intercept = rng.normal(size=2) * 1e-5
            recovered = np.linalg.solve(matrix + delta_matrix, matrix @ reference + delta_intercept)
            bound = reference_error_bound(matrix, reference, delta_matrix, delta_intercept)
            self.assertLessEqual(np.linalg.norm(recovered - reference), bound + 1e-12)
        with self.assertRaises(ValueError):
            reference_error_bound(np.eye(2), np.zeros(2), -np.eye(2), np.zeros(2))

    def test_centred_finite_bound_and_translation_invariance(self) -> None:
        rng = np.random.default_rng(20260911)
        for norm in (1, 2, np.inf):
            for _ in range(20):
                appraisal, reference, outcome = rng.normal(size=(3, 2))
                delta_appraisal, delta_reference = rng.normal(size=(2, 2)) * .1
                old = appraisal @ (outcome - reference)
                new = (appraisal + delta_appraisal) @ (outcome - reference - delta_reference)
                expansion = (delta_appraisal @ (outcome - reference)
                             - appraisal @ delta_reference - delta_appraisal @ delta_reference)
                self.assertAlmostEqual(new - old, expansion, places=12)
                bound = centred_score_bound(appraisal, reference, outcome, delta_appraisal, delta_reference, norm=norm)
                self.assertLessEqual(abs(new - old), bound + 1e-12)
                translation = np.array([100, -250])
                shifted = centred_score_bound(appraisal, reference + translation, outcome + translation,
                                               delta_appraisal, delta_reference, norm=norm)
                self.assertAlmostEqual(bound, shifted, places=11)
                if bound < abs(old):
                    self.assertEqual(np.sign(new), np.sign(old))

    def test_cross_term_cannot_be_discarded(self) -> None:
        appraisal = np.array([1.0, 0.0])
        reference = outcome = np.zeros(2)
        delta_appraisal = np.array([0.0, 1.0])
        delta_reference = np.array([0.0, 1.0])
        first_order = delta_appraisal @ (outcome - reference) - appraisal @ delta_reference
        actual_change = (appraisal + delta_appraisal) @ (outcome - reference - delta_reference)
        self.assertEqual(first_order, 0)
        self.assertEqual(actual_change, -1)

    def test_grid_nesting_and_continuous_nonidentification(self) -> None:
        summaries, candidates = strict_label_grid()
        counts = [r["feasible_grid_candidates"] for r in summaries]
        self.assertEqual(counts, sorted(counts, reverse=True))
        for row in summaries:
            self.assertGreater(row["certified_open_ball_radius"], 0)
            self.assertGreater(row["witness_minimum_strict_slack"], 0)
            self.assertGreater(row["distinct_normalised_witness_angle_degrees"], 45)
            self.assertEqual(row["grid_total"], 36461)
        self.assertGreater(len(candidates), 0)

    def test_exogenous_interventions_and_declared_classifier_witness(self) -> None:
        case, rows = institutional_case()
        self.assertTrue(case["coherent_cycle_any_classifier_admissible"])
        self.assertTrue(case["altered_cycle_any_classifier_admissible"])
        np.testing.assert_allclose(case["coherent_reference"], [1, 1], atol=1e-12)
        exact, altered = rows[1:3]
        self.assertEqual(exact["off_diagonal_residual"], 0)
        self.assertTrue(exact["same_signature"])
        self.assertFalse(altered["same_signature"])
        self.assertAlmostEqual(altered["off_diagonal_residual"], .1)
        self.assertAlmostEqual(altered["after_2"], -.075)
        self.assertEqual(rows[3]["off_diagonal_residual"], 0)
        self.assertAlmostEqual(rows[4]["off_diagonal_residual"], .2)

    def test_exact_non_diagonalisable_reporting_cycle_certificate(self) -> None:
        certificate = nilpotent_shear_certificate()
        self.assertTrue(certificate["nilpotent_nonzero"])
        self.assertTrue(certificate["nilpotent_square_zero"])
        self.assertFalse(certificate["any_full_rank_classifier_possible"])
        self.assertEqual(certificate["minimal_polynomial"], "(z-1)^2")
        self.assertTrue(nilpotent_shear_certificate(Fraction(0))["any_full_rank_classifier_possible"])

    def test_retaining_both_intervention_routes_obstructs_common_frame(self) -> None:
        case, _ = institutional_case()
        h = np.array(case["coherent_cycle_linear"])
        k = np.array(case["altered_cycle_linear"])
        appraisal = np.array(case["appraisal_matrix"])
        commutator = appraisal @ (h @ k - k @ h) @ np.linalg.inv(appraisal)
        np.testing.assert_allclose(commutator, [[0, 0], [.3, 0]], atol=1e-12)

    def test_rectangular_common_reference_examples(self) -> None:
        under = np.array([[1.0, 1.0, 0.0], [0.0, 1.0, 1.0]])
        reference = np.array([1.0, 2.0, 3.0])
        kernel_direction = np.array([1.0, -1.0, 1.0])
        np.testing.assert_allclose(under @ kernel_direction, 0)
        np.testing.assert_allclose(under @ reference, under @ (reference + 10 * kernel_direction))
        over = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        compatible = np.array([1.0, 2.0, 3.0])
        recovered = np.linalg.lstsq(over, compatible, rcond=None)[0]
        np.testing.assert_allclose(recovered, [1, 2])
        incompatible = np.array([1.0, 2.0, 4.0])
        recovered = np.linalg.lstsq(over, incompatible, rcond=None)[0]
        self.assertGreater(np.linalg.norm(over @ recovered - incompatible), .5)

    def test_published_robustness_example_certifies_both_signs(self) -> None:
        for row in robustness_rows():
            self.assertTrue(row["sign_certified"])
            self.assertLessEqual(row["absolute_score_change"], row["centred_bound"])


if __name__ == "__main__":
    unittest.main()
