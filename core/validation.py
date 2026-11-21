"""
core/validation.py — Comparación de soluciones y verificación de errores
=========================================================================

Este módulo cierra el círculo del proyecto: demuestra que la solución
analítica (hecha a mano / SymPy), la solución numérica (SciPy / RK45) y,
cuando existe, los datos experimentales son coherentes entre sí.

--------------------------------------------------------------------------
1) ERROR ABSOLUTO Y RELATIVO
--------------------------------------------------------------------------
Dadas dos series y_a (analítica) e y_n (numérica) evaluadas en los mismos
instantes:

        E_abs(t) = | y_a(t) - y_n(t) |

        E_rel(t) = | y_a(t) - y_n(t) | / | y_a(t) | · 100   (porcentaje)

El error relativo solo está definido cuando el valor de referencia
y_a(t) ≠ 0; en caso contrario se reporta como NaN (no definido).

Una diferencia pequeña entre ambas soluciones es ESPERABLE: la solución
numérica introduce un error de truncamiento (aproximación del método de
Runge-Kutta) y de redondeo (aritmética de punto flotante del computador).

--------------------------------------------------------------------------
2) VERIFICACIÓN DE QUE UNA SOLUCIÓN SATISFACE LA EDO
--------------------------------------------------------------------------
Si y(t) resuelve y' = f(t, y), entonces la derivada numérica de y debe
coincidir con f. Usamos diferencias centradas (np.gradient) para estimar
y'(t) y definimos el residuo:

        r(t) = y'_numérica(t) - f(t, y(t))

Un residuo pequeño en todo el intervalo confirma que la solución analítica
realmente satisface la ecuación diferencial.
"""

from __future__ import annotations

import numpy as np


def compare_analytical_numerical(t, y_analytic, y_numeric) -> dict:
    """Compara dos soluciones evaluadas en los mismos instantes t.

    Devuelve un diccionario con los arrays de errores y los máximos.
    """
    t = np.asarray(t, dtype=float)
    y_a = np.asarray(y_analytic, dtype=float)
    y_n = np.asarray(y_numeric, dtype=float)

    abs_err = np.abs(y_a - y_n)

    # Error relativo porcentual; NaN donde el valor de referencia es ~0.
    with np.errstate(divide="ignore", invalid="ignore"):
        rel_err = np.where(np.abs(y_a) > 1e-12, abs_err / np.abs(y_a) * 100.0, np.nan)

    return {
        "t": t,
        "analytic": y_a,
        "numeric": y_n,
        "abs_err": abs_err,
        "rel_err": rel_err,
        "max_abs": float(np.nanmax(abs_err)),
        "mean_abs": float(np.nanmean(abs_err)),
        # Máximo del error relativo ignorando los NaN (donde no está definido).
        "max_rel": float(np.nanmax(rel_err)) if np.any(np.isfinite(rel_err)) else float("nan"),
    }


def check_solution(ode_rhs, t, y, y0, t0=None) -> dict:
    """Verifica que y(t) cumple la EDO  y' = f(t, y)  y la condición inicial.

    Parámetros:
        ode_rhs : función f(t, y) (debe aceptar dos argumentos)
        t       : array de tiempos
        y       : array de valores de la solución
        y0      : valor inicial esperado
        t0      : tiempo inicial esperado (por defecto t[0])

    Devuelve un diccionario con:
        residual_max   : máximo |y'_num - f(t, y)| (debe ser pequeño)
        ic_ok          : ¿la solución cumple y(t0) ≈ y0?
        ic_value       : valor de la solución en t0
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    t0 = t[0] if t0 is None else t0

    # Derivada numérica con diferencias centradas.
    dy_num = np.gradient(y, t)
    rhs = np.asarray(ode_rhs(t, y), dtype=float)
    residuo = dy_num - rhs

    # Valor en la condición inicial: interpolamos o tomamos el punto más cercano.
    idx0 = int(np.argmin(np.abs(t - t0)))
    ic_value = float(y[idx0])
    ic_ok = bool(np.isclose(ic_value, float(y0), atol=1e-6, rtol=1e-6))

    return {
        "residual": residuo,
        "residual_max": float(np.max(np.abs(residuo))),
        "ic_ok": ic_ok,
        "ic_value": ic_value,
    }


def verify_initial_condition(y_analytic_func, t0, y0) -> bool:
    """Comprueba si la solución analítica cumple y(t0) = y0 (tolerancia 1e-6)."""
    return bool(np.isclose(float(y_analytic_func(t0)), float(y0), atol=1e-6, rtol=1e-6))
