"""
core/regression.py — Análisis de los datos experimentales RC
=============================================================

Este módulo implementa la REGRESIÓN LINEAL del logaritmo del voltaje
respecto al tiempo. Es el paso clave para estimar la constante de tiempo τ
a partir de las mediciones reales.

--------------------------------------------------------------------------
1) POR QUÉ UNA REGRESIÓN LINEAL SI EL MODELO ES EXPONENCIAL
--------------------------------------------------------------------------
El modelo de descarga es exponencial:

        V(t) = V₀·e^{-t/τ}

Tomando logaritmo natural a ambos lados:

        ln(V) = ln(V₀) - (1/τ)·t                            (1)

La ecuación (1) es una RECTA en las variables (t, ln(V)):

        y = b + m·t      con     y = ln(V)
                                 b = ln(V₀)      (intercepto)
                                 m = -1/τ        (pendiente)

Por tanto, ajustar una recta a los datos (t, ln V) permite estimar:

        V₀ = e^b        y        τ = -1/m

--------------------------------------------------------------------------
2) MÍNIMOS CUADRADOS ORDINARIOS (fórmulas cerradas)
--------------------------------------------------------------------------
Dados n puntos (x_i, y_i), la recta y = m·x + b que minimiza la suma de
residuos al cuadrado  Σ(y_i - (m x_i + b))²  tiene la solución:

        m = (n·Σxy - Σx·Σy) / (n·Σx² - (Σx)²)             (2a)
        b = (Σy - m·Σx) / n                               (2b)

(se obtienen igualando a cero las derivadas parciales del error respecto a
m y a b: son las llamadas "ecuaciones normales").

--------------------------------------------------------------------------
3) COEFICIENTE DE DETERMINACIÓN R²
--------------------------------------------------------------------------
R² mide qué fracción de la variabilidad de y explica el modelo lineal:

        R² = 1 - SS_res / SS_tot

con:
        SS_res = Σ (y_i - ŷ_i)²      (residuos: lo que el modelo NO explica)
        SS_tot = Σ (y_i - ȳ)²        (variabilidad total respecto a la media)

R² ∈ [0, 1]; cuanto más cerca de 1, mejor es el ajuste. En el proyecto se
reporta R² ≈ 0,9991 (ajuste casi perfecto).

--------------------------------------------------------------------------
4) ERRORES ESTÁNDAR DE LOS COEFICIENTES
--------------------------------------------------------------------------
Para valorar la incertidumbre de m y b se usa la varianza residual
s² = SS_res/(n-2) (se restan 2 grados de libertad por estimar m y b):

        SE(m) = sqrt( s² / Σ(x_i - x̄)² )
        SE(b) = sqrt( s² · (1/n + x̄² / Σ(x_i - x̄)² ) )
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def linear_regression(x, y) -> dict:
    """Ajusta y = m·x + b por mínimos cuadrados (fórmulas cerradas).

    Parámetros:
        x, y : arrays 1-D de igual longitud (x = tiempo, y = ln(V))

    Devuelve un diccionario con m, b, R² y los errores estándar.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = float(x.size)

    if x.size != y.size:
        raise ValueError("x e y deben tener la misma longitud.")
    if x.size < 2:
        raise ValueError("Se necesitan al menos 2 puntos para ajustar una recta.")

    Sx = np.sum(x)
    Sy = np.sum(y)
    Sxx = np.sum(x * x)
    Sxy = np.sum(x * y)

    # Pendiente e intercepto (ecuaciones normales, ver docstring).
    denom = n * Sxx - Sx * Sx
    m = (n * Sxy - Sx * Sy) / denom
    b = (Sy - m * Sx) / n

    # Valores ajustados y residuos.
    y_pred = m * x + b
    residuos = y - y_pred
    SS_res = np.sum(residuos**2)
    SS_tot = np.sum((y - np.mean(y)) ** 2)

    # R²: si SS_tot es 0 (y constante) el ajuste es trivialmente perfecto.
    r2 = 1.0 - SS_res / SS_tot if SS_tot > 0 else 1.0

    # Errores estándar (ver docstring, sección 4).
    x_centrado = x - np.mean(x)
    Sxx_centrado = np.sum(x_centrado**2)
    if n > 2 and Sxx_centrado > 0:
        s2 = SS_res / (n - 2)
        se_m = float(np.sqrt(s2 / Sxx_centrado))
        se_b = float(np.sqrt(s2 * (1.0 / n + np.mean(x) ** 2 / Sxx_centrado)))
    else:
        se_m = se_b = float("nan")

    return {"m": float(m), "b": float(b), "r2": float(r2),
            "se_m": se_m, "se_b": se_b,
            "y_pred": y_pred, "residuals": residuos}


def fit_discharge(t, V) -> dict:
    """Estima V₀, τ y R² ajustando ln(V) = ln(V₀) - t/τ a los datos.

    Parámetros:
        t : tiempos (array)
        V : voltajes medidos (array), todos positivos para poder usar ln

    Devuelve un diccionario con m, b, V₀, τ, R² y los arrays intermedios.
    Lanza ValueError si hay voltajes no positivos (ln no definido).
    """
    t = np.asarray(t, dtype=float)
    V = np.asarray(V, dtype=float)

    if np.any(V <= 0):
        raise ValueError(
            "Hay voltajes ≤ 0. El logaritmo ln(V) solo está definido para V > 0; "
            "revisa los datos o usa el modelo sin logaritmo."
        )

    lnV = np.log(V)
    reg = linear_regression(t, lnV)

    m, b = reg["m"], reg["b"]
    V0 = float(np.exp(b))       # V₀ = e^b
    tau = float(-1.0 / m)       # τ = -1/m  (pues m = -1/τ)

    V_fit = V0 * np.exp(-t / tau)   # modelo ajustado en voltaje (no en ln)

    return {
        "m": m, "b": b, "r2": reg["r2"],
        "se_m": reg["se_m"], "se_b": reg["se_b"],
        "V0": V0, "tau": tau,
        "t": t, "V": V, "lnV": lnV, "V_fit": V_fit,
        "residuals_V": V - V_fit,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Carga y validación de datos experimentales (CSV)
# ─────────────────────────────────────────────────────────────────────────────


def load_dataset(path=None, df=None) -> tuple[pd.DataFrame, list[str]]:
    """Carga y valida un conjunto de mediciones de descarga.

    Acepta una ruta CSV (`path`) o un DataFrame (`df`). Normaliza los nombres
    de columna: acepta 'Time'/'t'/'tiempo' y 'Voltage'/'V'/'voltaje'.

    Devuelve (df_normalizado, problemas), donde `problemas` es una lista de
    mensajes describiendo cada registro con errores (vacía si todo está bien).
    """
    problemas: list[str] = []

    if df is None:
        if path is None:
            return pd.DataFrame(), ["No se indicó archivo ni DataFrame."]
        try:
            df = pd.read_csv(path)
        except Exception as exc:
            return pd.DataFrame(), [f"No se pudo leer el archivo CSV: {exc}"]

    if df is None or len(df) == 0:
        return pd.DataFrame(), ["El archivo está vacío."]

    # Normalizar nombres de columnas (búsqueda insensible a mayúsculas).
    df = df.copy()
    col_map = {}
    for col in df.columns:
        nombre = str(col).strip().lower()
        if nombre in ("time", "t", "tiempo", "tiempos"):
            col_map[col] = "t"
        elif nombre in ("voltage", "v", "voltaje", "voltios", "volts"):
            col_map[col] = "V"
    df = df.rename(columns=col_map)

    if "t" not in df.columns:
        return df, ["Falta la columna de tiempo (Time/t)."]
    if "V" not in df.columns:
        return df, ["Falta la columna de voltaje (Voltage/V)."]

    # Convertir a numérico; los no convertibles se marcan como NaN.
    df["t"] = pd.to_numeric(df["t"], errors="coerce")
    df["V"] = pd.to_numeric(df["V"], errors="coerce")

    # Detectar registros problemáticos (sin eliminarlos silenciosamente).
    if df["t"].isna().any():
        problemas.append(f"{int(df['t'].isna().sum())} tiempo(s) no numérico(s).")
    if df["V"].isna().any():
        problemas.append(f"{int(df['V'].isna().sum())} voltaje(s) no numérico(s).")

    validos = df.dropna(subset=["t", "V"])

    if (validos["t"] < 0).any():
        problemas.append("Hay tiempos negativos.")
    if (validos["V"] <= 0).any():
        problemas.append("Hay voltajes ≤ 0 (ln(V) no definido).")
    if validos["t"].duplicated().any():
        problemas.append("Hay tiempos duplicados.")
    if len(validos) > 1 and not validos["t"].is_monotonic_increasing:
        problemas.append("Las mediciones no están ordenadas temporalmente.")

    # Ordenar por tiempo para que la regresión sea correcta.
    df = df.sort_values("t").reset_index(drop=True)
    return df, problemas
