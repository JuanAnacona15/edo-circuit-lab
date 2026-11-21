"""pages/comparacion.py — Comparación entre solución analítica y numérica.

Demuestra que el cálculo manual/simbólico (SymPy) y la simulación numérica
(SciPy / RK45) coinciden, y cuantifica el error entre ambas.
"""

import numpy as np
import streamlit as st

from utils import styling

styling.inject()

from core import numerical_solver, rc_model, rl_model, symbolic_solver, validation
from utils import formatting as fmt
from utils import plotting

st.title("⚖️ Comparación y validación")

st.markdown(
    """
    Compara la **solución analítica** (obtenida a mano y verificada con
    SymPy) con la **solución numérica** (SciPy, método RK45). Una diferencia
    pequeña es esperable y se debe a la precisión numérica del computador.
    """
)

circuito = st.radio("Circuito", ["Circuito RC (descarga)", "Circuito RL"], horizontal=True)

c1, c2, c3, c4 = st.columns(4)
if circuito.startswith("RC"):
    with c1:
        V0 = st.number_input("V₀ (V)", value=9.2128, format="%.4f")
    with c2:
        tau = st.number_input("τ (s)", value=0.4896, format="%.4f")
    t_max = st.number_input("Tiempo de simulación (s)", value=2.0, format="%.2f", key="rc_tmax")
    dt = st.number_input("Paso (s)", value=0.02, format="%.3f", key="rc_dt")
    y0 = V0
else:
    with c1:
        R = st.number_input("R (Ω)", value=4.0, format="%.2f", key="rl_R")
    with c2:
        L = st.number_input("L (H)", value=2.0, format="%.2f", key="rl_L")
    with c3:
        E0 = st.number_input("E₀ (V)", value=12.0, format="%.2f", key="rl_E0")
    with c4:
        i0 = st.number_input("i₀ (A)", value=0.0, format="%.2f", key="rl_i0")
    t_max = st.number_input("Tiempo de simulación (s)", value=2.0, format="%.2f", key="rl_tmax")
    dt = st.number_input("Paso (s)", value=0.02, format="%.3f", key="rl_dt")
    y0 = i0

if st.button("🔬 Ejecutar comparación", type="primary"):
    t_malla = np.arange(0.0, t_max + dt / 2.0, dt)

    if circuito.startswith("RC"):
        sym = symbolic_solver.solve_rc(tau, V0)
        num = numerical_solver.simulate_rc_numerical(V0, tau, t_max, dt)
        y_analytic = rc_model.discharge_solution(t_malla, V0, tau)
        ylabel = "V (V)"
        ode_rhs = lambda t, y: rc_model.ode_rhs_discharge(y, tau)  # noqa: E731
    else:
        sym = symbolic_solver.solve_rl(R, L, E0, i0)
        num = numerical_solver.simulate_rl_numerical(R, L, E0, i0, t_max, dt)
        y_analytic = rl_model.current_solution(t_malla, R, L, E0, i0)
        ylabel = "i (A)"
        ode_rhs = lambda t, y: rl_model.ode_rhs(y, R, L, E0)  # noqa: E731

    st.markdown("### Solución simbólica (SymPy)")
    st.latex(sym["latex_solution"])

    # La solución numérica se evalúa en la malla que devuelve solve_ivp.
    t = num["t"]
    y_num = num["y"]
    # Evaluamos la analítica en los MISMOS instantes para comparar punto a punto.
    if circuito.startswith("RC"):
        y_ana_eval = rc_model.discharge_solution(t, V0, tau)
    else:
        y_ana_eval = rl_model.current_solution(t, R, L, E0, i0)

    comp = validation.compare_analytical_numerical(t, y_ana_eval, y_num)

    st.markdown("### Gráfica comparativa")
    st.plotly_chart(
        plotting.figure_comparison(t, y_ana_eval, y_num, comp["abs_err"], ylabel),
        width="stretch",
    )

    st.markdown("### Indicadores de precisión")
    c1, c2, c3 = st.columns(3)
    c1.metric("Error absoluto máximo", f"{comp['max_abs']:.3e}")
    c2.metric("Error absoluto medio", f"{comp['mean_abs']:.3e}")
    c3.metric("Error relativo máximo", f"{fmt.fmt_es(comp['max_rel'], 4)} %")

    # ── Tabla de comparación en instantes seleccionados ──────────────────────
    instantes = np.unique(np.round(np.linspace(0, t_max, 11), 3))
    idx = [int(np.argmin(np.abs(t - ti))) for ti in instantes]
    import pandas as pd
    tabla = pd.DataFrame({
        "t (s)": [round(float(t[i]), 3) for i in idx],
        "Analítica": [float(y_ana_eval[i]) for i in idx],
        "Numérica": [float(y_num[i]) for i in idx],
        "|Error abs|": [float(comp["abs_err"][i]) for i in idx],
        "Error rel. (%)": [round(float(comp["rel_err"][i]), 6) if np.isfinite(comp["rel_err"][i]) else None for i in idx],
    })
    st.markdown("#### Comparación en instantes seleccionados")
    st.dataframe(tabla, width="stretch")

    # ── Verificación de la EDO y de la condición inicial ─────────────────────
    check = validation.check_solution(ode_rhs, t, y_ana_eval, y0, t0=0.0)
    st.markdown("#### Verificación de la solución")
    if check["ic_ok"]:
        st.success("✅ La solución cumple la condición inicial y(0) = y₀.")
    else:
        st.error(f"❌ La solución NO cumple la condición inicial: y(0) = "
                 f"{fmt.fmt_es(check['ic_value'])} ≠ {fmt.fmt_es(y0)}.")
    st.info(f"Residuo máximo |y′_numérica − f(t, y)| = {check['residual_max']:.3e}. "
            "Un residuo pequeño confirma que la solución analítica satisface "
            "la ecuación diferencial.")
