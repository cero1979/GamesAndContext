"""Numerical and source checks for the final presentation; no visual-QA claims."""

import hashlib
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

import numpy as np

from context_games.qq_audit import running_example_rows

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("qq_final_audit", ROOT / "scripts/run_qq_final_audit.py")
FINAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FINAL)


class FinalPresentationTests(unittest.TestCase):
    def test_compact_game_keeps_strategic_and_evaluative_layers_separate(self):
        utilities = np.array([[[0., 1.], [0., 0.]], [[1., 1.], [1., 0.]]])
        consequences = {(1, 0): np.array([1., -1.]), (0, 0): np.array([1., 1.])}
        strict_equilibria = [
            (row, column) for row in range(2) for column in range(2)
            if utilities[row, column, 0] > utilities[1 - row, column, 0]
            and utilities[row, column, 1] > utilities[row, 1 - column, 1]
        ]
        self.assertEqual(strict_equilibria, [(1, 0)])
        self.assertEqual(tuple(np.sign(consequences[(1, 0)])), (1, -1))
        self.assertEqual(tuple(np.sign(consequences[(0, 0)])), (1, 1))
        rng = np.random.default_rng(20260911)
        for _ in range(50):
            perturbed = utilities + rng.uniform(-.49, .49, utilities.shape)
            self.assertTrue(np.all(perturbed[1, :, 0] > perturbed[0, :, 0]))
            self.assertTrue(np.all(perturbed[:, 0, 1] > perturbed[:, 1, 1]))
            for profile, outcome in consequences.items():
                shifted = outcome + rng.uniform(-.99, .99, 2)
                np.testing.assert_array_equal(np.sign(shifted), np.sign(outcome))

    def test_running_evaluations_and_signatures(self):
        expected = [((3, 0), (2, 2), (1, 1)), ((0, 2), (-3, 1), (-1, 1)),
                    ((0, -2), (1, -3), (1, -1)), ((-1, 0), (-2, -2), (-1, -1))]
        for row, (point, scores, signature) in zip(running_example_rows(), expected):
            self.assertEqual((row["x1"], row["x2"]), point)
            self.assertEqual((row["e1"], row["e2"]), scores)
            self.assertEqual((row["s1"], row["s2"]), signature)

    def test_running_table_has_three_columns_and_no_legacy_labels(self):
        table = FINAL.running_table()
        self.assertIn(r"\begin{tabular}{ccc}", table)
        self.assertIn(r"Outcome \(x\) & \(E_C(x)\) & Signature", table)
        rows = [line for line in table.splitlines() if " & " in line]
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(line.count(" & ") == 2 for line in rows))
        self.assertNotIn("Legacy", table)
        for label in "IHMD":
            self.assertNotIn(r"\(" + label + r"\)", table)
        self.assertIn(r"\((0,-2)\) & \((1,-3)\) & \((+,-)\)", table)
        self.assertIn("not types of people", table)

    def test_figure_geometry_and_signature_coordinates(self):
        source = (ROOT / "figures/contextual_fans_final.tex").read_text(encoding="utf-8")
        for geometry in ("(-3.2,0)--(3.2,0)", "(0,-2.7)--(0,2.7)",
                         "(-1.6,-2.6)--(3.6,2.6)", "(-1.6,2.6)--(3.6,-2.6)",
                         r"\fill (1,0) circle (2pt)", "[xshift=8.2cm]", "scale=0.88"):
            self.assertIn(geometry, source)
        nodes = re.findall(r"\\node\[signature\] at \(([-\d.]+),([-\d.]+)\) \{\\\(\(([+\-]),([+\-])\)\\\)\};", source)
        self.assertEqual(len(nodes), 8)
        self.assertEqual([(float(x), float(y)) for x, y, _, _ in nodes],
                         [(1.5, 1.45), (-1.5, 1.45), (1.5, -1.45), (-1.5, -1.45),
                          (2.45, 0), (.4, 1.55), (.4, -1.55), (-1.65, 0)])
        matrix = np.array([[1., -1.], [1., 1.]])
        for index, (x, y, first, second) in enumerate(nodes):
            point = np.array([float(x), float(y)])
            scores = point if index < 4 else matrix @ (point - [1., 0.])
            self.assertEqual(tuple(np.sign(scores)),
                             tuple(1 if sign == "+" else -1 for sign in (first, second)))
        self.assertIn("signature/.style={fill=white,inner sep=2pt}", source)
        self.assertNotRegex(source, r"\\[IHMD]class")

    def test_provenance_hashes_final_content_and_retains_diagnostic_fields(self):
        old = {"seed": 20260911, "source_sha256": {"base.py": "base-hash"},
               "outputs_sha256": {"table_running_labels.tex": "old-hash"}}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            content = FINAL.running_table().encode("utf-8")
            (output / "table_running_labels.tex").write_bytes(content)
            (output / "provenance.json").write_text("old provenance", encoding="utf-8")
            result = FINAL.refresh_provenance(old, output, figure_compiled=False)
            self.assertEqual(result["seed"], old["seed"])
            self.assertEqual(result["source_sha256"]["base.py"], "base-hash")
            self.assertEqual(result["outputs_sha256"],
                             {"table_running_labels.tex": hashlib.sha256(content).hexdigest()})
            self.assertEqual(old["source_sha256"], {"base.py": "base-hash"})
            self.assertTrue(result["reproduction_command"].endswith(" --skip-figure"))
            self.assertEqual(len(result["source_sha256"]), 4)


if __name__ == "__main__":
    unittest.main()
