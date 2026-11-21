"""pages/campo_direcciones.py — Campo de direcciones y variación de parámetros.

Último objetivo específico del proyecto: visualizar el campo de pendientes
de la EDO y cómo cambia la solución al variar condiciones iniciales y
parámetros.
"""

import numpy as np
import streamlit as st

from core import rc_model, rl_model
from utils import plotting

st.title("🧭 Campo de direcciones")

st.markdown(
    """
    El **campo de direcciones** dibuja, en cada punto $(t, y)$ del plano, un
    segmento con pendiente $f(t, y)$ de la EDO $y' = f(t, y)$. Las soluciones
    son las curvas tangentes a estos segmentos: al superponerlas se ve que
    siguen la dirección del campo.

    - En el RC las pendientes son negativas y se suavizan al acercarse a 0.
    - En el RL la corriente asciende hasta su valor estacionario.
    """
)

circuito = st.radio("Circuito", ["Circuito RC (descarga)", "Circuito RL"], horizontal=True)

if circuito.startswith("RC"):
    st.markdown("#### Parámetros")
    c1, c2 = st.columns(2)
    with c1:
        tau = st.slider("Constante de tiempo τ (s)", 0.1, 2.0, 0.4896, 0.05)
    with c2:
        t_max = st.slider("Tiempo máximo (s)", 0.5, 5.0, 2.0, 0.1)

    # Variación de la condición inicial (RF-23): varias curvas a la vez.
    v0_list = st.multiselect(
        "Voltajes iniciales a dibujar (V)",
        options=[2.0, 5.0, 9.0, 12.0, 15.0],
        default=[5.0, 9.0, 12.0, 15.0],
    )

    ode_rhs = lambda t, V: rc_model.ode_rhs_discharge(V, tau)  # noqa: E731
    t = np.linspace(0, t_max, 300)
    curvas = []
    for v0 in v0_list:
        curvas.append((t, rc_model.discharge_solution(t, v0, tau), f"V₀ = {v0:g} V"))

    fig = plotting.figure_direction_field(
        ode_rhs, (0, t_max), (0, max(v0_list) * 1.1 if v0_list else 15),
        curves=curvas, xlabel="t (s)", ylabel="V (V)",
        title=f"Campo de direcciones de dV/dt = −V/τ (τ = {tau:g} s)",
    )
    st.pyplot(fig)
    st.caption("A mayor τ, la descarga es más lenta (las curvas caen más despacio).")

else:
    st.markdown("#### Parámetros")
    c1, c2, c3 = st.columns(3)
    with c1:
        R = st.slider("Resistencia R (Ω)", 1.0, 20.0, 4.0, 0.5)
    with c2:
        L = st.slider("Inductancia L (H)", 0.5, 10.0, 2.0, 0.5)
    with c3:
        E0 = st.slider("Fuente E₀ (V)", 1.0, 24.0, 12.0, 1.0)
    t_max = st.slider("Tiempo máximo (s)", 0.5, 5.0, 2.0, 0.1)

    i_inf = E0 / R
    ode_rhs = lambda t, i: rl_model.ode_rhs(i, R, L, E0)  # noqa: E731
    t = np.linspace(0, t_max, 300)
    # Varias corrientes iniciales para mostrar la convergencia a I∞.
    curvas = []
    for i0 in [0.0, 0.5 * i_inf, 1.5 * i_inf]:
        curvas.append((t, rl_model.current_solution(t, R, L, E0, i0),
                       f"i₀ = {i0:.2f} A"))

    fig = plotting.figure_direction_field(
        ode_rhs, (0, t_max), (0, i_inf * 1.6),
        curves=curvas, xlabel="t (s)", ylabel="i (A)",
        title=f"Campo de direcciones de L·di/dt + R·i = E₀ (τ = {L / R:.2f} s)",
    )
    st.pyplot(fig)
    st.caption(
        f"τ = L/R = {L / R:.2f} s; corriente estacionaria I∞ = E₀/R = {i_inf:.2f} A. "
        "Todas las trayectorias convergen a I∞ independientemente de i₀."
    )
