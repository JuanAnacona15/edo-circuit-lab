"""pages/ecuaciones_exactas.py — Verificador de exactitud y factores integrantes.

Requisito académico fundamental: demuestra paso a paso cómo una EDO que no
es exacta se convierte en exacta mediante un factor integrante.
"""

import streamlit as st

from utils import styling

styling.inject()

from core import exact_equations as ee
from utils import formatting as fmt

st.title("🧮 Ecuaciones exactas y factores integrantes")

st.markdown(
    """
    Este módulo aplica el **método de ecuaciones exactas** a una EDO escrita
    en forma diferencial:

    $$
    M(x, y)\\,dx + N(x, y)\\,dy = 0
    $$

    El criterio de exactitud es $\\dfrac{\\partial M}{\\partial y} =
    \\dfrac{\\partial N}{\\partial x}$. Si no se cumple, se busca un
    **factor integrante** $\\mu$ que vuelva exacta la ecuación.
    """
)

# ── Selección de la ecuación ─────────────────────────────────────────────────
opcion = st.radio(
    "Ecuación a analizar",
    ["Circuito RL (ejercicio del proyecto)", "Circuito RC (descarga)", "Personalizada"],
    horizontal=True,
)

preset = None
x_label = y_label = ""

if opcion.startswith("Circuito RL"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        R = st.number_input("R (Ω)", value=4.0, format="%.2f")
    with c2:
        L = st.number_input("L (H)", value=2.0, format="%.2f")
    with c3:
        E0 = st.number_input("E₀ (V)", value=12.0, format="%.2f")
    with c4:
        i0 = st.number_input("i₀ (A)", value=0.0, format="%.2f")
    preset = ee.preset_rl(R, L, E0, i0)
    x_label, y_label = "t (s)", "i (A)"
    st.info("Se analiza la EDO  L·di/dt + R·i = E₀  escrita como "
            "(R·i − E₀)·dt + L·di = 0.")

elif opcion.startswith("Circuito RC"):
    c1, c2 = st.columns(2)
    with c1:
        tau = st.number_input("Constante de tiempo τ (s)", value=0.4896, format="%.4f")
    with c2:
        V0 = st.number_input("Voltaje inicial V₀ (V)", value=9.2128, format="%.4f")
    preset = ee.preset_rc(tau, V0)
    x_label, y_label = "t (s)", "V (V)"
    st.info("Se analiza la EDO  dV/dt + V/τ = 0  escrita como "
            "(V/τ)·dt + 1·dV = 0.")

else:
    c1, c2 = st.columns(2)
    with c1:
        M_str = st.text_input("M(x, y)", value="x*y - 1",
                              help="Coeficiente que multiplica a dx")
        x_var = st.text_input("Nombre de la variable x", value="x")
    with c2:
        N_str = st.text_input("N(x, y)", value="x**2",
                              help="Coeficiente que multiplica a dy")
        y_var = st.text_input("Nombre de la variable y", value="y")
    x_label, y_label = f"{x_var}", f"{y_var}"

if st.button("🧪 Analizar ecuación", type="primary"):
    try:
        if preset is not None:
            M, N, x, y = preset["M"], preset["N"], preset["x"], preset["y"]
            cond_inicial = preset["initial_condition"]
        else:
            M, N, x, y = ee.parse_MN(M_str, N_str, x_var, y_var)
            cond_inicial = None  # para personalizada no se da condición inicial

        resultado = ee.analyze(M, N, x, y, initial_condition=cond_inicial)

        # ── Veredicto ───────────────────────────────────────────────────────
        if resultado["is_exact"]:
            st.success("La ecuación **SÍ es exacta**: ∂M/∂y = ∂N/∂x.")
        else:
            if resultado["mu"] is not None:
                st.warning("La ecuación **NO es exacta**, pero existe un factor "
                           "integrante que la convierte en exacta.")
            else:
                st.error("La ecuación **NO es exacta** y no se encontró factor "
                         "integrante por los dos criterios habituales.")

        if resultado["errors"]:
            for e in resultado["errors"]:
                st.warning(e)

        # ── Procedimiento paso a paso ───────────────────────────────────────
        st.markdown("### Procedimiento paso a paso")
        for paso in resultado["steps"]:
            if paso["title"]:
                st.markdown(f"**{paso['title']}**")
            if paso["kind"] == "latex":
                st.latex(paso["detail"])
            else:
                st.markdown(paso["detail"])

    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:  # cualquier error simbólico inesperado
        st.error(f"Ocurrió un error al analizar la ecuación: {exc}")

st.divider()
with st.expander("📖 Recordatorio del método (resumen teórico)"):
    st.markdown(
        """
        1. **Exactitud**: comprobar si $\\partial M/\\partial y = \\partial N/\\partial x$.
        2. **Factor integrante** (si no es exacta):
           - Si $\\frac{M_y - N_x}{N}$ depende solo de $x$ → $\\mu(x)=e^{\\int\\! f(x)\\,dx}$.
           - Si $\\frac{N_x - M_y}{M}$ depende solo de $y$ → $\\mu(y)=e^{\\int\\! g(y)\\,dy}$.
        3. **Transformar**: multiplicar $M$ y $N$ por $\\mu$ y re-verificar exactitud.
        4. **Potencial**: $F = \\int\\! \\tilde M\\,dx + g(y)$, con $g'(y)=\\tilde N - \\partial_y\\!\\int\\!\\tilde M\\,dx$.
        5. **Solución**: $F(x,y)=C$ (implícita); despejar $y$ si es posible.
        """
    )
