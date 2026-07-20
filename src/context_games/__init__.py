"""Context-dependent benefit-loss games and contextual classifiers."""

from .benchmarks import BENCHMARKS, CONTEXTS, FEATURES, PROFILES, WEIGHTS
from .contextual_classifier import (
    AffineContext,
    AffineMap,
    analyze_cycle,
    contextual_radius,
    finite_label_inequalities,
    sign_pattern,
    transport_multiplier,
)
from .model import (
    ContextGame,
    classify,
    multiplicative_weights_step,
    opponent_contingent_affine_game,
    opponent_contingent_payoff_transform,
    simulate,
)

__all__ = [
    "BENCHMARKS",
    "CONTEXTS",
    "FEATURES",
    "PROFILES",
    "WEIGHTS",
    "AffineContext",
    "AffineMap",
    "ContextGame",
    "analyze_cycle",
    "classify",
    "contextual_radius",
    "finite_label_inequalities",
    "multiplicative_weights_step",
    "opponent_contingent_affine_game",
    "opponent_contingent_payoff_transform",
    "simulate",
    "sign_pattern",
    "transport_multiplier",
]

__version__ = "0.10.0"
