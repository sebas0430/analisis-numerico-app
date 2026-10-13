"""Método de Euler para y' = f(x, y), y(x₀) = y₀.

    yᵢ₊₁ = yᵢ + h·f(xᵢ, yᵢ)

Está programado a mano (SciPy no trae Euler de paso fijo) y guarda cada
paso para mostrarlo en una tabla. Error global O(h).
"""
import numpy as np

from algoritmos.ecuaciones_diferenciales.valor_inicial import (
    derivada_parcial_y,
    evaluar,
    preparar,
    solucion_referencia,
)


def resolver_euler(texto_funcion: str, x0: float, y0: float, xf: float,
                   n: int, texto_exacta: str = "") -> dict:
    """Aproxima y(x) en [x₀, x final] con n pasos de tamaño h.

    Devuelve un diccionario con xs, ys, h, la tabla de pasos, la solución
    de referencia (si se pudo calcular) y el error en cada punto.
    Lanza ValueError si los datos de entrada no son válidos.
    """
    f, expresion, h, xs = preparar(texto_funcion, x0, y0, xf, n)

    ys = np.empty(n + 1)
    ys[0] = y0
    pendientes = []
    for i in range(n):
        pendiente = evaluar(f, xs[i], ys[i])
        ys[i + 1] = ys[i] + h * pendiente
        pendientes.append(pendiente)
    pendientes.append(None)  # en el último punto ya no se avanza

    referencia, origen = solucion_referencia(f, x0, y0, xs, texto_exacta)
    tabla = [{"i": i, "xᵢ": xs[i], "f(xᵢ, yᵢ)": pendientes[i], "yᵢ": ys[i]}
             for i in range(n + 1)]
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
