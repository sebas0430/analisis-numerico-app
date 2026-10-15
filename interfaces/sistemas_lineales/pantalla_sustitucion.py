"""Pantalla de sustitución hacia adelante y hacia atrás.

El cálculo está en algoritmos/sistemas_lineales/sustitucion.py.
Escribe la matriz triangular (L con unos o cualquier diagonal, o U) y el
vector del lado derecho; la pantalla verifica la forma triangular.
"""
import numpy as np
import streamlit as st

from algoritmos.sistemas_lineales.sustitucion import (
    sustitucion_hacia_adelante,
    sustitucion_hacia_atras,
)
from interfaces.sistemas_lineales.componentes import (
    entrada_sistema,
    mostrar_matriz,
    mostrar_vector,
)


def mostrar():
    st.header("Sustitución hacia adelante y hacia atrás")
    st.caption("Resuelve Ly = b (L triangular inferior, hacia adelante) o "
               "Ux = y (U triangular superior, hacia atrás). "
               "Son los dos pasos de la solución de Ax = b por LU/LUP.")

    direccion = st.radio("Dirección",
                         ["Hacia adelante (Ly = b, L inferior)",
                          "Hacia atrás (Ux = y, U superior)"])
    st.caption("Escribe la matriz triangular en A y el vector del lado derecho en b.")
    A, b = entrada_sistema("sust")

    if not st.button("Resolver", type="primary"):
        return

    adelante = direccion.startswith("Hacia adelante")
    M = np.nan_to_num(A, nan=0.0)

    if adelante and not np.allclose(np.triu(M, 1), 0):
        st.error("La matriz no es triangular inferior: hay valores sobre la diagonal.")
        return
    if not adelante and not np.allclose(np.tril(M, -1), 0):
        st.error("La matriz no es triangular superior: hay valores bajo la diagonal.")
        return

    try:
        if adelante:
            r = sustitucion_hacia_adelante(M, b)
        else:
            r = sustitucion_hacia_atras(M, b)
    except ValueError as e:
        st.error(str(e))
        return

    if adelante:
        st.success("Solución: " + ", ".join(f"y{i + 1} = {v:.6g}"
                                             for i, v in enumerate(r["y"])))
        st.caption(f"Residuo ‖Ly − b‖∞ = {r['residuo']:.2e}")
        st.subheader("Matriz y solución")
        mostrar_matriz("L", M)
        mostrar_vector("y", r["y"])
        st.latex(r"y_i = \frac{b_i - \sum_{j<i} L_{ij}\,y_j}{L_{ii}}")
    else:
        st.success("Solución: " + ", ".join(f"x{i + 1} = {v:.6g}"
                                             for i, v in enumerate(r["x"])))
        st.caption(f"Residuo ‖Ux − y‖∞ = {r['residuo']:.2e}")
        st.subheader("Matriz y solución")
        mostrar_matriz("U", M)
        mostrar_vector("x", r["x"])
        st.latex(r"x_i = \frac{y_i - \sum_{j>i} U_{ij}\,x_j}{U_{ii}}")