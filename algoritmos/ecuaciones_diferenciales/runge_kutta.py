"""Método de Runge-Kutta de orden 4 (clásico) para y' = f(x, y), y(x₀) = y₀.

    k₁ = f(xᵢ, yᵢ)
    k₂ = f(xᵢ + h/2, yᵢ + h·k₁/2)
    k₃ = f(xᵢ + h/2, yᵢ + h·k₂/2)
    k₄ = f(xᵢ + h,   yᵢ + h·k₃)
    yᵢ₊₁ = yᵢ + h/6 · (k₁ + 2k₂ + 2k₃ + k₄)

Está programado a mano: solve_ivp(method="RK45") es adaptativo y no es el
RK4 de paso fijo que se ve en clase. Error global O(h⁴).
"""
import numpy as np

from algoritmos.ecuaciones_diferenciales.valor_inicial import (
    derivada_parcial_y,
    evaluar,
    preparar,
    solucion_referencia,
)


def resolver_runge_kutta(texto_funcion: str, x0: float, y0: float, xf: float,
                         n: int, texto_exacta: str = "") -> dict:
    """Aproxima y(x) en [x₀, x final] con n pasos de tamaño h.

    Devuelve lo mismo que resolver_euler; la tabla incluye k₁…k₄.
    Lanza ValueError si los datos de entrada no son válidos.
    """
    f, expresion, h, xs = preparar(texto_funcion, x0, y0, xf, n)

    ys = np.empty(n + 1)
    ys[0] = y0
    tabla = []
    for i in range(n):
        xi, yi = xs[i], ys[i]
        k1 = evaluar(f, xi, yi)
        k2 = evaluar(f, xi + h / 2, yi + h * k1 / 2)
        k3 = evaluar(f, xi + h / 2, yi + h * k2 / 2)
        k4 = evaluar(f, xi + h, yi + h * k3)
        ys[i + 1] = yi + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        tabla.append({"i": i, "xᵢ": xi, "yᵢ": yi,
                      "k₁": k1, "k₂": k2, "k₃": k3, "k₄": k4})
    tabla.append({"i": n, "xᵢ": xs[n], "yᵢ": ys[n],
                  "k₁": None, "k₂": None, "k₃": None, "k₄": None})

    referencia, origen = solucion_referencia(f, x0, y0, xs, texto_exacta)
    if referencia is not None:
        for fila, yr in zip(tabla, referencia):
            fila["y(xᵢ)"] = yr
            fila["|error|"] = abs(yr - fila["yᵢ"])

    return {
        "xs": xs,
        "ys": ys,
        "h": h,
        "y_final": float(ys[-1]),
        "referencia": referencia,
        "origen_referencia": origen,
        "error_final": None if referencia is None else float(abs(referencia[-1] - ys[-1])),
        "expresion": expresion,
        "df_dy": derivada_parcial_y(expresion),
        "tabla": tabla,
    }
