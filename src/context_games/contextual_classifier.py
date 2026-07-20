"""Affine contextual benefit-loss classifiers and transport audits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import numpy as np

Vector: TypeAlias = np.ndarray
Matrix: TypeAlias = np.ndarray
SignPattern: TypeAlias = tuple[int, int]


def _as_vector(value: object, *, name: str) -> Vector:
    vector = np.asarray(value, dtype=float)
    if vector.shape != (2,) or not np.isfinite(vector).all():
        raise ValueError(f"{name} must be a finite vector of shape (2,)")
    vector = vector.copy()
    vector.setflags(write=False)
    return vector


def _as_matrix(value: object, *, name: str) -> Matrix:
    matrix = np.asarray(value, dtype=float)
    if matrix.shape != (2, 2) or not np.isfinite(matrix).all():
        raise ValueError(f"{name} must be a finite matrix of shape (2, 2)")
    matrix = matrix.copy()
    matrix.setflags(write=False)
    return matrix


def sign_pattern(value: object, *, atol: float = 0.0) -> SignPattern:
    """Return the coordinate sign pattern in {-1, 0, 1}^2."""
    if atol < 0:
        raise ValueError("atol must be non-negative")
    vector = _as_vector(value, name="value")
    signs = np.where(vector > atol, 1, np.where(vector < -atol, -1, 0))
    return int(signs[0]), int(signs[1])


@dataclass(frozen=True)
class AffineMap:
    """An invertible affine map x -> linear @ x + offset."""

    linear: Matrix
    offset: Vector

    def __post_init__(self) -> None:
        linear = _as_matrix(self.linear, name="linear")
        if abs(float(np.linalg.det(linear))) <= 1e-14:
            raise ValueError("linear must be nonsingular")
        object.__setattr__(self, "linear", linear)
        object.__setattr__(self, "offset", _as_vector(self.offset, name="offset"))

    def __call__(self, value: object) -> Vector:
        return self.linear @ _as_vector(value, name="value") + self.offset

    def compose(self, inner: "AffineMap") -> "AffineMap":
        """Return self composed after inner."""
        return AffineMap(
            self.linear @ inner.linear,
            self.linear @ inner.offset + self.offset,
        )

    def inverse(self) -> "AffineMap":
        inverse_linear = np.linalg.inv(self.linear)
        return AffineMap(inverse_linear, -(inverse_linear @ self.offset))


@dataclass(frozen=True)
class AffineContext:
    """A contextual signature sign(matrix @ (x - reference))."""

    matrix: Matrix
    reference: Vector

    def __post_init__(self) -> None:
        matrix = _as_matrix(self.matrix, name="matrix")
        if abs(float(np.linalg.det(matrix))) <= 1e-14:
            raise ValueError("matrix must be nonsingular")
        object.__setattr__(self, "matrix", matrix)
        object.__setattr__(self, "reference", _as_vector(self.reference, name="reference"))

    def evaluate(self, value: object) -> Vector:
        return self.matrix @ (_as_vector(value, name="value") - self.reference)

    def signature(self, value: object, *, atol: float = 0.0) -> SignPattern:
        return sign_pattern(self.evaluate(value), atol=atol)

    def transport_to(self, target: "AffineContext", scaling: object) -> AffineMap:
        """Construct the unique transport with a chosen positive row scaling."""
        scale = _as_matrix(scaling, name="scaling")
        if not np.allclose(scale, np.diag(np.diag(scale)), atol=0.0, rtol=0.0):
            raise ValueError("scaling must be diagonal")
        if not np.all(np.diag(scale) > 0):
            raise ValueError("scaling diagonal must be positive")
        linear = np.linalg.solve(target.matrix, scale @ self.matrix)
        offset = target.reference - linear @ self.reference
        return AffineMap(linear, offset)


def transport_multiplier(
    source: AffineContext,
    target: AffineContext,
    transport: AffineMap,
    *,
    atol: float = 1e-10,
) -> Matrix | None:
    """Return the positive diagonal multiplier, or None if transport fails."""
    if atol <= 0:
        raise ValueError("atol must be positive")
    reference_error = transport(source.reference) - target.reference
    if not np.allclose(reference_error, 0.0, atol=atol, rtol=0.0):
        return None
    multiplier = target.matrix @ transport.linear @ np.linalg.inv(source.matrix)
    diagonal = np.diag(np.diag(multiplier))
    if not np.allclose(multiplier, diagonal, atol=atol, rtol=0.0):
        return None
    if not np.all(np.diag(diagonal) > atol):
        return None
    diagonal.setflags(write=False)
    return diagonal


def transport_identity_error(
    source: AffineContext,
    target: AffineContext,
    transport: AffineMap,
    scaling: object,
) -> float:
    """Maximum coefficient error in E_D o T = scaling o E_C."""
    scale = _as_matrix(scaling, name="scaling")
    linear_error = target.matrix @ transport.linear - scale @ source.matrix
    offset_error = target.matrix @ (
        transport.linear @ source.reference + transport.offset - target.reference
    )
    return float(max(np.max(np.abs(linear_error)), np.max(np.abs(offset_error))))


def contextual_radius(
    context: AffineContext,
    value: object,
    *,
    norm: float = 2,
) -> float:
    """Exact distance to the nearest appraisal boundary."""
    if norm == 1:
        dual = np.inf
    elif norm == 2:
        dual = 2
    elif norm == np.inf:
        dual = 1
    else:
        raise ValueError("norm must be 1, 2, or numpy.inf")
    scores = np.abs(context.evaluate(value))
    row_norms = np.linalg.norm(context.matrix, ord=dual, axis=1)
    return float(np.min(scores / row_norms))


def finite_label_inequalities(
    outcomes: object,
    labels: object,
) -> Matrix:
    """Build strict inequalities constraints @ (a1, a2, b) > 0."""
    points = np.asarray(outcomes, dtype=float)
    signs = np.asarray(labels, dtype=int)
    if points.ndim != 2 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError("outcomes must be a finite array of shape (n, 2)")
    if signs.shape != (points.shape[0],) or not np.isin(signs, (-1, 1)).all():
        raise ValueError("labels must contain one strict sign (-1 or 1) per outcome")
    augmented = np.column_stack((points, -np.ones(points.shape[0])))
    constraints = signs[:, None] * augmented
    constraints.setflags(write=False)
    return constraints


def finite_label_slacks(constraints: object, parameters: object) -> Vector:
    matrix = np.asarray(constraints, dtype=float)
    theta = np.asarray(parameters, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != 3 or not np.isfinite(matrix).all():
        raise ValueError("constraints must be a finite array of shape (n, 3)")
    if theta.shape != (3,) or not np.isfinite(theta).all():
        raise ValueError("parameters must be a finite vector of shape (3,)")
    return matrix @ theta


@dataclass(frozen=True)
class CycleAnalysis:
    """Observable implications of one affine contextual cycle."""

    admissible: bool
    has_fixed_point: bool
    unique_reference: bool
    reference: Vector | None
    eigenvalues: tuple[complex, complex]
    left_eigendirections: Matrix | None


def analyze_cycle(cycle: AffineMap, *, atol: float = 1e-10) -> CycleAnalysis:
    """Test the positive-diagonal holonomy condition for one affine cycle."""
    if atol <= 0:
        raise ValueError("atol must be positive")

    fixed_matrix = np.eye(2) - cycle.linear
    candidate, _, _, _ = np.linalg.lstsq(fixed_matrix, cycle.offset, rcond=None)
    has_fixed_point = bool(
        np.allclose(fixed_matrix @ candidate, cycle.offset, atol=atol, rtol=0.0)
    )
    unique_reference = bool(abs(float(np.linalg.det(fixed_matrix))) > atol)
    reference = candidate if has_fixed_point and unique_reference else None
    if reference is not None:
        reference = reference.copy()
        reference.setflags(write=False)

    eigenvalues, right_eigenvectors = np.linalg.eig(cycle.linear)
    real_eigenvalues = bool(np.all(np.abs(eigenvalues.imag) <= atol))
    positive_eigenvalues = real_eigenvalues and bool(np.all(eigenvalues.real > atol))
    diagonalizable = bool(np.linalg.matrix_rank(right_eigenvectors, tol=atol) == 2)
    admissible = has_fixed_point and positive_eigenvalues and diagonalizable

    left_directions: Matrix | None = None
    if admissible and abs(float(eigenvalues[0].real - eigenvalues[1].real)) > atol:
        left_values, left_vectors = np.linalg.eig(cycle.linear.T)
        order = np.argsort(left_values.real)
        directions = left_vectors[:, order].real.T
        directions /= np.linalg.norm(directions, axis=1, keepdims=True)
        directions.setflags(write=False)
        left_directions = directions

    return CycleAnalysis(
        admissible=admissible,
        has_fixed_point=has_fixed_point,
        unique_reference=unique_reference,
        reference=reference,
        eigenvalues=(complex(eigenvalues[0]), complex(eigenvalues[1])),
        left_eigendirections=left_directions,
    )
