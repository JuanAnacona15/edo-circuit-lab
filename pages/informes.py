"""pages/informes.py — Generación de informes y exportación de resultados."""

from pathlib import Path

import pandas as pd
import streamlit as st

from utils import styling

styling.inject()

from core import rc_model, regression, rl_model
from utils import export
from utils import formatting as fmt

st.title("📄 Informes y exportación")

st.markdown(
    """
    Genera un informe en **Markdown** (y PDF si está instalado `reportlab`)
    con los resultados del proyecto, y permite descargar los datos de una
    simulación en CSV.
    """
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VOLTS_CSV = PROJECT_ROOT / "data" / "Volts.csv"

# ── 1. Exportar datos de simulación (CSV) ────────────────────────────────────
st.markdown("### ⬇️ Exportar datos de simulación")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Circuito RC (descarga, parámetros del proyecto)**")
    sim_rc = rc_model.simulate(9.2128, 0.4896, 1.0, 0.02, mode="discharge")
    df_rc = pd.DataFrame({"t (s)": sim_rc["t"], "V (V)": sim_rc["V"]})
    st.download_button(
        "Descargar RC (CSV)",
        data=export.df_to_csv_bytes(df_rc),
        file_name="simulacion_rc.csv",
        mime="text/csv",
    )
with col2:
    st.markdown("**Circuito RL (ejercicio del proyecto)**")
    sim_rl = rl_model.simulate(4.0, 2.0, 12.0, 0.0, 1.0, 0.02)
    df_rl = pd.DataFrame({"t (s)": sim_rl["t"], "i (A)": sim_rl["i"]})
    st.download_button(
        "Descargar RL (CSV)",
        data=export.df_to_csv_bytes(df_rl),
        file_name="simulacion_rl.csv",
        mime="text/csv",
    )

st.divider()

# ── 2. Informe en Markdown / PDF ─────────────────────────────────────────────
st.markdown("### 📝 Informe del proyecto")

# Construimos el informe con los resultados REALES calculados ahora mismo.
fit = None
if VOLTS_CSV.exists():
    df, problemas = regression.load_dataset(path=str(VOLTS_CSV))
    validos = df.dropna(subset=["t", "V"])
    if len(validos) >= 2 and (validos["V"] > 0).all():
        fit = regression.fit_discharge(validos["t"].to_numpy(), validos["V"].to_numpy())

linea_reg = ""
if fit:
    linea_reg = (f"- V₀ estimado = {fmt.fmt_es(fit['V0'])} V\n"
                 f"- Constante de tiempo τ = {fmt.fmt_es(fit['tau'])} s\n"
                 f"- Pendiente m = {fmt.fmt_es(fit['m'])} s⁻¹\n"
                 f"- Coeficiente R² = {fmt.fmt_es(fit['r2'], 5)}\n")

secciones = [
    ("Circuito RC (problema real)",
     "Modelo de descarga del capacitor:\n\n"
     "- EDO: dV/dt = −V/τ, con τ = RC\n"
     "- Solución analítica: V(t) = V₀·e^(−t/τ)\n"
     "- Condición inicial: V(0) = 9,2128 V\n"
     "- Constante de tiempo: τ = 0,4896 s\n"
     f"{linea_reg}"
     "- A 5τ el capacitor está descargado en ≈99,3 % (nunca llega a 0 exactamente)."),
    ("Circuito RL (ejercicio complementario)",
     "- EDO: L·di/dt + R·i = E₀\n"
     "- Solución: i(t) = E₀/R + (i₀ − E₀/R)·e^(−(R/L)t)\n"
     "- Con R = 4 Ω, L = 2 H, E₀ = 12 V, i₀ = 0 A:\n"
     "- i(t) = 3(1 − e^(−2t)), τ = 0,5 s, I∞ = 3 A"),
    ("Ecuaciones exactas",
     "- RC: (V/τ)·dt + 1·dV = 0 → no exacta → μ(t) = e^(t/τ)\n"
     "- RL: (R·i − E₀)·dt + L·di = 0 → no exacta → μ(t) = e^((R/L)t)\n"
     "- En ambos casos el factor integrante convierte la ecuación en exacta."),
    ("Validación computacional",
     "- SymPy resuelve la EDO de forma simbólica (solución exacta).\n"
     "- SciPy (solve_ivp, método RK45) integra el PVI numéricamente.\n"
     "- El error entre ambas soluciones es del orden del error numérico."),
]

reporte = export.build_markdown_report(secciones)

with st.expander("Vista previa del informe", expanded=False):
    st.markdown(reporte)

st.download_button(
    "⬇️ Descargar informe (Markdown)",
    data=reporte.encode("utf-8"),
    file_name="informe_edo_circuit_lab.md",
    mime="text/markdown",
)

pdf = export.text_to_pdf(reporte)
if pdf is not None:
    st.download_button(
        "⬇️ Descargar informe (PDF)",
        data=pdf,
        file_name="informe_edo_circuit_lab.pdf",
        mime="application/pdf",
    )
else:
    st.caption("Para exportar a PDF, instala `reportlab` y reinicia la app "
               "(dependencia opcional).")
