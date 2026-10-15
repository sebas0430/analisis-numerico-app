"""Método de Jacobi.

A diferencia de Gauss-Seidel, cada iteración usa únicamente los valores de
la iteración anterior (x⁽ᵏ⁾), nunca los recién calculados. Programado a
mano porque NumPy y SciPy no lo incluyen. Guarda cada iteración en una tabla.
"""
import numpy as np

from algoritmos.sistemas_lineales.validacion import validar_sistema


def es_diagonal_dominante(A) -> bool:
    """|a_ii| > suma de |a_ij| (j != i) en todas las filas."""
    diagonal = np.abs(np.diag(A))
    resto = np.sum(np.abs(A), axis=1) - diagonal
    return bool(np.all(diagonal > resto))


def resolver_jacobi(A, b, x0=None, tol: float = 1e-6,
                    max_iter: int = 100) -> dict:
    A, b = validar_sistema(A, b)
    n = A.shape[0]

    if np.any(np.diag(A) == 0):
        raise ValueError("Hay ceros en la diagonal de A; reordena las ecuaciones")

    x = np.zeros(n) if x0 is None else np.asarray(x0, dtype=float).copy()
    tabla = [{"iteración": 0, **{f"x{i + 1}": x[i] for i in range(n)}, "error": None}]
    convergio = False

    for k in range(1, max_iter + 1):
        x_anterior = x.copy()
        for i in range(n):
            # Jacobi usa SOLO los valores de x_anterior (iteración k-1)
            suma = A[i, :i] @ x_anterior[:i] + A[i, i + 1:] @ x_anterior[i + 1:]
            x[i] = (b[i] - suma) / A[i, i]

        error = float(np.linalg.norm(x - x_anterior, np.inf))
        tabla.append({"iteración": k, **{f"x{i + 1}": x[i] for i in range(n)},
                      "error": error})

        if not np.all(np.isfinite(x)):
            break
        if error < tol:
            convergio = True
            break

    return {
        "x": x,
        "iteraciones": len(tabla) - 1,
        "convergio": convergio,
        "diagonal_dominante": es_diagonal_dominante(A),
        "tabla": tabla,
        "residuo": float(np.linalg.norm(A @ x - b, np.inf)),
    }