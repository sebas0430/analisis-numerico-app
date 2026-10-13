"""Pantalla de la regla compuesta de Simpson. El cálculo está en algoritmos/integracion/simpson.py."""
import numpy as np
import streamlit as st

from algoritmos.integracion.simpson import resolver_simpson
from interfaces.integracion.componentes import (
    entrada_integral,
    graficar,
    mostrar_resultado,
    mostrar_tabla,
)


def _parabolas(nodos_x, nodos_y):
    """Función que evalúa la parábola por cada trío de nodos (x₂ₖ, x₂ₖ₊₁, x₂ₖ₊₂)."""
    nodos_x, nodos_y = np.asarray(nodos_x), np.asarray(nodos_y)

    def evaluar(xs):
        ys = np.empty_like(xs)
        for k in range(0, len(nodos_x) - 1, 2):
            tramo = (xs >= nodos_x[k]) & (xs <= nodos_x[k + 2])
            coef = np.polyfit(nodos_x[k:k + 3], nodos_y[k:k + 3], 2)
            ys[tramo] = np.polyval(coef, xs[tramo])
        return ys

    return evaluar


def mostrar():
    st.header("Regla compuesta de Simpson")
    st.caption("Divide [a, b] en n partes (n par) y en cada par de subintervalos "
               "reemplaza f por la parábola que pasa por sus tres puntos.")
    st.latex(r"\int_a^b f(x)\,dx \approx \frac{h}{3}\Big[f(x_0) + "
             r"4\sum_{i\ \mathrm{impar}} f(x_i) + 2\sum_{i\ \mathrm{par}} f(x_i) + f(x_n)\Big]")

    texto, a, b, n = entrada_integral("f_simpson", n_inicial=10, paso_n=2)

    if not st.button("Calcular integral", type="primary"):
        return

    try:
        r = resolver_simpson(texto, a, b, n)
    except ValueError as e:
        st.error(str(e))
        return

    mostrar_resultado(r, texto, a, b, orden=4)
    st.latex(r"|E| \le \frac{(b-a)\,h^4}{180}\max_{a\le x\le b}|f^{(4)}(x)|")

    nodos_x = [fila["xᵢ"] for fila in r["tabla"]]
    nodos_y = [fila["f(xᵢ)"] for fila in r["tabla"]]
    graficar(r["f"], nodos_x, _parabolas(nodos_x, nodos_y))
    mostrar_tabla(r["tabla"])
