"""Pantalla de integración por sumas superiores e inferiores (Darboux).

El cálculo está en algoritmos/integracion/riemann.py.
"""
import numpy as np
import pandas as pd
import streamlit as st

from algoritmos.integracion.riemann import resolver_riemann
from interfaces.integracion.componentes import entrada_integral, mostrar_tabla
from interfaces.notacion import texto_a_latex


def mostrar():
    st.header("Sumas superiores e inferiores")
    st.caption("En cada subintervalo toma el mínimo mᵢ y el máximo Mᵢ de f "
               "y acota la integral: Σ mᵢ·h ≤ ∫f ≤ Σ Mᵢ·h.")
    st.latex(r"I_{inf} = h\sum_{i=1}^{n} m_i \le \int_a^b f(x)\,dx "
             r"\le h\sum_{i=1}^{n} M_i = I_{sup}")

    texto, a, b, n = entrada_integral("f_riemann", n_inicial=10, paso_n=1)

    if not st.button("Calcular integral", type="primary"):
        return

    try:
        r = resolver_riemann(texto, a, b, n)
    except ValueError as e:
        st.error(str(e))
        return

    st.success(f"{r['suma_inferior']:.10f} ≤ ∫ f(x) dx ≤ {r['suma_superior']:.10f}")
    st.latex(rf"\int_{{{a:g}}}^{{{b:g}}} {texto_a_latex(texto)[0]} \, dx")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Suma inferior", f"{r['suma_inferior']:.10f}")
    m2.metric("Suma superior", f"{r['suma_superior']:.10f}")
    m3.metric("Estimación (promedio)", f"{r['estimacion']:.10f}")
    m4.metric("Ancho (I_sup − I_inf)", f"{r['acotamiento']:.2e}")

    st.metric("Referencia (quad)",
              "—" if r["referencia"] is None else f"{r['referencia']:.10f}")

    _graficar_escalones(r, a)
    mostrar_tabla(r["tabla"])


def _graficar_escalones(r, a):
    """Grafica f junto con las funciones escalón inferior y superior."""
    tabla = r["tabla"]
    n = len(tabla)
    h = r["h"]
    xs = np.linspace(tabla[0]["aᵢ"], tabla[-1]["bᵢ"], 400)
    indices = np.clip(((xs - a) / h).astype(int), 0, n - 1)
    minimos = np.array([fila["mᵢ (mín)"] for fila in tabla])[indices]
    maximos = np.array([fila["Mᵢ (máx)"] for fila in tabla])[indices]
    with np.errstate(all="ignore"):
        ys = np.broadcast_to(r["f"](xs), xs.shape).astype(float)
    st.line_chart(pd.DataFrame({"f(x)": ys, "escalón inferior": minimos,
                                "escalón superior": maximos, "y = 0": 0.0}, index=xs))