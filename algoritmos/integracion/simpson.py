"""Fórmula compuesta de Simpson (1/3).

    ∫ₐᵇ f(x) dx ≈ h/3 · [f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + … + 4f(xₙ₋₁) + f(xₙ)]

con h = (b − a)/n y n par. La suma se hace con scipy.integrate.simpson,
que con un número impar de nodos (n par) es exactamente esta fórmula.
Cota del error: |E| ≤ (b − a)·h⁴/180 · max |f⁽⁴⁾(x)|.
"""
import numpy as np
from scipy.integrate import simpson

from algoritmos.integracion.elementos import maximo_derivada, preparar, valor_referencia


def resolver_simpson(texto_funcion: str, a: float, b: float, n: int) -> dict:
    """Aproxima la integral de f en [a, b] con n subintervalos (n par).

    Devuelve lo mismo que resolver_trapecio.
    Lanza ValueError si los datos de entrada no son válidos.
    """
    if n < 2 or n % 2:
        raise ValueError("Para Simpson n debe ser par (2, 4, 6, …)")

    f, expresion, h, xs, ys = preparar(texto_funcion, a, b, n)
    aproximacion = float(simpson(ys, x=xs))

    # Coeficientes 1, 4, 2, 4, …, 2, 4, 1 (multiplicados por h/3)
    coeficientes = np.where(np.arange(n + 1) % 2, 4.0, 2.0)
    coeficientes[[0, -1]] = 1.0

    referencia = valor_referencia(f, a, b)
    maximo, cuarta = maximo_derivada(expresion, 4, a, b)

    return {
        "aproximacion": aproximacion,
        "h": h,
        "referencia": referencia,
        "error": None if referencia is None else abs(referencia - aproximacion),
        "cota": None if maximo is None else (b - a) * h**4 / 180 * maximo,
        "derivada": cuarta,
        "expresion": expresion,
        "f": f,
        "tabla": [{"i": i, "xᵢ": xi, "f(xᵢ)": yi, "coeficiente": c}
                  for i, (xi, yi, c) in enumerate(zip(xs, ys, coeficientes))],
    }
