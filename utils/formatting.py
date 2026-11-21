"""
utils/formatting.py — Formateo de números, unidades y LaTeX
============================================================

Ayudantes de presentación. La interfaz debe mostrar números legibles y con
el separador decimal español (coma), mientras que internamente SIEMPRE se
trabaja con punto decimal (estándar de Python/NumPy). Estas funciones solo
convierten a texto; nunca cambian el valor numérico.
"""

from __future__ import annotations

import sympy as sp


def fmt_es(value, ndec: int = 4) -> str:
    """Formatea un número con coma decimal española (ej. 9,2128)."""
    if value is None:
        return "—"
    try:
        texto = f"{float(value):.{ndec}f}"
    except (TypeError, ValueError):
        return str(value)
    return texto.replace(".", ",")


def fmt_sig(value, ndig: int = 4) -> str:
    """Formatea con cifras significativas (para valores muy grandes/pequeños)."""
    if value is None:
        return "—"
    try:
        return f"{float(value):.{ndig}g}"
    except (TypeError, ValueError):
        return str(value)


def fmt_capacitance(F) -> str:
    """Muestra una capacitancia en faradios con una unidad legible.

    Un faradio es una unidad ENORME: los capacitores reales suelen ser de
    microfaradios (µF), nanofaradios (nF) o picofaradios (pF).
    """
    F = float(F)
    if F >= 1:
        return f"{fmt_es(F, 3)} F"
    if F >= 1e-3:
        return f"{fmt_es(F * 1e3, 2)} mF"
    if F >= 1e-6:
        return f"{fmt_es(F * 1e6, 2)} µF"
    if F >= 1e-9:
        return f"{fmt_es(F * 1e9, 2)} nF"
    return f"{fmt_es(F * 1e12, 2)} pF"


def sympy_latex(expr) -> str:
    """Convierte una expresión SymPy a LaTeX (para renderizar con st.latex)."""
    try:
        return sp.latex(expr)
    except Exception:
        return str(expr)
