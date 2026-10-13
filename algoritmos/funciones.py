"""Convierte el texto que escribe el usuario en una función evaluable.

Se usa sympy en lugar de eval para no ejecutar código arbitrario.
Lo comparten todos los métodos numéricos.

Acepta notación natural además de la de Python:
  2x, 3sin(x), (x+1)(x-1)   -> multiplicación implícita
  x^2, x²                   -> potencia
  ln, log10, sen, raiz      -> alias de funciones
  π, e, √, ×, ÷, −          -> símbolos del teclado
"""
import math
from tokenize import TokenError

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x = sp.Symbol("x")
y = sp.Symbol("y")

TRANSFORMACIONES = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

# Nombres que el usuario puede escribir y a qué equivalen en sympy
NOMBRES = {
    "x": x,
    "e": sp.E,
    "pi": sp.pi,
    "ln": sp.log,
    "log10": lambda z: sp.log(z, 10),
    "sen": sp.sin,
    "raiz": sp.sqrt,
    "abs": sp.Abs,
}

# Símbolos unicode que se reemplazan antes de interpretar
REEMPLAZOS = {
    "π": " pi ",
    "√": " sqrt ",
    "×": "*",
    "·": "*",
    "÷": "/",
    "−": "-",
    "²": "^2",
    "³": "^3",
}


def _normalizar(texto: str) -> str:
    limpio = texto.strip()
    for simbolo, equivalente in REEMPLAZOS.items():
        limpio = limpio.replace(simbolo, equivalente)
    return limpio


def _parsear(limpio: str, nombres: dict, texto: str):
    try:
        expresion = parse_expr(limpio, local_dict=nombres,
                               transformations=TRANSFORMACIONES)
    except (sp.SympifyError, SyntaxError, TypeError, AttributeError,
            NameError, ValueError, TokenError):
        raise ValueError(f"No se pudo interpretar la función: '{texto}'")

    if not isinstance(expresion, sp.Expr):
        raise ValueError(f"No se pudo interpretar la función: '{texto}'")
    return expresion


def interpretar(texto: str, con_y: bool = False):
    """Convierte el texto en una expresión de sympy que depende solo de x
    (o de x e y si con_y, para las ecuaciones diferenciales y' = f(x, y)).

    Lanza ValueError si el texto no es una función válida.
    """
    variables = "x e y" if con_y else "x"
    limpio = _normalizar(texto)
    if not limpio:
        raise ValueError(f"Escribe una función de {variables}")

    nombres = {**NOMBRES, "y": y} if con_y else NOMBRES
    expresion = _parsear(limpio, nombres, texto)

    if expresion.free_symbols - ({x, y} if con_y else {x}):
        raise ValueError(f"La función solo puede depender de {variables}")

    if expresion.has(sp.I):
        raise ValueError("La función no puede tener números imaginarios")

    return expresion


def interpretar_numero(texto: str):
    """Convierte una celda como '1/3', '√2', '2π' o '2,5' en (valor, expresion).

    Lo usan las tablas de sistemas lineales. La coma se toma como decimal.
    Lanza ValueError si la celda está vacía o no es un número real.
    """
    limpio = _normalizar(str(texto)).replace(",", ".")
    if not limpio:
        raise ValueError("está vacía")

    try:
        expresion = _parsear(limpio, NOMBRES, texto)
    except ValueError:
        raise ValueError("no es un número válido")
    if expresion.free_symbols:
        raise ValueError("debe ser un número, sin variables")

    valor = complex(expresion.evalf())
    if valor.imag != 0 or not math.isfinite(valor.real):
        raise ValueError("debe ser un número real")
    return valor.real, expresion


def crear_funcion(texto: str):
    """Recibe algo como 'x^3 - x - 2' y devuelve (f, expresion).

    f es una función de Python que recibe floats o arrays de numpy.
    Lanza ValueError si el texto no es una función válida de x.
    """
    expresion = interpretar(texto)
    f = sp.lambdify(x, expresion, "numpy")
    return f, expresion


def crear_funcion_xy(texto: str):
    """Recibe algo como 'x + y' y devuelve (f, expresion) con f(x, y).

    Lo usan los métodos de ecuaciones diferenciales (y' = f(x, y)).
    Lanza ValueError si el texto no es una función válida de x e y.
    """
    expresion = interpretar(texto, con_y=True)
    f = sp.lambdify((x, y), expresion, "numpy")
    return f, expresion


def derivar(expresion):
    """Deriva simbólicamente la expresión. Devuelve (f', expresion_derivada)."""
    derivada = sp.diff(expresion, x)
    return sp.lambdify(x, derivada, "numpy"), derivada
