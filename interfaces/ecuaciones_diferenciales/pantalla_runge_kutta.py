"""Pantalla del método de Runge-Kutta 4. El cálculo está en algoritmos/ecuaciones_diferenciales/runge_kutta.py."""
import streamlit as st

from algoritmos.ecuaciones_diferenciales.runge_kutta import resolver_runge_kutta
from interfaces.ecuaciones_diferenciales.componentes import entrada_pvi, mostrar_resultado


def mostrar():
    st.header("Método de Runge-Kutta (orden 4)")
    st.caption("Promedia cuatro pendientes dentro de cada paso. "
               "El error global es proporcional a h⁴.")
    st.latex(r"\begin{aligned}"
             r"k_1 &= f(x_i, y_i) & k_2 &= f\left(x_i + \tfrac{h}{2},\ y_i + \tfrac{h}{2}k_1\right)\\"
             r"k_3 &= f\left(x_i + \tfrac{h}{2},\ y_i + \tfrac{h}{2}k_2\right) & "
             r"k_4 &= f(x_i + h,\ y_i + h\,k_3)"
             r"\end{aligned}")
    st.latex(r"y_{i+1} = y_i + \frac{h}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)")

    texto, x0, y0, xf, n, texto_exacta = entrada_pvi("f_rk4")

    if not st.button("Resolver", type="primary"):
        return

    try:
        r = resolver_runge_kutta(texto, x0, y0, xf, n, texto_exacta)
    except ValueError as e:
        st.error(str(e))
        return

    mostrar_resultado(r, texto, x0, y0, xf)
