"""Sustitución hacia adelante (Ly = b) y hacia atrás (Ux = y).

Programadas a mano porque son los pasos de la solución de Ax = b por LU/LUP.
L debe ser triangular inferior y U triangular superior, ambas con diagonal
sin ceros.
"""
import numpy as np


def _validar_triangular(M, b, tipo: str):
    M = np.asarray(M, dtype=float)
    b = np.asarray(b, dtype=float).ravel()

    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("La matriz debe ser cuadrada")
    if b.shape[0] != M.shape[0]:
        raise ValueError("b debe tener tantas filas como la matriz")
    if not (np.all(np.isfinite(M)) and np.all(np.isfinite(b))):
        raise ValueError("Hay celdas vacías o valores no numéricos")
    if np.any(np.diag(M) == 0):
        raise ValueError(f"La diagonal de {tipo} tiene ceros: no se puede despejar")

    return M, b


def sustitucion_hacia_adelante(L, b) -> dict:
    """Resuelve Ly = b con L triangular inferior.

    y_i = (b_i − Σ_{j<i} L_ij·y_j) / L_ii,  i = 0, …, n−1
    """
    L, b = _validar_triangular(L, b, "L")
    n = L.shape[0]
    y = np.zeros(n)

    for i in range(n):
        y[i] = (b[i] - L[i, :i] @ y[:i]) / L[i, i]

    return {"y": y, "residuo": float(np.linalg.norm(L @ y - b, np.inf))}


def sustitucion_hacia_atras(U, y) -> dict:
    """Resuelve Ux = y con U triangular superior.

    x_i = (y_i − Σ_{j>i} U_ij·x_j) / U_ii,  i = n−1, …, 0
    """
    U, y = _validar_triangular(U, y, "U")
    n = U.shape[0]
    x = np.zeros(n)

    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - U[i, i + 1:] @ x[i + 1:]) / U[i, i]

    return {"x": x, "residuo": float(np.linalg.norm(U @ x - y, np.inf))}