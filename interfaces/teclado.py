"""Teclado matemático tipo GeoGebra con cursor, compartido por las pantallas.

Edita el texto guardado en st.session_state[clave]; la posición del cursor
va en st.session_state[clave_cursor(clave)]. Los botones escriben donde
está el cursor y ← → lo mueven.
"""
import re

import streamlit as st

# Teclas que no escriben texto sino que hacen una acción
RETROCESO, LIMPIAR, IZQUIERDA, DERECHA, CERRAR = "⌫", "Borrar", "←", "→", ")"

# (etiqueta del botón, texto que inserta). Lo que termina en '(' se cierra
# solo y deja el cursor adentro. None = tecla de acción (ver arriba).
# La pestaña 123 va en dos bloques: símbolos a la izquierda, números a la derecha.
TECLAS_SIMBOLOS = [
    [("x", "x"), ("π", "π"), ("e", "e"), ("x²", "^2"), ("xⁿ", "^(")],
    [("√", "sqrt("), ("|x|", "abs("), ("eˣ", "e^("), ("1/□", "1/("), ("ln", "ln(")],
    [("(", "("), (CERRAR, None), (".", "."), ("sin", "sin("), ("cos", "cos(")],
]

TECLAS_NUMEROS = [
    [("7", "7"), ("8", "8"), ("9", "9"), ("×", "*"), ("÷", "/"), (RETROCESO, None)],
    [("4", "4"), ("5", "5"), ("6", "6"), ("+", " + "), ("−", " - "), (LIMPIAR, None)],
    [("1", "1"), ("2", "2"), ("3", "3"), ("0", "0"), (IZQUIERDA, None), (DERECHA, None)],
]

TECLAS_FUNCIONES = [
    [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("sec", "sec("), ("csc", "csc(")],
    [("sin⁻¹", "asin("), ("cos⁻¹", "acos("), ("tan⁻¹", "atan("), ("cot", "cot("), ("exp", "exp(")],
    [("sinh", "sinh("), ("cosh", "cosh("), ("tanh", "tanh("), ("log₁₀", "log10("), ("ln", "ln(")],
]

# Un nombre de función con su '(' (sin(, sqrt() o el '^(' de un exponente
_APERTURA_FINAL = re.compile(r"(?:[A-Za-z_]\w*|\^)?\($", re.ASCII)
_APERTURA_INICIAL = re.compile(r"(?:[A-Za-z_]\w*|\^)?\(", re.ASCII)
_NOMBRE_FINAL = re.compile(r"[A-Za-z_]\w*$", re.ASCII)
_NOMBRE_INICIAL = re.compile(r"[A-Za-z_]\w*", re.ASCII)


def clave_cursor(clave: str) -> str:
    return f"{clave}__cursor"


def estado(clave: str):
    """Devuelve (texto, cursor)."""
    texto = st.session_state[clave]
    cursor = min(max(st.session_state[clave_cursor(clave)], 0), len(texto))
    return texto, cursor


def _guardar(clave: str, texto: str, cursor: int):
    st.session_state[clave] = texto
    st.session_state[clave_cursor(clave)] = cursor


def _insertar(clave: str, nuevo: str):
    texto, c = estado(clave)
    antes, despues = texto[:c], texto[c:]
    # Separa con espacio para que 'x' + 'sin(' no quede como 'xsin('
    if antes[-1:].isalpha() and nuevo[:1].isalpha():
        nuevo = " " + nuevo
    cierre = ")" if nuevo.endswith("(") else ""
    if not cierre and nuevo[-1:].isalpha() and despues[:1].isalpha():
        cierre = " "
    _guardar(clave, antes + nuevo + cierre + despues, c + len(nuevo))


def _cerrar_parentesis(clave: str):
    """Si ya hay un ')' adelante (lo puso el autocierre) solo lo salta."""
    texto, c = estado(clave)
    resto = texto[c:]
    if resto.lstrip().startswith(")"):
        _guardar(clave, texto, c + len(resto) - len(resto.lstrip()) + 1)
    else:
        _guardar(clave, texto[:c] + ")" + resto, c + 1)


def _parentesis_que_cierra(resto: str):
    """Índice en resto del ')' que cierra un '(' recién abierto, o None."""
    nivel = 0
    for i, ch in enumerate(resto):
        if ch == "(":
            nivel += 1
        elif ch == ")":
            if nivel == 0:
                return i
            nivel -= 1
    return None


def _retroceso(clave: str):
    """Borra lo que está antes del cursor: una función entera (sin(),
    un nombre o un carácter. Antes de un ')' entra al paréntesis."""
    texto, c = estado(clave)
    antes, despues = texto[:c].rstrip(), texto[c:]
    if not antes:
        return
    if antes.endswith(")"):
        _guardar(clave, texto, len(antes) - 1)
        return

    apertura = _APERTURA_FINAL.search(antes)
    if apertura:
        # Quita 'sin(' y su ')' pero deja lo que había adentro
        inicio = apertura.start()
        cierre = _parentesis_que_cierra(despues)
        if cierre is not None:
            despues = despues[:cierre] + despues[cierre + 1:]
    else:
        nombre = _NOMBRE_FINAL.search(antes)
        inicio = nombre.start() if nombre else len(antes) - 1

    izquierda = antes[:inicio].rstrip()
    _guardar(clave, izquierda + despues, len(izquierda))


def _limpiar(clave: str):
    _guardar(clave, "", 0)


def _mover_izquierda(clave: str):
    texto, c = estado(clave)
    antes = texto[:c].rstrip()
    coincidencia = _APERTURA_FINAL.search(antes) or _NOMBRE_FINAL.search(antes)
    if coincidencia and coincidencia.group() != "(":
        _guardar(clave, texto, coincidencia.start())
    else:
        _guardar(clave, texto, max(len(antes) - 1, 0))


def _mover_derecha(clave: str):
    texto, c = estado(clave)
    resto = texto[c:]
    c += len(resto) - len(resto.lstrip())
    resto = resto.lstrip()
    coincidencia = _APERTURA_INICIAL.match(resto) or _NOMBRE_INICIAL.match(resto)
    if coincidencia:
        c += coincidencia.end()
    elif resto:
        c += 1
    _guardar(clave, texto, c)


def al_escribir_a_mano(clave: str):
    """Callback para un st.text_input con la misma clave: cursor al final."""
    st.session_state[clave_cursor(clave)] = len(st.session_state[clave])


ACCIONES = {
    RETROCESO: (_retroceso, "retroceso"),
    LIMPIAR: (_limpiar, "limpiar"),
    IZQUIERDA: (_mover_izquierda, "izquierda"),
    DERECHA: (_mover_derecha, "derecha"),
    CERRAR: (_cerrar_parentesis, "cerrar"),
}

# Streamlit agrega la clase st-key-<key> a cada botón; así se colorean
# ⌫ (naranja), Borrar (rojo) y las flechas ← → (verde azulado)
ESTILOS = """
<style>
div[class*="st-key-"][class*="-retroceso"] button {
    background-color: #f59e0b; border-color: #f59e0b; color: #1f1f1f;
}
div[class*="st-key-"][class*="-limpiar"] button {
    background-color: #dc2626; border-color: #dc2626; color: #ffffff;
}
div[class*="st-key-"][class*="-izquierda"] button,
div[class*="st-key-"][class*="-derecha"] button {
    background-color: #0d9488; border-color: #0d9488; color: #ffffff;
}
div[class*="st-key-"][class*="-retroceso"] button:hover,
div[class*="st-key-"][class*="-limpiar"] button:hover,
div[class*="st-key-"][class*="-izquierda"] button:hover,
div[class*="st-key-"][class*="-derecha"] button:hover {
    filter: brightness(1.15); color: inherit;
}
</style>
"""


def _dibujar_teclas(filas, clave: str, pestana: str, deshabilitadas):
    for i, fila in enumerate(filas):
        columnas = st.columns(len(fila), gap="small")
        for j, (etiqueta, texto) in enumerate(fila):
            if texto is None:
                accion, nombre = ACCIONES[etiqueta]
                args = (clave,)
            else:
                accion, args, nombre = _insertar, (clave, texto), f"{i}_{j}"
            columnas[j].button(etiqueta, key=f"{clave}-{pestana}-{nombre}",
                               on_click=accion, args=args, width="stretch",
                               disabled=etiqueta in deshabilitadas)


def preparar(clave: str, valor_inicial: str):
    """Crea el texto y el cursor (al final) si aún no existen."""
    st.session_state.setdefault(clave, valor_inicial)
    st.session_state.setdefault(clave_cursor(clave), len(valor_inicial))


def fijar_texto(clave: str, texto: str):
    """Reemplaza el texto y deja el cursor al final."""
    _guardar(clave, texto, len(texto))


def dibujar_teclado(clave: str, deshabilitadas=frozenset(), con_y: bool = False):
    """Dibuja las pestañas 123 y f(x). deshabilitadas: etiquetas a desactivar.

    con_y agrega la tecla y junto a x (para y' = f(x, y)).
    """
    st.markdown(ESTILOS, unsafe_allow_html=True)
    simbolos_teclas = TECLAS_SIMBOLOS
    if con_y:
        primera = TECLAS_SIMBOLOS[0]
        simbolos_teclas = [[primera[0], ("y", "y"), *primera[1:]], *TECLAS_SIMBOLOS[1:]]
    pestana_123, pestana_fx = st.tabs(["123", "f(x)"])
    with pestana_123:
        simbolos, numeros = st.columns([5, 6], gap="xlarge")
        with simbolos:
            _dibujar_teclas(simbolos_teclas, clave, "simbolos", deshabilitadas)
        with numeros:
            _dibujar_teclas(TECLAS_NUMEROS, clave, "numeros", deshabilitadas)
    with pestana_fx:
        _dibujar_teclas(TECLAS_FUNCIONES, clave, "fx", deshabilitadas)
