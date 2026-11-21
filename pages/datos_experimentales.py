"""pages/datos_experimentales.py — Análisis de las mediciones de descarga RC.

Problema real del proyecto: cargar los 50 datos de voltaje, ajustar
ln(V) vs t por mínimos cuadrados y estimar V₀, τ y R².
"""

from pathlib import Path

import streamlit as st

from utils import styling

styling.inject()

from core import regression
from utils import export
from utils import formatting as fmt
from utils import plotting

st.title("📊 Datos experimentales RC")

st.markdown(
    """
    El modelo de descarga $V(t) = V_0 e^{-t/\\tau}$ se vuelve una RECTA al
    tomar logaritmos:

    $$
    \\ln(V) = \\ln(V_0) - \\frac{1}{\\tau}\\,t
    $$

    Ajustando una regresión lineal a los puntos $(t, \\ln V)$ se estiman
    $V_0 = e^b$ y $\\tau = -1/m$ (donde $m$ y $b$ son pendiente e
    intercepto de la recta).
    """
)

# Ruta absoluta del dataset (robusta aunque se lance desde otro directorio).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VOLTS_CSV = PROJECT_ROOT / "data" / "Volts.csv"

origen = st.radio(
    "Fuente de datos",
    ["Cargar los 50 datos del proyecto", "Subir archivo CSV propio"],
    horizontal=True,
)

df_raw = None
if origen.startswith("Cargar"):
    if VOLTS_CSV.exists():
        import pandas as pd
        df_raw = pd.read_csv(VOLTS_CSV)
        st.caption(f"Dataset: {VOLTS_CSV.name} ({len(df_raw)} filas).")
    else:
        st.error("No se encontró data/Volts.csv.")
else:
    archivo = st.file_uploader("Subir CSV (columnas Time y Voltage)", type=["csv"])
    if archivo is not None:
        import pandas as pd
        df_raw = pd.read_csv(archivo)

if df_raw is None:
    st.stop()

# ── Carga y validación ───────────────────────────────────────────────────────
df, problemas = regression.load_dataset(df=df_raw)

if problemas:
    st.warning("Se detectaron los siguientes problemas (los registros se "
               "marcan, no se eliminan silenciosamente):")
    for p in problemas:
        st.markdown(f"- {p}")

if df.empty or "t" not in df.columns or "V" not in df.columns:
    st.error("No hay datos utilizables (faltan columnas Time/Voltage).")
    st.stop()

validos = df.dropna(subset=["t", "V"])
if len(validos) < 2:
    st.error("Se necesitan al menos 2 mediciones válidas.")
    st.stop()
if (validos["V"] <= 0).any():
    st.error("Hay voltajes ≤ 0: ln(V) no está definido. Corrige los datos.")
    st.stop()

# ── Regresión ────────────────────────────────────────────────────────────────
fit = regression.fit_discharge(validos["t"].to_numpy(), validos["V"].to_numpy())

st.markdown("### Resultados de la regresión")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Voltaje inicial V₀", f"{fmt.fmt_es(fit['V0'])} V")
c2.metric("Constante de tiempo τ", f"{fmt.fmt_es(fit['tau'])} s")
c3.metric("Pendiente m", f"{fmt.fmt_es(fit['m'])} s⁻¹")
c4.metric("Intercepto b", f"{fmt.fmt_es(fit['b'])}")
c5.metric("R²", f"{fmt.fmt_es(fit['r2'], 5)}")

st.markdown("#### Comparación con los valores de referencia del proyecto")
st.markdown(
    f"""
    | Magnitud | Referencia | Calculado | Diferencia |
    |----------|-----------|-----------|------------|
    | V₀ (V) | 9,2128 | {fmt.fmt_es(fit['V0'])} | {fmt.fmt_es(fit['V0'] - 9.2128)} |
    | τ (s) | 0,4896 | {fmt.fmt_es(fit['tau'])} | {fmt.fmt_es(fit['tau'] - 0.4896)} |
    | m (s⁻¹) | −2,0423 | {fmt.fmt_es(fit['m'])} | {fmt.fmt_es(fit['m'] - (-2.0423))} |
    | R² | 0,9991 | {fmt.fmt_es(fit['r2'], 5)} | {fmt.fmt_es(fit['r2'] - 0.9991, 6)} |
    """
)

# ── Tabla de mediciones ──────────────────────────────────────────────────────
st.markdown("### Tabla de mediciones")
tabla = validos.copy().reset_index(drop=True)
tabla.insert(0, "Registro", range(1, len(tabla) + 1))
tabla["V_estimado"] = fit["V_fit"]
tabla["Diferencia"] = fit["residuals_V"]
tabla = tabla.rename(columns={"t": "Tiempo (s)", "V": "Voltaje medido (V)",
                              "V_estimado": "Voltaje estimado (V)",
                              "Diferencia": "Diferencia (V)"})
st.dataframe(tabla, width="stretch", height=320)

# ── Gráficas ─────────────────────────────────────────────────────────────────
st.markdown("### Visualización")
st.plotly_chart(
    plotting.figure_regression(fit["t"], fit["V"], fit["lnV"], fit["V_fit"],
                               fit["m"], fit["b"]),
    width="stretch",
)

# ── Exportación ──────────────────────────────────────────────────────────────
st.download_button(
    "⬇️ Descargar resultados (CSV)",
    data=export.df_to_csv_bytes(tabla),
    file_name="resultados_regresion.csv",
    mime="text/csv",
)
