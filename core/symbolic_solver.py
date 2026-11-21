"""
core/symbolic_solver.py — Resolución simbólica con SymPy
=========================================================

SymPy resuelve la ecuación diferencial de forma EXACTA (algebraica), sin
aproximaciones numéricas. Esto permite comprobar que el desarrollo "a mano"
del proyecto coincide con el resultado que produce un sistema de álgebra
computacional.

Cómo funciona por dentro: SymPy recibe la EDO como una igualdad
``Eq(derivada, lado_derecho)`` y la resuelve con ``dsolve``, que aplica
clasificadores de EDO (separables, lineales, exactas, etc.) y devuelve una
expresión simbólica. La condición inicial se pasa con ``ics={y(x0): y0}``
para obtener directamente la solución del problema de valor inicial.
"""

from __future__ import annotations

import sympy as sp


def _to_latex(expr) -> str:
    """Convierte una expresión simbólica a LaTeX para renderizar en la UI."""
    return sp.latex(expr)


def solve_rc(tau=0.4896, V0=9.2128) -> dict:
    """Resuelve simbólicamente el PVI del circuito RC en descarga.

    EDO:      dV/dt = -V/τ
    PVI:      V(0) = V₀
    Solución: V(t) = V₀·e^{-t/τ}
    """
    t = sp.symbols("t", real=True)
    V = sp.Function("V")
    tau_s, V0_s = sp.sympify(tau), sp.sympify(V0)

    # sp.Eq(Derivative(V(t), t), -V(t)/tau): expresa dV/dt = -V/τ
    ode = sp.Eq(sp.Derivative(V(t), t), -V(t) / tau_s)
    sol = sp.dsolve(ode, V(t), ics={V(0): V0_s})

    return {
        "ode": ode,
        "solution": sol,
        "rhs": sol.rhs,
        "latex_ode": _to_latex(ode),
        "latex_solution": _to_latex(sol),
    }


def solve_rl(R=4, L=2, E0=12, i0=0) -> dict:
    """Resuelve simbólicamente el PVI del circuito RL.

    EDO:      L·di/dt + R·i = E₀
    PVI:      i(0) = i₀
    Solución: i(t) = E₀/R + (i₀ - E₀/R)·e^{-(R/L)t}
    """
    t = sp.symbols("t", real=True)
    i = sp.Function("i")
    R_s, L_s, E0_s, i0_s = sp.sympify(R), sp.sympify(L), sp.sympify(E0), sp.sympify(i0)

    ode = sp.Eq(L_s * sp.Derivative(i(t), t) + R_s * i(t), E0_s)
    sol = sp.dsolve(ode, i(t), ics={i(0): i0_s})

    return {
        "ode": ode,
        "solution": sol,
        "rhs": sol.rhs,
        "latex_ode": _to_latex(ode),
        "latex_solution": _to_latex(sol),
    }


def solve_general(ode_rhs, y0, t0=0, t_symbol="t", y_name="y") -> dict:
    """Resuelve un PVI genérico  y'(t) = ode_rhs(y, t)  con  y(t0) = y0.

    `ode_rhs` es una expresión simbólica en la variable `t_symbol` y en la
    función `y_name(t)`. Devuelve la solución y su LaTeX. Útil para resolver
    EDO arbitrarias introducidas por el usuario en el módulo de validación.
    """
    t = sp.symbols(t_symbol, real=True)
    y = sp.Function(y_name)
    y0_s = sp.sympify(y0)
    rhs = sp.sympify(ode_rhs)
    # Sustituimos y_name(t) por y(t) si el usuario lo escribió con la letra.
    ode = sp.Eq(sp.Derivative(y(t), t), rhs)
    sol = sp.dsolve(ode, y(t), ics={y(t0): y0_s})
    return {"ode": ode, "solution": sol, "rhs": sol.rhs,
            "latex_ode": _to_latex(ode), "latex_solution": _to_latex(sol)}
