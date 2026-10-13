"""Entrada de f(x) con el teclado matemático (interfaces/teclado.py).

Lo usan todas las pantallas de raíces. Se ve la función tal cual se
escribe, en notación matemática y con un cursor que se mueve con ← →.
El texto crudo (lo que lee el programa) queda en un desplegable cerrado
para quien prefiera escribir con el teclado del computador.
"""
import streamlit as st

from algoritmos.funciones import interpretar
from interfaces import teclado
from interfaces.notacion import texto_a_latex


def pedir_funcion(etiqueta: str, valor_inicial: str, clave: str,
                  con_y: bool = False) -> str:
    """Dibuja la función en notación matemática y el teclado.

    con_y permite usar y además de x (ecuaciones diferenciales).
    Devuelve el texto escrito.
    """
    teclado.preparar(clave, valor_inicial)
    texto, cursor = teclado.estado(clave)

    # Se muestra tal cual está escrita; si algo falla, solo se avisa
    latex, incompleta = texto_a_latex(texto, cursor)
    st.latex(f"{etiqueta} = {latex}")
    if incompleta:
        st.caption("⚠️ Falta completar la función")
    else:
        try:
            interpretar(texto, con_y=con_y)
        except ValueError as e:
            st.caption(f"⚠️ {e}")

    teclado.dibujar_teclado(clave, con_y=con_y)

    with st.expander("✏️ Escribir a mano"):
        st.text_input(
            etiqueta, key=clave, label_visibility="collapsed",
            on_change=teclado.al_escribir_a_mano, args=(clave,),
            help="Escribe como en la calculadora: 2x^2 + 3x − 1, sen(x) − x/2, "
                 "e^x − 3, √(x+1), ln(x). También funciona la sintaxis de Python (x**2).",
        )

    return st.session_state[clave]
