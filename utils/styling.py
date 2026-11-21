"""
utils/styling.py — Tema visual "neón futurista" de la aplicación
=================================================================

Define la paleta de colores neón y el CSS global (fondo oscuro con
gradiente, títulos con resplandor, botones y tarjetas con efecto neón y
animaciones sutiles). Se inyecta con `inject()` desde cada página.

Nota: Streamlit renderiza el HTML de cada página de forma independiente,
por eso cada página llama a `styling.inject()` al inicio (es idempotente).
"""

import streamlit as st

# ── Paleta neón (compartida con utils/plotting.py) ───────────────────────────
CYAN = "#00e5ff"
MAGENTA = "#ff00e5"
PURPLE = "#8b5cf6"
BLUE = "#4d7cfe"
GREEN = "#00ff9f"
AMBER = "#ffb020"
PINK = "#ff2d95"
BG0 = "#05060f"
BG1 = "#0a0b1e"
BG2 = "#10122b"
TEXT = "#e8ecff"
MUTED = "#8b93b8"

# ── CSS global ───────────────────────────────────────────────────────────────
_CSS = f"""
<style>
/* ============ FONDO: oscuro con gradiente profundo ============ */
.stApp {{
  background:
    radial-gradient(ellipse at 15% 0%, rgba(139,92,246,0.18), transparent 55%),
    radial-gradient(ellipse at 85% 100%, rgba(0,229,255,0.14), transparent 55%),
    linear-gradient(160deg, {BG0} 0%, {BG1} 45%, #120b2e 100%);
}}

/* Ocultar la barra superior por defecto (más limpio). */
[data-testid="stHeader"] {{
  background: transparent;
}}

/* Contenido principal: entrada suave */
.block-container {{
  padding-top: 2.6rem;
  animation: fadeInUp 0.7s ease both;
}}
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: none; }}
}}

/* ============ TÍTULOS con resplandor neón ============ */
h1 {{
  font-weight: 800;
  letter-spacing: 0.5px;
  background: linear-gradient(90deg, {CYAN}, {PURPLE}, {MAGENTA});
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  filter: drop-shadow(0 0 12px rgba(0,229,255,0.45));
  animation: heroShift 5s linear infinite;
}}
h2 {{
  color: {CYAN};
  text-shadow: 0 0 12px rgba(0,229,255,0.55);
  letter-spacing: 0.4px;
}}
h3 {{
  color: {PURPLE};
  text-shadow: 0 0 10px rgba(139,92,246,0.5);
  letter-spacing: 0.3px;
}}
@keyframes heroShift {{ to {{ background-position: 200% center; }} }}

/* ============ SIDEBAR ============ */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, {BG1} 0%, {BG0} 100%);
  border-right: 1px solid rgba(0,229,255,0.22);
  box-shadow: 4px 0 30px rgba(0,229,255,0.10);
}}

/* ============ BOTONES ============ */
.stButton > button {{
  border: 1px solid rgba(0,229,255,0.45);
  border-radius: 10px;
  background: rgba(0,229,255,0.08);
  color: {TEXT};
  font-weight: 600;
  transition: all 0.25s ease;
}}
.stButton > button:hover {{
  border-color: {MAGENTA};
  color: #ffffff;
  box-shadow: 0 0 18px rgba(0,229,255,0.55), 0 0 30px rgba(255,0,229,0.25);
  transform: translateY(-1px);
}}
/* Botón primario: gradiente animado */
[data-testid="stBaseButton-primary"] {{
  border: none !important;
  background: linear-gradient(90deg, {CYAN}, {PURPLE}, {MAGENTA}) !important;
  background-size: 200% auto !important;
  color: {BG0} !important;
  font-weight: 800 !important;
  box-shadow: 0 0 18px rgba(0,229,255,0.55);
  animation: heroShift 3s linear infinite;
}}
[data-testid="stBaseButton-primary"]:hover {{
  box-shadow: 0 0 26px rgba(0,229,255,0.8), 0 0 40px rgba(255,0,229,0.4);
}}

/* ============ MÉTRICAS (tarjetas de resultados) ============ */
[data-testid="stMetric"] {{
  background: rgba(16,18,43,0.72);
  border: 1px solid rgba(139,92,246,0.35);
  border-radius: 12px;
  padding: 10px 14px;
  box-shadow: 0 0 16px rgba(139,92,246,0.15);
  transition: box-shadow 0.25s ease;
}}
[data-testid="stMetric"]:hover {{
  box-shadow: 0 0 22px rgba(0,229,255,0.35);
}}
[data-testid="stMetricValue"] {{
  color: {CYAN};
  text-shadow: 0 0 12px rgba(0,229,255,0.7);
  font-weight: 800;
}}
[data-testid="stMetricLabel"] {{ color: {MUTED}; }}

/* ============ ENTRADAS ============ */
[data-testid="stNumberInput"] input,
.stTextInput input {{
  background: rgba(10,11,30,0.85) !important;
  color: {TEXT} !important;
  border: 1px solid rgba(0,229,255,0.30) !important;
  border-radius: 8px !important;
}}
[data-testid="stNumberInput"] input:focus,
.stTextInput input:focus {{
  border-color: {CYAN} !important;
  box-shadow: 0 0 12px rgba(0,229,255,0.45) !important;
}}

/* ============ DATAFRAME ============ */
[data-testid="stDataFrame"] {{
  border: 1px solid rgba(0,229,255,0.25);
  border-radius: 10px;
  box-shadow: 0 0 16px rgba(0,229,255,0.12);
  overflow: hidden;
}}

/* ============ EXPANDER ============ */
[data-testid="stExpander"] {{
  border: 1px solid rgba(139,92,246,0.35);
  border-radius: 10px;
  background: rgba(10,11,30,0.55);
  box-shadow: 0 0 14px rgba(139,92,246,0.12);
}}

/* ============ TARJETA NEÓN (clase auxiliar) ============ */
.neon-card {{
  background: linear-gradient(135deg, rgba(16,18,43,0.85), rgba(10,11,30,0.85));
  border: 1px solid rgba(0,229,255,0.32);
  border-radius: 14px;
  padding: 1rem 1.2rem;
  margin-bottom: 0.8rem;
  box-shadow: 0 0 20px rgba(0,229,255,0.14), inset 0 0 22px rgba(139,92,246,0.06);
}}
.neon-card p {{ margin: 0.25rem 0; color: {TEXT}; }}

/* ============ TEXTO SECUNDARIO ============ */
[data-testid="stCaptionContainer"], .stCaption {{ color: {MUTED}; }}

/* Scrollbar (Chromium) */
::-webkit-scrollbar {{ width: 10px; }}
::-webkit-scrollbar-thumb {{
  background: linear-gradient({PURPLE}, {CYAN});
  border-radius: 6px;
}}
::-webkit-scrollbar-track {{ background: {BG0}; }}
</style>
"""


def inject():
    """Inyecta el CSS global. Llamar al inicio de cada página."""
    st.markdown(_CSS, unsafe_allow_html=True)


def neon_card(markdown_text: str) -> None:
    """Envuelve contenido Markdown en una tarjeta con borde neón."""
    st.markdown(f'<div class="neon-card">{markdown_text}</div>',
                unsafe_allow_html=True)
