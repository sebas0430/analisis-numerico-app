"""Pantalla de la regla compuesta del trapecio. El cálculo está en algoritmos/integracion/trapecio.py."""
import numpy as np
import streamlit as st

from algoritmos.integracion.trapecio import resolver_trapecio
from interfaces.integracion.componentes import (
    entrada_integral,
    graficar,
    mostrar_resultado,
    mostrar_tabla,
)


def mostrar():
    st.header("Regla compuesta del trapecio")
    st.caption("Divide [a, b] en n partes de ancho h y en cada una reemplaza f "
               "por la recta que une sus extremos.")
    st.latex(r"\int_a^b f(x)\,dx \approx \frac{h}{2}\Big[f(x_0) + "
             r"2\sum_{i=1}^{n-1} f(x_i) + f(x_n)\Big]")

    texto, a, b, n = entrada_integral("f_trapecio", n_inicial=10, paso_n=1)

    if not st.button("Calcular integral", type="primary"):
        return

    try:
        r = resolver_trapecio(texto, a, b, n)
    except ValueError as e:
        st.error(str(e))
        return

    mostrar_resultado(r, texto, a, b, orden=2)
    st.latex(r"|E| \le \frac{(b-a)\,h^2}{12}\max_{a\le x\le b}|f''(x)|")

    nodos_x = [fila["xᵢ"] for fila in r["tabla"]]
    nodos_y = [fila["f(xᵢ)"] for fila in r["tabla"]]
    graficar(r["f"], nodos_x, lambda xs: np.interp(xs, nodos_x, nodos_y))
    mostrar_tabla(r["tabla"])
