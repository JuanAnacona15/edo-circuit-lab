"""
utils/plotting.py — Generación de gráficas (Plotly y Matplotlib)
=================================================================

Dos motores de gráficas, cada uno con su papel:

    * Plotly      -> gráficas INTERACTIVAS para la app (zoom, hover, etc.):
                     RC, RL, regresión y comparación.
    * Matplotlib  -> FIGURAS CIENTÍFICAS "clásicas" exigidas por el
                     documento, sobre todo el campo de direcciones.

Ambas se alimentan de arrays de NumPy ya calculados en core/.
"""

from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend sin ventana (obligatorio en servidor/Streamlit)
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Colores coherentes con la paleta "científica azul" de la app.
AZUL = "#1f4e79"
AZUL_CLARO = "#2e86c1"
NARANJA = "#e67e22"
VERDE = "#27ae60"
ROJO = "#c0392b"
GRIS = "#7f8c8d"


# ─────────────────────────────────────────────────────────────────────────────
# Circuito RC
# ─────────────────────────────────────────────────────────────────────────────


def figure_rc(t, V, tau, V0, mode="discharge", E0=None) -> go.Figure:
    """Curva de voltaje del RC con las marcas 1τ / 3τ / 5τ.

    Las líneas verticales en t = τ, 3τ y 5τ permiten visualizar la regla
    práctica: a τ queda el 36,8 %, a 3τ el 5 % y a 5τ el 0,7 % del valor.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=V, mode="lines", name="V(t)",
        line=dict(color=AZUL, width=3),
        hovertemplate="t = %{x:.3f} s<br>V = %{y:.4f} V<extra></extra>",
    ))

    # Marca de τ, 3τ y 5τ (solo si caen dentro del rango simulado).
    for k, color, etiqueta in [(1, NARANJA, "τ"), (3, VERDE, "3τ"), (5, ROJO, "5τ")]:
        tk = k * tau
        if tk <= float(t[-1]):
            Vk = V0 * np.exp(-k) if mode == "discharge" else None
            if Vk is None:  # en carga, V(τ) = E0 + (V0-E0)e^-1
                Vk = E0 + (V0 - E0) * np.exp(-k)
            fig.add_vline(x=tk, line_dash="dash", line_color=color,
                          line_width=1, annotation_text=f"{etiqueta}", opacity=0.7)

    fig.update_layout(
        title=("Descarga del capacitor" if mode == "discharge" else "Carga del capacitor"),
        xaxis_title="Tiempo t (s)",
        yaxis_title="Voltaje V (V)",
        template="plotly_white",
        hovermode="x unified",
        height=420,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Circuito RL
# ─────────────────────────────────────────────────────────────────────────────


def figure_rl(t, i, tau, i_inf, i0) -> go.Figure:
    """Curva de corriente del RL, con la asíntota de estado estacionario.

    La línea punteada horizontal en I∞ = E₀/R muestra el valor al que la
    corriente tiende cuando t → ∞ (la bobina se comporta como un cable).
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=i, mode="lines", name="i(t)",
        line=dict(color=AZUL, width=3),
        hovertemplate="t = %{x:.3f} s<br>i = %{y:.4f} A<extra></extra>",
    ))
    # Asíntota de estado estacionario.
    fig.add_hline(y=i_inf, line_dash="dash", line_color=ROJO, line_width=1,
                  annotation_text="I∞ = E₀/R", opacity=0.7)
    # Marca de τ.
    if tau <= float(t[-1]):
        i_tau = i_inf + (i0 - i_inf) * np.exp(-1)
        fig.add_vline(x=tau, line_dash="dot", line_color=NARANJA, line_width=1,
                      annotation_text="τ", opacity=0.7)

    fig.update_layout(
        title="Respuesta de corriente del circuito RL",
        xaxis_title="Tiempo t (s)",
        yaxis_title="Corriente i (A)",
        template="plotly_white",
        hovermode="x unified",
        height=420,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Regresión de los datos experimentales (dos paneles)
# ─────────────────────────────────────────────────────────────────────────────


def figure_regression(t, V, lnV, V_fit, m, b) -> go.Figure:
    """Dos paneles: (izq) V vs t con el modelo exponencial; (der) ln(V) vs t
    con la recta de regresión. Así se VE por qué una exponencial se vuelve
    una recta al tomar logaritmos."""
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "Voltaje experimental y modelo exponencial",
        "Regresión lineal de ln(V) vs t"),
    )

    # Panel izquierdo: datos medidos (puntos) + modelo ajustado (línea).
    fig.add_trace(go.Scatter(
        x=t, y=V, mode="markers", name="Mediciones",
        marker=dict(color=AZUL_CLARO, size=6),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=t, y=V_fit, mode="lines", name="Modelo V₀e^(−t/τ)",
        line=dict(color=NARANJA, width=2),
    ), row=1, col=1)

    # Panel derecho: ln(V) (puntos) + recta y = m·t + b (línea).
    fig.add_trace(go.Scatter(
        x=t, y=lnV, mode="markers", name="ln(V) medido",
        marker=dict(color=AZUL_CLARO, size=6),
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=t, y=m * t + b, mode="lines", name="Recta y = m·t + b",
        line=dict(color=NARANJA, width=2),
    ), row=1, col=2)

    fig.update_xaxes(title_text="Tiempo t (s)", row=1, col=1)
    fig.update_xaxes(title_text="Tiempo t (s)", row=1, col=2)
    fig.update_yaxes(title_text="Voltaje V (V)", row=1, col=1)
    fig.update_yaxes(title_text="ln(V)", row=1, col=2)
    fig.update_layout(template="plotly_white", height=430, showlegend=False)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Comparación analítica vs numérica
# ─────────────────────────────────────────────────────────────────────────────


def figure_comparison(t, y_analytic, y_numeric, abs_err, ylabel="V (V)") -> go.Figure:
    """Superpone la solución analítica y la numérica, y debajo grafica el
    error absoluto |y_a - y_n| para apreciar cuán pequeña es la diferencia."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Soluciones analítica y numérica",
                                        "Error absoluto |y_a − y_n|"),
                        row_heights=[0.7, 0.3])

    fig.add_trace(go.Scatter(
        x=t, y=y_analytic, mode="lines", name="Analítica (SymPy/exacta)",
        line=dict(color=AZUL, width=2),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=t, y=y_numeric, mode="lines", name="Numérica (RK45)",
        line=dict(color=NARANJA, width=2, dash="dash"),
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=t, y=abs_err, mode="lines", name="|Error absoluto|",
        line=dict(color=ROJO, width=1.5), fill="tozeroy",
    ), row=2, col=1)

    fig.update_xaxes(title_text="Tiempo t (s)", row=2, col=1)
    fig.update_yaxes(title_text=ylabel, row=1, col=1)
    fig.update_yaxes(title_text="Error", row=2, col=1)
    fig.update_layout(template="plotly_white", height=520,
                      hovermode="x unified")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Múltiples curvas (variación de parámetros)
# ─────────────────────────────────────────────────────────────────────────────


def figure_multi_curves(curves, xlabel="Tiempo t (s)", ylabel="", title="") -> go.Figure:
    """Dibuja varias curvas en la misma gráfica (comparación de escenarios).

    `curves` es una lista de tuplas (t, y, nombre).
    """
    fig = go.Figure()
    for t, y, nombre in curves:
        fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name=nombre,
                                 line=dict(width=2)))
    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel,
                      template="plotly_white", height=430,
                      hovermode="x unified")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Campo de direcciones (Matplotlib)
# ─────────────────────────────────────────────────────────────────────────────


def figure_direction_field(ode_rhs, x_lim, y_lim, curves=None, xlabel="t",
                           ylabel="y", title="Campo de direcciones", grid=22) -> plt.Figure:
    """Campo de pendientes de la EDO  y' = f(t, y).

    En cada punto (t, y) de una malla se dibuja un segmento corto cuya
    pendiente es f(t, y). Una solución de la EDO es una curva que en todo
    punto es TANGENTE a estos segmentos.

    Parámetros:
        ode_rhs : función f(t, y) (vectorizada)
        x_lim, y_lim : tuplas (min, max) del dominio a dibujar
        curves  : lista de (t, y, etiqueta) para superponer soluciones
    """
    t = np.linspace(x_lim[0], x_lim[1], grid)
    y = np.linspace(y_lim[0], y_lim[1], grid)
    T, Y = np.meshgrid(t, y)

    dydt = np.asarray(ode_rhs(T, Y), dtype=float)

    # Normalizamos las flechas a longitud 1 para que todas se vean igual;
    # la DIRECCIÓN (pendiente) es lo que transmite la información.
    U = np.ones_like(dydt)
    norm = np.hypot(U, dydt)
    norm[norm == 0] = 1.0  # evita división por cero en puntos singulares

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.quiver(T, Y, U / norm, dydt / norm, angles="xy",
              pivot="mid", color=AZUL_CLARO, alpha=0.55, width=0.002)

    if curves:
        for tc, yc, etiqueta in curves:
            ax.plot(tc, yc, lw=2.2, label=etiqueta)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    if curves:
        ax.legend()
    fig.tight_layout()
    return fig
