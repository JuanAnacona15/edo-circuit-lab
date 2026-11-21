"""
core/numerical_solver.py — Resolución numérica con SciPy (solve_ivp / RK45)
============================================================================

Mientras SymPy da la solución EXACTA, SciPy aproxima la solución del PVI
mediante integración numérica. El método exigido por el documento es RK45:
un método de Runge-Kutta-Fehlberg de orden 4/5 con paso adaptativo.

Cómo funciona RK45 (idea breve):
    * Runge-Kutta aproxima y(t + h) combinando varias evaluaciones de la
      pendiente f(t, y) dentro del intervalo [t, t+h] (en vez de una sola,
      como en el método de Euler). RK45 usa 6 evaluaciones para estimar la
      solución con orden 5 y 4.
    * Fehlberg reutiliza esas mismas evaluaciones para estimar el error
      entre las dos órdenes y ajusta el paso h automáticamente: lo reduce si
      el error es grande y lo aumenta si es pequeño. Por eso es "adaptativo".

Esto garantiza una precisión controlada sin que el usuario tenga que elegir
el paso manualmente.

``solve_ivp`` resuelve el problema de valor inicial:

        y'(t) = f(t, y),   y(t0) = y0

en el intervalo [t0, tf]. Con ``t_eval`` le pedimos que devuelva la solución
evaluada exactamente en los instantes que queremos comparar con la solución
analítica.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp


def solve_ivp_rk45(f, t_span, y0, t_eval=None, **kwargs):
    """Envoltorio de solve_ivp con el método RK45.

    Parámetros:
        f      : función f(t, y) que define y' = f(t, y)
        t_span : (t_inicial, t_final)
        y0     : valor inicial (lista o escalar)
        t_eval : instantes donde se evalúa la solución (array)

    Devuelve la solución de SciPy (objeto con .t, .y, .success, .message).

    Se usan tolerancias MUY estrictas (rtol=1e-9, atol=1e-11) en lugar de las
    de SciPy (rtol=1e-3): como este módulo sirve para VALIDAR que la solución
    analítica y la numérica coinciden, queremos que la diferencia refleje
    solo el error de punto flotante y no la tolerancia del integrador.
    """
    kwargs.setdefault("rtol", 1e-9)
    kwargs.setdefault("atol", 1e-11)
    return solve_ivp(f, t_span, [float(y0)], method="RK45", t_eval=t_eval,
                     dense_output=False, **kwargs)


def simulate_rc_numerical(V0: float, tau: float, t_max: float, dt: float) -> dict:
    """PVI del RC en descarga:  dV/dt = -V/τ,  V(0) = V₀.

    Devuelve {t, y} con la solución numérica evaluada en la malla t_eval.
    """
    t_eval = np.arange(0.0, t_max + dt / 2.0, dt)
    sol = solve_ivp_rk45(lambda t, y: -y[0] / float(tau), (0.0, t_max), V0,
                         t_eval=t_eval)
    return {"t": sol.t, "y": sol.y[0], "success": sol.success,
            "message": sol.message}


def simulate_rl_numerical(R: float, L: float, E0: float, i0: float,
                          t_max: float, dt: float) -> dict:
    """PVI del RL:  di/dt = (E₀ - R·i)/L,  i(0) = i₀.

    Devuelve {t, y} con la solución numérica evaluada en la malla t_eval.
    """
    t_eval = np.arange(0.0, t_max + dt / 2.0, dt)
    sol = solve_ivp_rk45(lambda t, i: (float(E0) - float(R) * i[0]) / float(L),
                         (0.0, t_max), i0, t_eval=t_eval)
    return {"t": sol.t, "y": sol.y[0], "success": sol.success,
            "message": sol.message}
