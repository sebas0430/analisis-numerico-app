"""Problema de valor inicial  y' = f(x, y),  y(x₀) = y₀  (lo comparten Euler y RK4).

- Valida los datos y arma la malla x_i = x₀ + i·h.
- Calcula ∂f/∂y: si f y ∂f/∂y son continuas cerca de (x₀, y₀), el PVI
  tiene solución única (teorema de existencia y unicidad).
- Solución de referencia con scipy.integrate.solve_ivp (tolerancia muy fina)
  o con la solución exacta que escriba el usuario, para medir el error.
"""
import warnings

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

from algoritmos.funciones import crear_funcion, crear_funcion_xy, y


def preparar(texto_funcion: str, x0: float, y0: float, xf: float, n: int):
    """Devuelve (f, expresion, h, xs). Lanza ValueError si algo no es válido."""
    if xf <= x0:
        raise ValueError("x final debe ser mayor que x₀")
    if n < 1:
        raise ValueError("n debe ser al menos 1")

    f, expresion = crear_funcion_xy(texto_funcion)
    h = (xf - x0) / n
    xs = x0 + h * np.arange(n + 1)
    return f, expresion, h, xs


def evaluar(f, xi: float, yi: float) -> float:
    """f(xᵢ, yᵢ) como float; ValueError si no es finita (la solución explotó)."""
    with np.errstate(all="ignore"):
        valor = float(f(xi, yi))
    if not np.isfinite(valor):
        raise ValueError(f"f(x, y) no es finita en x = {xi:.6g}, y = {yi:.6g}; "
                         "prueba con un h más pequeño o un intervalo más corto")
    return valor


def derivada_parcial_y(expresion):
    return sp.diff(expresion, y)


def solucion_referencia(f, x0: float, y0: float, xs, texto_exacta: str = ""):
    """Valores de y(xᵢ) para comparar y una etiqueta de dónde salen.

    Si el usuario escribió la solución exacta y(x) se usa esa; si no,
    solve_ivp con tolerancias finas. Devuelve (None, motivo) si no se puede.
    """
    if texto_exacta.strip():
        exacta, _ = crear_funcion(texto_exacta)
        with np.errstate(all="ignore"):
            valores = np.broadcast_to(exacta(xs), xs.shape).astype(float)
        if not np.all(np.isfinite(valores)):
            return None, "la solución exacta no es finita en toda la malla"
        return valores, "solución exacta"

    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore")
        sol = solve_ivp(lambda t, u: [f(t, u[0])], (xs[0], xs[-1]), [y0],
                        method="DOP853", t_eval=xs, rtol=1e-11, atol=1e-12)
    if not sol.success or sol.y.shape[1] != len(xs):
        return None, "solve_ivp no pudo resolver el problema"
    return sol.y[0], "scipy solve_ivp"
