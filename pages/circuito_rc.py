"""pages/circuito_rc.py — Simulador del circuito RC (carga y descarga).

Módulo central del "problema real" del proyecto: la descarga de un
capacitor a través de una resistencia.
"""

import streamlit as st

from utils import styling

styling.inject()

from core import rc_model
from utils import formatting as fmt
from utils import plotting

st.title("🔋 Simulador de circuito RC")

st.markdown(
    """
    Un circuito **RC** es una resistencia $R$ y un capacitor $C$ en serie.
    La tensión del capacitor evoluciona según la ecuación diferencial
    (ley de tensiones de Kirchhoff):

    $$
    \\frac{dV}{dt} = -\\frac{V}{RC} = -\\frac{V}{\\tau}
    $$

    donde $\\tau = RC$ es la **constante de tiempo**. En la *descarga* el
    voltaje cae exponencialmente hacia 0; en la *carga* sube hacia la
    tensión de la fuente $E_0$.
    """
)

# ── 1. Parámetros ────────────────────────────────────────────────────────────
st.markdown("### 1. Parámetros del circuito")

col_params, col_extra = st.columns([1.0, 1.0], gap="large")

with col_params:
    modo = st.radio("Modo de operación", ["Descarga", "Carga"], horizontal=True)

    usar_tau = st.checkbox(
        "Usar la constante de tiempo del proyecto (τ = 0,4896 s)",
        value=True,
        help="El conjunto Volts no da R y C por separado; solo se conoce τ.",
    )

    V0 = st.number_input("Voltaje inicial V₀ (V)", value=9.2128, format="%.4f")

    if usar_tau:
        tau = st.number_input("Constante de tiempo τ (s)", value=0.4896,
                              format="%.4f", disabled=True)
        R = C = None
        st.caption("R y C no se necesitan: se trabaja con τ directamente.")
    else:
        R = st.number_input("Resistencia R (Ω)", value=1000.0, format="%.2f")
        C = st.number_input("Capacitancia C (F)", value=0.0004896, format="%.6f")
        st.caption(f"Equivalente: {fmt.fmt_capacitance(C)}")
        tau = float(R) * float(C) if R > 0 and C > 0 else None

    E0 = None
    if modo == "Carga":
        E0 = st.number_input("Voltaje de la fuente E₀ (V)", value=12.0, format="%.2f")

    t_max = st.number_input("Tiempo de simulación (s)", value=3.0, format="%.2f")
    dt = st.number_input("Paso de tiempo (s)", value=0.02, format="%.3f")

with col_extra:
    st.markdown("#### Circuito")
    st.markdown(
        """
        ```
           +--- R ---+--- V_C ---+
           |         |           |
        fuente       └─── C ─────┘
        (descarga: sin fuente, C entrega su energía a R)
        ```
        """
    )
    st.markdown("#### Regla práctica")
    st.markdown(
        """
        | Tiempo | Voltaje restante |
        |--------|------------------|
        | 1τ | 36,8 % |
        | 2τ | 13,5 % |
        | 3τ | 5,0 % |
        | 5τ | 0,7 % |

        A las **5τ** se considera el capacitor prácticamente descargado
        (≈99,3 %), aunque matemáticamente nunca llega a 0.
        """
    )

# ── Validación ───────────────────────────────────────────────────────────────
errores = rc_model.validate_params(R, C, V0, t_max, dt, E0=E0,
                                   mode="discharge" if modo == "Descarga" else "charge")

if errores:
    st.error("Corrige los siguientes valores antes de simular:")
    for e in errores:
        st.markdown(f"- {e}")
    st.stop()

# ── 2. Cálculo y resultados ──────────────────────────────────────────────────
modo_key = "discharge" if modo == "Descarga" else "charge"
sim = rc_model.simulate(V0, tau, t_max, dt, mode=modo_key, E0=E0)

st.markdown("### 2. Resultado matemático")

if modo == "Descarga":
    st.latex(r"\frac{dV}{dt} = -\frac{V}{\tau} = " +
             rf"-\frac{{V}}{{{fmt.fmt_es(tau)}}}")
    st.latex(r"V(0) = V_0 = " + fmt.fmt_es(V0) + r"\ \text{V}")
    st.latex(rf"V(t) = {fmt.fmt_es(V0)}\,e^{{-t/{fmt.fmt_es(tau)}}}")
else:
    st.latex(r"\frac{dV}{dt} = \frac{E_0 - V}{\tau}")
    st.latex(r"V(0) = " + fmt.fmt_es(V0) + r"\ \text{V}")
    st.latex(rf"V(t) = {fmt.fmt_es(E0)} + ({fmt.fmt_es(V0)} - {fmt.fmt_es(E0)})"
             rf"\,e^{{-t/{fmt.fmt_es(tau)}}}")

st.markdown("### 3. Gráfica del comportamiento")
st.plotly_chart(plotting.figure_rc(sim["t"], sim["V"], tau, V0, mode=modo_key, E0=E0),
                width="stretch")

# ── 4. Indicadores ───────────────────────────────────────────────────────────
st.markdown("### 4. Indicadores")
V_en_tau = rc_model.charge_solution(tau, E0, V0, tau) if modo == "Carga" \
    else rc_model.discharge_solution(tau, V0, tau)
V_final = sim["V"][-1]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Voltaje inicial V₀", f"{fmt.fmt_es(V0)} V")
c2.metric("Constante de tiempo τ", f"{fmt.fmt_es(tau)} s")
c3.metric("Voltaje a t = τ", f"{fmt.fmt_es(V_en_tau)} V")
c4.metric("Voltaje a t = t_max", f"{fmt.fmt_es(V_final)} V")
if modo == "Descarga":
    pct_restante = V_final / V0 * 100
    c5.metric("% restante", f"{fmt.fmt_es(pct_restante, 2)} %")
else:
    c5.metric("% de carga", f"{fmt.fmt_es(V_final / E0 * 100, 2)} %")

# ── Consulta: tiempo para alcanzar un voltaje ───────────────────────────────
st.markdown("#### ⏱️ Tiempo para alcanzar un voltaje determinado")
if modo == "Descarga":
    v_target = st.number_input("Voltaje objetivo (V)", value=V0 / 2.0,
                               min_value=0.0001, max_value=V0, format="%.4f")
    t_objetivo = rc_model.discharge_time_to_voltage(v_target, V0, tau)
else:
    v_target = st.number_input("Voltaje objetivo (V)", value=(E0 - V0) * 0.63 + V0,
                               min_value=V0, max_value=E0, format="%.4f")
    t_objetivo = rc_model.charge_time_to_voltage(v_target, E0, V0, tau)
st.success(f"Se alcanza **{fmt.fmt_es(v_target)} V** en **{fmt.fmt_es(t_objetivo)} s**.")

# ── Explicación física ───────────────────────────────────────────────────────
with st.expander("💡 ¿Qué significa esto físicamente?", expanded=False):
    if modo == "Descarga":
        st.markdown(
            """
            - El capacitor entrega su energía almacenada a través de R. Cuanto
              mayor es R, más lenta es la corriente y más tarda en descargarse.
            - Cuanto mayor es C, más carga almacena (para el mismo voltaje) y
              más tarda en vaciarse.
            - **Aumentar τ (R o C) → descarga más lenta.** Disminuir τ →
              descarga más rápida.
            - La pendiente de la curva es más pronunciada al inicio (hay más
              voltaje "empujando" la corriente) y se aplana al acercarse a 0.
            """
        )
    else:
        st.markdown(
            """
            - El capacitor se carga desde la fuente. La corriente es máxima al
              inicio (el capacitor está "vacío") y cae a medida que la tensión
              se acerca a E₀.
            - La carga **nunca** llega exactamente a E₀: solo se aproxima de
              forma asintótica (a 5τ alcanza ≈99,3 %).
            """
        )

