"""Barra lateral compartida: primero la unidad y luego el método."""
import streamlit as st

UNIDADES = {
    "Raíces de ecuaciones": [
        "Bisección",
        "Posición falsa",
        "Punto fijo",
        "Newton-Raphson",
        "Secante",
    ],
    "Sistemas lineales": [
        "Eliminación de Gauss",
        "Factorización LU",
        "Factorización LUP",
        "Gauss-Seidel",
    ],
    "Integración numérica": [
        "Trapecio compuesto",
        "Simpson compuesto",
    ],
    "Ecuaciones diferenciales": [
        "Euler",
        "Runge-Kutta 4",
    ],
}


def mostrar_barra_lateral() -> tuple[str, str]:
    """Dibuja la barra y devuelve (unidad, método) seleccionados."""
    with st.sidebar:
        st.title("Proyecto Numérico")
        unidad = st.selectbox("Unidad", list(UNIDADES))
        metodo = st.selectbox("Método", UNIDADES[unidad])
    return unidad, metodo
