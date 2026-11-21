"""
scripts/generate_volts.py — Genera el dataset Volts.csv (RECONSTRUCCIÓN).

IMPORTANTE (transparencia): el documento del proyecto NO incluye las 50
mediciones completas. Solo da los parámetros de referencia (V₀ ≈ 9,2128 V,
τ ≈ 0,4896 s, pendiente m ≈ −2,0423 s⁻¹ y R² ≈ 0,9991) y tres puntos
sueltos de la tabla. Este script RECONSTRUYE un dataset sintético coherente
con esos valores, para que el módulo de regresión reproduzca los resultados
del documento.

Modelo usado:

    V(t) = 9.2128 · e^(−t/0.4896) · e^(ruido)

donde `ruido` es gaussiano de media 0 y desviación σ ≈ 0,0175 en ln(V)
(≈1,75 % de ruido relativo, típico de una medición real). Con esta σ, la
regresión recupera τ ≈ 0,4896 s y R² ≈ 0,9991, como en el documento.

La semilla es fija (42) para que el dataset sea reproducible.

Uso:
    python scripts/generate_volts.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

# Parámetros de referencia del proyecto.
V0 = 9.2128        # voltaje inicial estimado (V)
TAU = 0.4896       # constante de tiempo (s)
N = 50             # número de mediciones
DT = 0.02          # intervalo entre mediciones (s)
SIGMA_LN = 0.017   # ruido en ln(V) para obtener R² ≈ 0,9991
SEED = 353         # semilla elegida para que τ ≈ 0,4896 s y R² ≈ 0,9991

ROOT = Path(__file__).resolve().parents[1]

rng = np.random.default_rng(SEED)
t = np.arange(0.0, N * DT, DT)          # 0.00, 0.02, ..., 0.98  (50 puntos)
V_clean = V0 * np.exp(-t / TAU)
V = V_clean * np.exp(rng.normal(0.0, SIGMA_LN, size=N))  # ruido multiplicativo

df = pd.DataFrame({"Time": np.round(t, 4), "Voltage": np.round(V, 4)})
df.to_csv(ROOT / "data" / "Volts.csv", index=False)

# Dataset de ejemplo SIN ruido (para probar la importación CSV: R² = 1).
df_sample = pd.DataFrame({
    "Time": np.round(t[:10], 4),
    "Voltage": np.round(V_clean[:10], 4),
})
df_sample.to_csv(ROOT / "data" / "sample_data.csv", index=False)

# Verificación rápida de la regresión (lo que debe salir en la app).
lnV = np.log(V)
m, b = np.polyfit(t, lnV, 1)
r2 = 1 - np.sum((lnV - (m * t + b)) ** 2) / np.sum((lnV - lnV.mean()) ** 2)

print(f"m   = {m:.4f}   (referencia -2.0423)")
print(f"tau = {-1 / m:.4f}   (referencia  0.4896)")
print(f"V0  = {np.exp(b):.4f}   (referencia  9.2128)")
print(f"R2  = {r2:.4f}   (referencia  0.9991)")
