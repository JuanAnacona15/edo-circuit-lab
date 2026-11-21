"""pages/circuito_rl.py — Simulador del circuito RL.

Ejercicio complementario del proyecto: evolución de la corriente en una
bobina conectada a una fuente de voltaje constante.
"""

import streamlit as st

from core import rl_model
from utils import formatting as fmt
from utils import plotting

st.title("🧲 Simulador de circuito RL")

st.markdown(
    """
    Un circuito **RL** es una resistencia $R$ y una bobina (inductancia) $L$
    en serie con una fuente $E_0$. La corriente satisface (ley de tensiones
    de Kirchhoff):

    $$
    L\\frac{di}{dt} + R\\,i = E_0
    $$

    La **constante de tiempo** es $\\tau = L/R$ y la corriente de estado
    estacionario es $I_\\infty = E_0/R$. Al encender, la bobina se opone al
    cambio (ley de Lenz) y la corriente crece gradualmente desde $i_0$ hasta
    $I_\\infty$.
    """
)

# ── 1. Parámetros ────────────────────────────────────────────────────────────
st.markdown("### 1. Parámetros del circuito")

if st.button("📚 Cargar ejercicio del proyecto (R=4 Ω, L=2 H, E₀=12 V, i₀=0 A)"):
    st.session_state["rl_R"] = 4.0
    st.session_state["rl_L"] = 2.0
    st.session_state["rl_E0"] = 12.0
    st.session_state["rl_i0"] = 0.0

c1, c2, c3, c4 = st.columns(4)
with c1:
    R = st.number_input("Resistencia R (Ω)", value=st.session_state.get("rl_R", 4.0),
                        key="rl_R", format="%.2f")
with c2:
    L = st.number_input("Inductancia L (H)", value=st.session_state.get("rl_L", 2.0),
                        key="rl_L", format="%.2f")
with c3:
    E0 = st.number_input("Voltaje de la fuente E₀ (V)",
                         value=st.session_state.get("rl_E0", 12.0), key="rl_E0",
                         format="%.2f")
with c4:
    i0 = st.number_input("Corriente inicial i₀ (A)",
                         value=st.session_state.get("rl_i0", 0.0), key="rl_i0",
                         format="%.2f")

c5, c6 = st.columns(2)
with c5:
    t_max = st.number_input("Tiempo de simulación (s)", value=3.0, format="%.2f")
with c6:
    dt = st.number_input("Paso de tiempo (s)", value=0.02, format="%.3f")

# ── Validación ───────────────────────────────────────────────────────────────
errores = rl_model.validate_params(R, L, E0, i0, t_max, dt)
if errores:
    st.error("Corrige los siguientes valores antes de simular:")
    for e in errores:
        st.markdown(f"- {e}")
    st.stop()

tau = rl_model.time_constant(R, L)
i_inf = rl_model.steady_state_current(E0, R)
sim = rl_model.simulate(R, L, E0, i0, t_max, dt)

# ── 2. Resultado matemático ──────────────────────────────────────────────────
st.markdown("### 2. Resultado matemático")
st.latex(rf"L\frac{{di}}{{dt}} + R\,i = E_0 \quad\Rightarrow\quad "
         rf"{fmt.fmt_es(L)}\frac{{di}}{{dt}} + {fmt.fmt_es(R)}\,i = {fmt.fmt_es(E0)}")
st.latex(rf"\tau = \frac{{L}}{{R}} = \frac{{{fmt.fmt_es(L)}}}{{{fmt.fmt_es(R)}}} = "
         rf"{fmt.fmt_es(tau)}\ \text{{s}}")
st.latex(rf"I_\infty = \frac{{E_0}}{{R}} = \frac{{{fmt.fmt_es(E0)}}}{{{fmt.fmt_es(R)}}} = "
         rf"{fmt.fmt_es(i_inf)}\ \text{{A}}")
st.latex(rf"i(t) = \frac{{E_0}}{{R}} + \left(i_0 - \frac{{E_0}}{{R}}\right)"
         rf"e^{{-Rt/L}} = {fmt.fmt_es(i_inf)} + ({fmt.fmt_es(i0)} - {fmt.fmt_es(i_inf)})"
         rf"\,e^{{-{fmt.fmt_es(R/L)}t}}")

# ── 3. Gráfica ───────────────────────────────────────────────────────────────
st.markdown("### 3. Gráfica de la corriente")
st.plotly_chart(plotting.figure_rl(sim["t"], sim["i"], tau, i_inf, i0),
                width="stretch")

# ── 4. Indicadores ───────────────────────────────────────────────────────────
st.markdown("### 4. Indicadores")
i_en_tau = rl_model.current_solution(tau, R, L, E0, i0)
i_final = sim["i"][-1]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Corriente inicial i₀", f"{fmt.fmt_es(i0)} A")
c2.metric("Constante de tiempo τ", f"{fmt.fmt_es(tau)} s")
c3.metric("Corriente a t = τ", f"{fmt.fmt_es(i_en_tau)} A")
c4.metric("Corriente final I∞", f"{fmt.fmt_es(i_inf)} A")
c5.metric("% del valor final", f"{fmt.fmt_es(i_final / i_inf * 100, 2)} %")

# ── Consulta: tiempo para alcanzar una corriente ─────────────────────────────
st.markdown("#### ⏱️ Tiempo para alcanzar una corriente determinada")
i_target = st.number_input("Corriente objetivo (A)", value=0.95 * i_inf,
                           min_value=i0, max_value=i_inf, format="%.4f")
t_objetivo = rl_model.time_to_current(i_target, R, L, E0, i0)
st.success(f"Se alcanza **{fmt.fmt_es(i_target)} A** en **{fmt.fmt_es(t_objetivo)} s**.")

# ── Explicación física ───────────────────────────────────────────────────────
with st.expander("💡 ¿Cómo influyen R y L?", expanded=False):
    st.markdown(
        f"""
        - **Aumentar R** → disminuye la corriente final $I_\\infty = E_0/R$ y,
          si L se mantiene, **reduce** τ (la corriente se estabiliza antes).
        - **Aumentar L** → la bobina se opone más al cambio, por lo que τ
          crece y la corriente **tarda más** en establecerse.
        - Con los valores actuales: τ = **{fmt.fmt_es(tau)} s** e
          I∞ = **{fmt.fmt_es(i_inf)} A**.

        Físicamente, la bobina almacena energía en su campo magnético
        ($W = \\tfrac{{1}}{{2}}Li^2$) y se resiste a los cambios bruscos de
        corriente, suavizando la respuesta del circuito.
        """
    )
