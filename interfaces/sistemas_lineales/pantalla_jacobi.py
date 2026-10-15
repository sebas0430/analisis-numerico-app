"""Pantalla del método de Jacobi. El cálculo está en algoritmos/sistemas_lineales/jacobi.py."""
import pandas as pd
import streamlit as st

from algoritmos.sistemas_lineales.jacobi import resolver_jacobi
from interfaces.sistemas_lineales.componentes import entrada_sistema, mostrar_solucion


def mostrar():
    st.header("Método de Jacobi")
    st.caption("Método iterativo: en cada paso despeja xᵢ de la ecuación i usando "
               "únicamente los valores de la iteración anterior. "
               "Converge si A es diagonalmente dominante.")

    A, b = entrada_sistema("jacobi")

    col1, col2 = st.columns(2)
    tol = col1.number_input("Tolerancia", value=1e-6, min_value=1e-15, format="%.1e")
    max_iter = col2.number_input("Máx. iteraciones", value=100, min_value=1, step=1)
    st.caption("Valor inicial: x⁽⁰⁾ = 0")

    if not st.button("Resolver", type="primary"):
        return

    try:
        r = resolver_jacobi(A, b, tol=tol, max_iter=int(max_iter))
    except ValueError as e:
        st.error(str(e))
        return

    if not r["diagonal_dominante"]:
        st.info("A no es diagonalmente dominante: la convergencia no está garantizada. "
                "Reordenar las ecuaciones puede ayudar.")

    if r["convergio"]:
        mostrar_solucion(r["x"], r["residuo"])
    else:
        st.warning(f"No convergió en {r['iteraciones']} iteraciones.")

    st.metric("Iteraciones", r["iteraciones"])

    with st.expander("Ver iteraciones"):
        st.dataframe(pd.DataFrame(r["tabla"]), hide_index=True)