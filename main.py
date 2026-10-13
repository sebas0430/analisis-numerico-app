"""Punto de entrada. Ejecutar con:  streamlit run main.py"""
import streamlit as st

from interfaces.barra_lateral import mostrar_barra_lateral
from interfaces.ecuaciones_diferenciales import pantalla_euler, pantalla_runge_kutta
from interfaces.integracion import pantalla_simpson, pantalla_trapecio
from interfaces.raices import (
    pantalla_biseccion,
    pantalla_newton,
    pantalla_posicion_falsa,
    pantalla_punto_fijo,
    pantalla_secante,
)
from interfaces.sistemas_lineales import (
    pantalla_gauss,
    pantalla_gauss_seidel,
    pantalla_lu,
    pantalla_lup,
)

st.set_page_config(page_title="Proyecto Numérico", layout="wide")

PANTALLAS = {
    "Raíces de ecuaciones": {
        "Bisección": pantalla_biseccion.mostrar,
        "Posición falsa": pantalla_posicion_falsa.mostrar,
        "Punto fijo": pantalla_punto_fijo.mostrar,
        "Newton-Raphson": pantalla_newton.mostrar,
        "Secante": pantalla_secante.mostrar,
    },
    "Sistemas lineales": {
        "Eliminación de Gauss": pantalla_gauss.mostrar,
        "Factorización LU": pantalla_lu.mostrar,
        "Factorización LUP": pantalla_lup.mostrar,
        "Gauss-Seidel": pantalla_gauss_seidel.mostrar,
    },
    "Integración numérica": {
        "Trapecio compuesto": pantalla_trapecio.mostrar,
        "Simpson compuesto": pantalla_simpson.mostrar,
    },
    "Ecuaciones diferenciales": {
        "Euler": pantalla_euler.mostrar,
        "Runge-Kutta 4": pantalla_runge_kutta.mostrar,
    },
}

unidad, metodo = mostrar_barra_lateral()
PANTALLAS[unidad][metodo]()
