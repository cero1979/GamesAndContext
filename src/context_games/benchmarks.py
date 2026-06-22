"""Auditable benchmark specification used by the manuscript."""

from __future__ import annotations

import numpy as np

from .model import ContextGame, Profile

ROWS = ("G", "P")
COLUMNS = ("U", "R")
PROFILES: tuple[Profile, ...] = tuple((a, b) for a in ROWS for b in COLUMNS)
CONTEXTS = ("business", "classroom", "sport")
FEATURES = ("g", "p", "u", "r", "pu", "gr", "pr")

FEATURE_VECTORS = {
    ("G", "U"): np.asarray([1, 0, 1, 0, 0, 0, 0], dtype=float),
    ("G", "R"): np.asarray([1, 0, 0, 1, 0, 1, 0], dtype=float),
    ("P", "U"): np.asarray([0, 1, 1, 0, 1, 0, 0], dtype=float),
    ("P", "R"): np.asarray([0, 1, 0, 1, 0, 0, 1], dtype=float),
}

WEIGHTS = {
    "business": np.asarray(
        [[1, 0, 1, -2, 1, 0, 0], [1, -1, 2, -2, -3, 0, 0]], dtype=float
    ),
    "classroom": np.asarray(
        [[1, -2, 1, -3, 0, 0, 3], [1, -4, 2, 0, 0, 0, 1]], dtype=float
    ),
    "sport": np.asarray(
        [[2, 1, 1, -3, 0, 0, 0], [1, 0, 2, -2, 0, 0, -1]], dtype=float
    ),
}

LABELS = {
    "business": "Business C_B",
    "classroom": "Classroom C_A",
    "sport": "Sport team C_S",
}


def build_benchmarks() -> dict[str, ContextGame]:
    games: dict[str, ContextGame] = {}
    for key in CONTEXTS:
        payoffs = {
            profile: tuple(float(value) for value in WEIGHTS[key] @ FEATURE_VECTORS[profile])
            for profile in PROFILES
        }
        games[key] = ContextGame(key, LABELS[key], ROWS, COLUMNS, payoffs)
    return games


BENCHMARKS = build_benchmarks()

EXPECTED_PAYOFFS = {
    "business": {("G", "U"): (2, 3), ("G", "R"): (-1, -1), ("P", "U"): (2, -2), ("P", "R"): (-2, -3)},
    "classroom": {("G", "U"): (2, 3), ("G", "R"): (-2, 1), ("P", "U"): (-1, -2), ("P", "R"): (-2, -3)},
    "sport": {("G", "U"): (3, 3), ("G", "R"): (-1, -1), ("P", "U"): (2, 2), ("P", "R"): (-2, -3)},
}
