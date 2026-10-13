"""Elementos comunes de integración numérica (lo comparten trapecio y Simpson).

- Validar [a, b] y n, y armar la partición x_i = a + i·h.
- Valor de referencia con scipy.integrate.quad para medir el error real.
- Máximo de |f⁽ᵏ⁾| en [a, b] para la cota teórica del error.
"""
import warnings

import numpy as np
import sympy as sp
from scipy.integrate import quad

from algoritmos.funciones import crear_funcion, x


def preparar(texto_funcion: str, a: float, b: float, n: int):
    """Devuelve (f, expresion, h, xs, ys) con la partición de [a, b] en n partes.

    Lanza ValueError si los datos no son válidos o f no es finita en algún nodo.
    """
    if a >= b:
        raise ValueError("a debe ser menor que b")
    if n < 1:
        raise ValueError("n debe ser al menos 1")

    f, expresion = crear_funcion(texto_funcion)
    h = (b - a) / n
    xs = np.linspace(a, b, n + 1)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(f(xs), xs.shape).astype(float)

    if not np.all(np.isfinite(ys)):
        malo = xs[~np.isfinite(ys)][0]
        raise ValueError(f"f no está definida (o no es finita) en x = {malo:.6g}")
    return f, expresion, h, xs, ys


def valor_referencia(f, a: float, b: float):
    """Integral con scipy.integrate.quad (adaptativo), o None si no converge."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            valor, _ = quad(f, a, b, limit=200)
        except Exception:
            return None
    return float(valor) if np.isfinite(valor) else None


def maximo_derivada(expresion, orden: int, a: float, b: float):
    """Aproxima max |f⁽orden⁾(x)| en [a, b] evaluando en 1001 puntos.

    Devuelve (maximo, derivada) o (None, derivada) si no se puede evaluar.
    """
    derivada = sp.diff(expresion, x, orden)
    df = sp.lambdify(x, derivada, "numpy")
    puntos = np.linspace(a, b, 1001)
    with np.errstate(all="ignore"):
        valores = np.abs(np.broadcast_to(df(puntos), puntos.shape).astype(float))
    if not np.all(np.isfinite(valores)):
        return None, derivada
    return float(np.max(valores)), derivada
