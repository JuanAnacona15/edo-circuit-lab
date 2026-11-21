"""
core/rc_model.py — Modelo matemático del circuito RC
=====================================================

Circuito RC: una resistencia R y un capacitor C conectados en serie.
Es el "problema real" del proyecto de aula: la DESCARGA de un capacitor
a través de una resistencia, medida de forma experimental.

--------------------------------------------------------------------------
1) DEDUCCIÓN DE LA ECUACIÓN DIFERENCIAL (Ley de tensiones de Kirchhoff)
--------------------------------------------------------------------------
En un lazo cerrado la suma de las caídas de tensión es cero (LTK):

        V_R + V_C = 0                                         (1)

donde:
    * V_R = tensión en la resistencia. Ley de Ohm: V_R = R·i
    * V_C = tensión en el capacitor. Definición de capacitancia: V_C = q/C
      (q = carga almacenada en el capacitor, C = capacitancia)

La corriente i es la RAPIDEZ con la que sale carga del capacitor:

        i = - dq/dt

(el signo negativo indica que, durante la descarga, la carga DISMINUYE).
Como q = C·V_C, al derivar respecto al tiempo:

        dq/dt = C · dV_C/dt        →        i = - C · dV_C/dt   (2)

Sustituyendo (2) en V_R = R·i y llevando a (1):

        -R·C·dV_C/dt + V_C = 0
        R·C·dV_C/dt + V_C = 0
        dV_C/dt = - V_C / (R·C)                                (3)

La ecuación (3) es una EDO lineal de primer orden de la forma:

        dV/dt = - V / τ       con       τ = R·C

La cantidad τ = R·C se llama CONSTANTE DE TIEMPO. Sus unidades son
segundos (Ω·F = s) y representa el tiempo característico del circuito.

--------------------------------------------------------------------------
2) SOLUCIÓN ANALÍTICA (método de separación de variables)
--------------------------------------------------------------------------
        dV/dt = -V/τ   →   dV/V = -dt/τ

Integrando ambos lados:

        ln|V| = -t/τ + C   →   V(t) = A·e^{-t/τ}

Imponiendo la condición inicial V(0) = V₀:

        V(0) = A = V₀        →       V(t) = V₀ · e^{-t/τ}      (4)

--------------------------------------------------------------------------
3) CARGA DEL CAPACITOR (caso complementario)
--------------------------------------------------------------------------
Si en lugar de descargar, el capacitor se carga desde una fuente E₀ a
través de R, la LTK da:

        E₀ = R·i + V_C = R·C·dV_C/dt + V_C    (ahora i = +C·dV/dt)

        dV/dt = (E₀ - V) / τ

cuya solución con condición inicial V(0) = V₀ es:

        V(t) = E₀ + (V₀ - E₀)·e^{-t/τ}                          (5)

(Nota: si el capacitor parte descargado, V₀ = 0, y queda V = E₀(1 - e^{-t/τ})).

--------------------------------------------------------------------------
4) INTERPRETACIÓN FÍSICA DE LA CONSTANTE DE TIEMPO
--------------------------------------------------------------------------
    t = τ   →  V = V₀·e^{-1} ≈ 0.3679·V₀   (queda el 36,8 %)
    t = 2τ  →  V = V₀·e^{-2} ≈ 0.1353·V₀   (queda el 13,5 %)
    t = 3τ  →  V = V₀·e^{-3} ≈ 0.0498·V₀   (queda el  5,0 %)
    t = 5τ  →  V = V₀·e^{-5} ≈ 0.0067·V₀   (queda el  0,7 %)

En la práctica se considera el capacitor "descargado" a las 5τ (≈99,3 %).
Matemáticamente NUNCA llega a cero:  lim_{t→∞} V(t) = 0.
"""

from __future__ import annotations

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# Funciones analíticas (evaluables sobre arrays de NumPy de forma vectorizada)
# ─────────────────────────────────────────────────────────────────────────────


def time_constant(R: float, C: float) -> float:
    """Constante de tiempo del circuito RC:  τ = R·C  (en segundos).

    R en ohmios (Ω), C en faradios (F). El producto Ω·F tiene dimensión de
    tiempo (segundos), lo que justifica que τ se mida en segundos.
    """
    return float(R) * float(C)


def discharge_solution(t, V0: float, tau: float):
    """Solución analítica de la DESCARGA:  V(t) = V₀·e^{-t/τ}.

    `t` puede ser un escalar o un array de NumPy; el resultado conserva la
    forma de la entrada (evaluación vectorizada).
    """
    t = np.asarray(t, dtype=float)
    return float(V0) * np.exp(-t / float(tau))


def charge_solution(t, E0: float, V0: float, tau: float):
    """Solución analítica de la CARGA:  V(t) = E₀ + (V₀ - E₀)·e^{-t/τ}.

    E₀  : tensión de la fuente de carga (V)
    V₀  : tensión inicial del capacitor (V)
    tau : constante de tiempo (s)

    Si V₀ = 0 (capacitor descargado) se recupera V(t) = E₀(1 - e^{-t/τ}).
    """
    t = np.asarray(t, dtype=float)
    E0, V0, tau = float(E0), float(V0), float(tau)
    return E0 + (V0 - E0) * np.exp(-t / tau)


def discharge_time_to_voltage(V_target: float, V0: float, tau: float) -> float:
    """Tiempo que tarda la DESCARGA en alcanzar un voltaje V_target.

    De V(t) = V₀·e^{-t/τ} se despeja:
        e^{-t/τ} = V_target/V₀  →  -t/τ = ln(V_target/V₀)  →  t = τ·ln(V₀/V_target)

    Válido solo si 0 < V_target ≤ V₀ (de lo contrario no tiene sentido físico).
    """
    V_target, V0, tau = float(V_target), float(V0), float(tau)
    return tau * np.log(V0 / V_target)


def charge_time_to_voltage(V_target: float, E0: float, V0: float, tau: float) -> float:
    """Tiempo que tarda la CARGA en alcanzar un voltaje V_target.

    De V(t) = E₀ + (V₀ - E₀)e^{-t/τ} se despeja:
        e^{-t/τ} = (E₀ - V_target)/(E₀ - V₀)  →  t = τ·ln((E₀ - V₀)/(E₀ - V_target))

    Válido solo si V_target está entre V₀ y E₀.
    """
    E0, V0, tau = float(E0), float(V0), float(tau)
    return tau * np.log((E0 - V0) / (E0 - V_target))


def remaining_fraction_after_n_tau(n: float) -> float:
    """Fracción de voltaje que queda tras n constantes de tiempo: e^{-n}."""
    return float(np.exp(-float(n)))


def ode_rhs_discharge(V, tau: float):
    """Lado derecho de la EDO de descarga:  f(V) = dV/dt = -V/τ.

    Se usa para la simulación numérica (solve_ivp) y para verificar que la
    solución analítica satisface la ecuación diferencial.
    """
    return -np.asarray(V, dtype=float) / float(tau)


def ode_rhs_charge(V, E0: float, tau: float):
    """Lado derecho de la EDO de carga:  f(V) = dV/dt = (E₀ - V)/τ."""
    V = np.asarray(V, dtype=float)
    return (float(E0) - V) / float(tau)


# ─────────────────────────────────────────────────────────────────────────────
# Validación de parámetros
# ─────────────────────────────────────────────────────────────────────────────


def validate_params(R, C, V0, t_max, dt, E0=None, mode="discharge") -> list[str]:
    """Valida los parámetros del simulador RC y devuelve una lista de errores.

    Devuelve una lista de cadenas con los problemas encontrados (vacía = OK).
    No lanza excepciones: la interfaz decide cómo mostrar los mensajes.
    """
    errors: list[str] = []
    # R y C solo se validan si se proporcionan. Si se usa la constante de
    # tiempo τ directamente (R=C=None), se omiten estas comprobaciones.
    if R is not None and R <= 0:
        errors.append("La resistencia R debe ser mayor que cero (Ω).")
    if C is not None and C <= 0:
        errors.append("La capacitancia C debe ser mayor que cero (F).")
    if V0 is None or V0 < 0:
        errors.append("El voltaje inicial V₀ debe ser mayor o igual que cero.")
    if mode == "charge" and E0 is not None and E0 <= 0:
        errors.append("El voltaje de la fuente E₀ debe ser mayor que cero.")
    if t_max is None or t_max <= 0:
        errors.append("El tiempo de simulación debe ser mayor que cero.")
    if dt is None or dt <= 0:
        errors.append("El paso de tiempo debe ser mayor que cero.")
    if t_max and dt and dt > t_max:
        errors.append("El paso de tiempo no puede ser mayor que el tiempo total.")
    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Simulación: genera la malla de tiempo y los valores de voltaje
# ─────────────────────────────────────────────────────────────────────────────


def simulate(V0: float, tau: float, t_max: float, dt: float,
             mode: str = "discharge", E0: float | None = None) -> dict:
    """Genera (t, V) usando la solución analítica cerrada.

    Parámetros:
        V0    : voltaje inicial del capacitor (V)
        tau   : constante de tiempo (s)
        t_max : duración total de la simulación (s)
        dt    : separación entre puntos (s)
        mode  : "discharge" (descarga) o "charge" (carga)
        E0    : tensión de fuente (solo para "charge")

    Devuelve un diccionario con las claves:
        t           -> array de tiempos (desde 0 hasta t_max, paso dt)
        V           -> array de voltajes correspondientes
        tau         -> constante de tiempo usada
        info        -> diccionario con valores derivados (V_final, etc.)
    """
    # np.arange(0, t_max + dt/2, dt): incluimos el extremo si cae en la malla.
    t = np.arange(0.0, float(t_max) + float(dt) / 2.0, float(dt))

    if mode == "charge":
        V = charge_solution(t, E0, V0, tau)
        V_final = float(E0)  # el capacitor tiende a la tensión de la fuente
    else:
        V = discharge_solution(t, V0, tau)
        V_final = 0.0  # límite asintótico de la descarga

    info = {
        "t": t,
        "V": V,
        "tau": float(tau),
        "V0": float(V0),
        "V_final": V_final,
        "mode": mode,
        "E0": float(E0) if E0 is not None else None,
        # Porcentaje que queda tras 1τ, 3τ y 5τ (explicación física).
        "remaining_1tau": remaining_fraction_after_n_tau(1) * 100,
        "remaining_3tau": remaining_fraction_after_n_tau(3) * 100,
        "remaining_5tau": remaining_fraction_after_n_tau(5) * 100,
    }
    return info
