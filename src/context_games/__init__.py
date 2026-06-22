"""Context-dependent benefit-loss games."""

from .benchmarks import BENCHMARKS, CONTEXTS, FEATURES, PROFILES, WEIGHTS
from .model import ContextGame, classify, multiplicative_weights_step, simulate

__all__ = [
    "BENCHMARKS",
    "CONTEXTS",
    "FEATURES",
    "PROFILES",
    "WEIGHTS",
    "ContextGame",
    "classify",
    "multiplicative_weights_step",
    "simulate",
]

__version__ = "0.9.0"
