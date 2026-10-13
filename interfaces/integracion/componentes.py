"""Partes compartidas por las pantallas de integración (trapecio y Simpson)."""
import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from interfaces.notacion import texto_a_latex
from interfaces.raices.entrada_funcion import pedir_funcion


def entrada_integral(clave: str, n_inicial: int, paso_n: int):
    """Pide f(x), a, b y n. Devuelve (texto, a, b, n)."""
    texto = pedir_funcion("f(x)", "e^(-x^2)", clave=clave)

    col1, col2, col3 = st.columns(3)
    a = col1.number_input("a", value=0.0, format="%.4f", key=f"{clave}_a")
    b = col2.number_input("b", value=1.0, format="%.4f", key=f"{clave}_b")
    n = col3.number_input("n (subintervalos)", value=n_inicial, min_value=paso_n,
                          step=paso_n, key=f"{clave}_n")
    return texto, a, b, int(n)


def mostrar_resultado(r: dict, texto: str, a: float, b: float, orden: int):
    """Muestra la aproximación, el error, la cota y la tabla de nodos.

    orden es el de la derivada que aparece en la cota (2 trapecio, 4 Simpson).
    """
    st.success(f"∫ f(x) dx ≈ {r['aproximacion']:.10f}")
    st.latex(rf"\int_{{{a:g}}}^{{{b:g}}} {texto_a_latex(texto)[0]} \, dx")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("h", f"{r['h']:.6g}")
    m2.metric("Referencia (quad)",
              "—" if r["referencia"] is None else f"{r['referencia']:.10f}")
    m3.metric("Error real", "—" if r["error"] is None else f"{r['error']:.2e}")
    m4.metric("Cota teórica", "—" if r["cota"] is None else f"{r['cota']:.2e}")

    prima = "''" if orden == 2 else "^{(4)}"
    st.latex(rf"f{prima}(x) = {sp.latex(r['derivada'])}")
    if r["cota"] is None:
        nombre = "f''" if orden == 2 else "f⁽⁴⁾"
        st.caption(f"No se pudo calcular la cota: {nombre} no es finita en todo [a, b].")


def graficar(f, xs_nodos, aproximacion_en):
    """Grafica f junto con la curva que la regla integra en su lugar."""
    xs = np.linspace(xs_nodos[0], xs_nodos[-1], 400)
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(f(xs), xs.shape).astype(float)
    st.line_chart(pd.DataFrame({"f(x)": ys, "aproximación": aproximacion_en(xs),
                                "y = 0": 0.0}, index=xs))


def mostrar_tabla(tabla):
    with st.expander("Ver nodos"):
        st.dataframe(pd.DataFrame(tabla), hide_index=True)
