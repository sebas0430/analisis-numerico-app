"""Fórmula compuesta del trapecio.

    ∫ₐᵇ f(x) dx ≈ h/2 · [f(x₀) + 2f(x₁) + … + 2f(xₙ₋₁) + f(xₙ)],  h = (b − a)/n

La suma se hace con scipy.integrate.trapezoid sobre los nodos.
Cota del error: |E| ≤ (b − a)·h²/12 · max |f''(x)|.
"""
import numpy as np
from scipy.integrate import trapezoid

from algoritmos.integracion.elementos import maximo_derivada, preparar, valor_referencia


def resolver_trapecio(texto_funcion: str, a: float, b: float, n: int) -> dict:
    """Aproxima la integral de f en [a, b] con n subintervalos.

    Devuelve un diccionario con la aproximación, h, la tabla de nodos,
    el valor de referencia (quad), el error real y la cota teórica.
    Lanza ValueError si los datos de entrada no son válidos.
    """
    f, expresion, h, xs, ys = preparar(texto_funcion, a, b, n)
    aproximacion = float(trapezoid(ys, xs))

    # Coeficientes 1, 2, 2, …, 2, 1 (multiplicados por h/2)
    coeficientes = np.full(n + 1, 2.0)
    coeficientes[[0, -1]] = 1.0

    referencia = valor_referencia(f, a, b)
    maximo, segunda = maximo_derivada(expresion, 2, a, b)

    return {
        "aproximacion": aproximacion,
        "h": h,
        "referencia": referencia,
        "error": None if referencia is None else abs(referencia - aproximacion),
        "cota": None if maximo is None else (b - a) * h**2 / 12 * maximo,
        "derivada": segunda,
        "expresion": expresion,
        "f": f,
        "tabla": [{"i": i, "xᵢ": xi, "f(xᵢ)": yi, "coeficiente": c}
                  for i, (xi, yi, c) in enumerate(zip(xs, ys, coeficientes))],
    }
