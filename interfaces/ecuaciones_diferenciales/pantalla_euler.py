"""Pantalla del método de Euler. El cálculo está en algoritmos/ecuaciones_diferenciales/euler.py."""
import streamlit as st

from algoritmos.ecuaciones_diferenciales.euler import resolver_euler
from interfaces.ecuaciones_diferenciales.componentes import entrada_pvi, mostrar_resultado


def mostrar():
    st.header("Método de Euler")
    st.caption("Avanza por la recta tangente: la pendiente en cada paso es f(xᵢ, yᵢ). "
               "El error global es proporcional a h.")
    st.latex(r"y_{i+1} = y_i + h\,f(x_i, y_i)")

    texto, x0, y0, xf, n, texto_exacta = entrada_pvi("f_euler")

    if not st.button("Resolver", type="primary"):
        return

    try:
        r = resolver_euler(texto, x0, y0, xf, n, texto_exacta)
    except ValueError as e:
        st.error(str(e))
        return

    mostrar_resultado(r, texto, x0, y0, xf)
