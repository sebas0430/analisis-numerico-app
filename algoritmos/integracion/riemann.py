"""Integración por sumas superiores e inferiores (sumas de Darboux).

En cada subintervalo [x_i, x_{i+1}]:
    Suma inferior = Σ m_i·h,   m_i = mín f en el subintervalo
    Suma superior = Σ M_i·h,   M_i = máx f en el subintervalo

Los extremos m_i y M_i se aproximan muestreando cada subintervalo con
101 puntos. La integral exacta queda acotada: I_inf ≤ ∫f ≤ I_sup.
"""
import numpy as np

from algoritmos.integracion.elementos import preparar, valor_referencia


def resolver_riemann(texto_funcion: str, a: float, b: float, n: int,
                     muestras: int = 101) -> dict:
    """Aproxima la integral de f en [a, b] con n subintervalos.

    Devuelve las sumas inferior y superior, el ancho del intervalo que
    encierra a la integral (superior − inferior), el valor de referencia
    (quad) y la tabla de mínimos y máximos por subintervalo.
    """
    f, expresion, h, xs, ys = preparar(texto_funcion, a, b, n)

    inferior = 0.0
    superior = 0.0
    tabla = []

    for i in range(n):
        puntos = np.linspace(xs[i], xs[i + 1], muestras)
        with np.errstate(all="ignore"):
            valores = np.broadcast_to(f(puntos), puntos.shape).astype(float)
        valores = valores[np.isfinite(valores)]
        if valores.size == 0:
            raise ValueError(
                f"f no está definida en el subintervalo [{xs[i]:.6g}, {xs[i+1]:.6g}]")

        minimo = float(np.min(valores))
        maximo = float(np.max(valores))
        inferior += minimo * h
        superior += maximo * h
        tabla.append({"i": i + 1, "aᵢ": xs[i], "bᵢ": xs[i + 1],
                      "mᵢ (mín)": minimo, "Mᵢ (máx)": maximo,
                      "mᵢ·h": minimo * h, "Mᵢ·h": maximo * h})

    estimacion = (inferior + superior) / 2
    referencia = valor_referencia(f, a, b)

    return {
        "suma_inferior": inferior,
        "suma_superior": superior,
        "estimacion": estimacion,
        "h": h,
        "acotamiento": superior - inferior,
        "referencia": referencia,
        "error": None if referencia is None else abs(referencia - estimacion),
        "expresion": expresion,
        "f": f,
        "tabla": tabla,
    }