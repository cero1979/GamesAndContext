from __future__ import annotations

import unittest

import numpy as np

from context_games.contextual_classifier import (
    AffineContext,
    AffineMap,
    analyze_cycle,
    contextual_radius,
    finite_label_inequalities,
    finite_label_slacks,
    sign_pattern,
    transport_identity_error,
    transport_multiplier,
)
from context_games.experiments import (
    context_path_events,
    contextual_classifier_audit,
)


class ContextualClassifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.first = AffineContext(
            np.asarray([[1.0, 0.25], [-0.2, 1.0]]),
            np.asarray([0.5, -1.0]),
        )
        self.second = AffineContext(
            np.asarray([[0.8, -0.1], [0.3, 1.2]]),
            np.asarray([-0.25, 0.75]),
        )

    def test_sign_is_invariant_under_positive_coordinate_rescaling(self) -> None:
        vectors = (
            np.asarray([2.0, 3.0]),
            np.asarray([-2.0, 3.0]),
            np.asarray([2.0, -3.0]),
            np.asarray([-2.0, -3.0]),
            np.asarray([0.0, -3.0]),
        )
        scaling = np.asarray([4.0, 0.2])
        for vector in vectors:
            self.assertEqual(sign_pattern(vector), sign_pattern(scaling * vector))

    def test_exact_transport_and_composition_law(self) -> None:
        third = AffineContext(
            np.asarray([[1.1, 0.4], [-0.3, 0.9]]),
            np.asarray([1.25, 0.2]),
        )
        first_scale = np.diag([2.0, 3.0])
        second_scale = np.diag([0.5, 4.0])
        first_transport = self.first.transport_to(self.second, first_scale)
        second_transport = self.second.transport_to(third, second_scale)
        composite = second_transport.compose(first_transport)
        direct = self.first.transport_to(third, second_scale @ first_scale)

        self.assertLess(
            transport_identity_error(
                self.first, self.second, first_transport, first_scale
            ),
            1e-12,
        )
        np.testing.assert_allclose(composite.linear, direct.linear, atol=1e-12)
        np.testing.assert_allclose(composite.offset, direct.offset, atol=1e-12)
        np.testing.assert_allclose(
            transport_multiplier(self.first, third, composite),
            second_scale @ first_scale,
            atol=1e-12,
        )

        rng = np.random.default_rng(20260720)
        for point in rng.normal(size=(50, 2)):
            self.assertEqual(
                self.first.signature(point),
                self.second.signature(first_transport(point)),
            )

    def test_rotation_is_a_holonomy_obstruction(self) -> None:
        quarter_turn = AffineMap(
            np.asarray([[0.0, -1.0], [1.0, 0.0]]),
            np.zeros(2),
        )
        analysis = analyze_cycle(quarter_turn)
        self.assertFalse(analysis.admissible)
        self.assertTrue(analysis.has_fixed_point)
        self.assertTrue(any(abs(value.imag) > 0.5 for value in analysis.eigenvalues))

    def test_nondegenerate_cycle_identifies_reference_and_boundaries(self) -> None:
        matrix = np.asarray([[1.0, 1.0], [1.0, -1.0]])
        reference = np.asarray([0.5, -0.25])
        context = AffineContext(matrix, reference)
        cycle = context.transport_to(context, np.diag([2.0, 3.0]))
        analysis = analyze_cycle(cycle)

        self.assertTrue(analysis.admissible)
        self.assertTrue(analysis.unique_reference)
        np.testing.assert_allclose(analysis.reference, reference, atol=1e-12)
        self.assertIsNotNone(analysis.left_eigendirections)

        recovered = analysis.left_eigendirections
        assert recovered is not None
        normalized_rows = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
        absolute_matches = np.abs(recovered @ normalized_rows.T)
        self.assertTrue(np.all(np.max(absolute_matches, axis=1) > 1 - 1e-12))

    def test_exact_contextual_radius_for_three_norms(self) -> None:
        context = AffineContext(
            np.asarray([[1.0, -1.0], [1.0, 1.0]]),
            np.zeros(2),
        )
        point = np.asarray([3.0, 1.0])
        self.assertAlmostEqual(contextual_radius(context, point, norm=1), 2.0)
        self.assertAlmostEqual(contextual_radius(context, point, norm=2), np.sqrt(2.0))
        self.assertAlmostEqual(contextual_radius(context, point, norm=np.inf), 1.0)

    def test_finite_strict_labels_define_an_open_identified_set(self) -> None:
        outcomes = np.asarray([[2.0, 1.0], [-1.0, 2.0], [2.0, -3.0], [-2.0, -2.0]])
        labels = np.sign(outcomes[:, 0]).astype(int)
        constraints = finite_label_inequalities(outcomes, labels)
        exact = np.asarray([1.0, 0.0, 0.0])
        nearby = np.asarray([1.01, 0.001, 0.001])

        self.assertGreater(np.min(finite_label_slacks(constraints, exact)), 0.0)
        self.assertGreater(np.min(finite_label_slacks(constraints, nearby)), 0.0)

    def test_nontransport_is_rejected(self) -> None:
        identity_context = AffineContext(np.eye(2), np.zeros(2))
        shear = AffineMap(np.asarray([[1.0, 1.0], [0.0, 1.0]]), np.zeros(2))
        self.assertIsNone(
            transport_multiplier(identity_context, identity_context, shear)
        )

    def test_reported_audits_pass_and_path_events_are_transversal(self) -> None:
        audit = contextual_classifier_audit()
        events = context_path_events()
        self.assertTrue(audit.passed.all())
        self.assertTrue((audit.loc[audit.relation == "<=", "value"] == 0.0).all())
        self.assertEqual(
            set(audit.audit),
            {
                "exact_transport_identity",
                "transport_composition",
                "rotation_cycle_obstruction",
                "cycle_reference_recovery",
                "euclidean_margin_sharp_value",
                "finite_label_open_slack",
            },
        )
        self.assertTrue(events.transversal.all())
        self.assertEqual(list(events.crossing_t), [-1.0, 0.5, 2.0])


if __name__ == "__main__":
    unittest.main()
