"""
core/rl_model.py — Modelo matemático del circuito RL
=====================================================

Circuito RL: una resistencia R y una inductancia (bobina) L conectadas
en serie con una fuente de voltaje constante E₀. Es el "ejercicio
complementario" del proyecto de aula.

--------------------------------------------------------------------------
1) DEDUCCIÓN DE LA ECUACIÓN DIFERENCIAL (Ley de tensiones de Kirchhoff)
--------------------------------------------------------------------------
En un lazo cerrado, la suma de caídas de tensión es igual a la tensión
de la fuente (LTK):

        V_R + V_L = E₀                                        (1)

donde:
    * V_R = caída en la resistencia. Ley de Ohm: V_R = R·i
    * V_L = caída en la bobina. Ley de Faraday-Lenz:
            V_L = L·di/dt
      (una bobina se OPPONE a los cambios de corriente; L es la inductancia)

Sustituyendo en (1):

        R·i + L·di/dt = E₀
        L·di/dt + R·i = E₀                                    (2)

La ecuación (2) es una EDO lineal de primer orden, NO homogénea
(término independiente E₀).

--------------------------------------------------------------------------
2) SOLUCIÓN ANALÍTICA
--------------------------------------------------------------------------
(2) es lineal de la forma  di/dt + (R/L)·i = E₀/L.

La solución general es: homogénea + particular.

    * Homogénea (E₀ = 0):  di/dt = -(R/L)·i  →  i_h(t) = A·e^{-(R/L)t}
    * Particular (estado estacionario, di/dt = 0):  i_p = E₀/R

Sumando y aplicando la condición inicial i(0) = i₀:

        i(t) = E₀/R + (i₀ - E₀/R)·e^{-(R/L)t}                 (3)

La CONSTANTE DE TIEMPO es:

        τ = L / R        (segundos: H/Ω = s)

y la CORRIENTE DE ESTADO ESTACIONARIO (cuando t → ∞, la exponencial se
anula y la bobina se comporta como un cable):

        I∞ = E₀ / R

--------------------------------------------------------------------------
3) EJERCICIO DEL PROYECTO (R = 4 Ω, L = 2 H, E₀ = 12 V, i₀ = 0 A)
--------------------------------------------------------------------------
        τ = L/R = 2/4 = 0,5 s
        I∞ = E₀/R = 12/4 = 3 A

Sustituyendo en (3):

        i(t) = 3 + (0 - 3)·e^{-2t} = 3(1 - e^{-2t})

La corriente crece exponencialmente desde 0 A hasta acercarse a 3 A.
"""

from __future__ import annotations

import numpy as np


def time_constant(R: float, L: float) -> float:
    """Constante de tiempo del circuito RL:  τ = L/R  (en segundos)."""
    return float(L) / float(R)


def steady_state_current(E0: float, R: float) -> float:
    """Corriente de estado estacionario:  I∞ = E₀/R  (amperios)."""
    return float(E0) / float(R)


def current_solution(t, R: float, L: float, E0: float, i0: float):
    """Solución analítica:  i(t) = E₀/R + (i₀ - E₀/R)·e^{-(R/L)t}.

    `t` puede ser escalar o array de NumPy (evaluación vectorizada).
    """
    t = np.asarray(t, dtype=float)
    R, L, E0, i0 = float(R), float(L), float(E0), float(i0)
    i_inf = E0 / R
    return i_inf + (i0 - i_inf) * np.exp(-(R / L) * t)


def time_to_current(i_target: float, R: float, L: float, E0: float, i0: float) -> float:
    """Tiempo que tarda la corriente en alcanzar i_target.

    De i(t) = I∞ + (i₀ - I∞)e^{-(R/L)t} se despeja:
        e^{-(R/L)t} = (I∞ - i_target)/(I∞ - i₀)
        t = (L/R)·ln((I∞ - i₀)/(I∞ - i_target))

    Válido solo si i_target está entre i₀ e I∞.
    """
    R, L, E0, i0 = float(R), float(L), float(E0), float(i0)
    i_inf = E0 / R
    return (L / R) * np.log((i_inf - i0) / (i_inf - i_target))


def ode_rhs(i, R: float, L: float, E0: float):
    """Lado derecho de la EDO:  f(i) = di/dt = (E₀ - R·i)/L.

    Se obtiene despejando di/dt de (2). Se usa para la simulación numérica
    y para comprobar que la solución analítica satisface la EDO.
    """
    i = np.asarray(i, dtype=float)
    return (float(E0) - float(R) * i) / float(L)


def validate_params(R, L, E0, i0, t_max, dt) -> list[str]:
    """Valida los parámetros del simulador RL y devuelve una lista de errores."""
    errors: list[str] = []
    if R is None or R <= 0:
        errors.append("La resistencia R debe ser mayor que cero (Ω).")
    if L is None or L <= 0:
        errors.append("La inductancia L debe ser mayor que cero (H).")
    if E0 is None:
        errors.append("El voltaje de la fuente E₀ debe ser un número.")
    if i0 is None:
        errors.append("La corriente inicial i₀ debe ser un número.")
    if t_max is None or t_max <= 0:
        errors.append("El tiempo de simulación debe ser mayor que cero.")
    if dt is None or dt <= 0:
        errors.append("El paso de tiempo debe ser mayor que cero.")
    return errors


def simulate(R: float, L: float, E0: float, i0: float,
             t_max: float, dt: float) -> dict:
    """Genera (t, i) usando la solución analítica cerrada.

    Devuelve un diccionario con `t`, `i`, y `info` (constante de tiempo,
    corriente final, etc.) listos para graficar.
    """
    t = np.arange(0.0, float(t_max) + float(dt) / 2.0, float(dt))
    i = current_solution(t, R, L, E0, i0)
    i_inf = steady_state_current(E0, R)

    info = {
        "t": t,
        "i": i,
        "tau": time_constant(R, L),
        "i0": float(i0),
        "i_inf": i_inf,
        "R": float(R),
        "L": float(L),
        "E0": float(E0),
    }
    return info
