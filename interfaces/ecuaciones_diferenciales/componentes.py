"""Partes compartidas por las pantallas de ecuaciones diferenciales (Euler y RK4)."""
import pandas as pd
import streamlit as st
import sympy as sp

from algoritmos.funciones import interpretar
from interfaces.notacion import texto_a_latex
from interfaces.raices.entrada_funcion import pedir_funcion


def entrada_pvi(clave: str):
    """Pide f(x, y), x₀, y₀, x final, n y (opcional) la solución exacta.

    Valores iniciales: el ejemplo clásico de Burden
    y' = y − x² + 1, y(0) = 0.5 en [0, 2], cuya solución es (x+1)² − 0.5eˣ.
    Devuelve (texto, x0, y0, xf, n, texto_exacta).
    """
    texto = pedir_funcion("y' = f(x, y)", "y - x^2 + 1", clave=clave, con_y=True)

    col1, col2 = st.columns(2)
    x0 = col1.number_input("x₀", value=0.0, format="%.4f", key=f"{clave}_x0")
    y0 = col2.number_input("y₀ = y(x₀)", value=0.5, format="%.4f", key=f"{clave}_y0")

    col3, col4 = st.columns(2)
    xf = col3.number_input("x final", value=2.0, format="%.4f", key=f"{clave}_xf")
    n = col4.number_input("n (pasos)", value=10, min_value=1, step=1, key=f"{clave}_n")

    with st.expander("Solución exacta y(x) (opcional, para comparar)"):
        texto_exacta = st.text_input(
            "y(x)", key=f"{clave}_exacta", placeholder="(x+1)^2 - 0.5e^x",
            help="Si la dejas vacía se compara con scipy.integrate.solve_ivp.")
        if texto_exacta.strip():
            try:
                interpretar(texto_exacta)
                st.latex(f"y(x) = {texto_a_latex(texto_exacta)[0]}")
            except ValueError as e:
                st.caption(f"⚠️ {e}")

    return texto, x0, y0, xf, int(n), texto_exacta


def mostrar_resultado(r: dict, texto: str, x0: float, y0: float, xf: float):
    """Muestra y(x final), el error, la condición de unicidad, la gráfica y la tabla."""
    st.success(f"y({xf:g}) ≈ {r['y_final']:.10f}")
    st.latex(rf"y' = {texto_a_latex(texto)[0]}, \quad y({x0:g}) = {y0:g}")

    m1, m2, m3 = st.columns(3)
    m1.metric("h", f"{r['h']:.6g}")
    if r["referencia"] is None:
        m2.metric("Referencia", "—")
        m3.metric("Error en x final", "—")
        st.caption(f"Sin comparación: {r['origen_referencia']}.")
    else:
        m2.metric(f"Referencia ({r['origen_referencia']})", f"{r['referencia'][-1]:.10f}")
        m3.metric("Error en x final", f"{r['error_final']:.2e}")

    # Teoría elemental del PVI: existencia y unicidad
    st.latex(rf"\frac{{\partial f}}{{\partial y}} = {sp.latex(r['df_dy'])}")
    st.caption("Si f y ∂f/∂y son continuas en una región que contiene a (x₀, y₀), "
               "el problema de valor inicial tiene solución única.")

    datos = {"aproximación": r["ys"]}
    if r["referencia"] is not None:
        datos["referencia"] = r["referencia"]
    st.line_chart(pd.DataFrame(datos, index=r["xs"]))

    with st.expander("Ver pasos"):
        st.dataframe(pd.DataFrame(r["tabla"]), hide_index=True)
