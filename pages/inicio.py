"""pages/inicio.py — Pantalla de bienvenida y navegación."""

import streamlit as st

from utils import styling

styling.inject()

st.title("⚡ EDO Circuit Lab")
st.markdown(
    '<div style="font-size:1.1rem; color:#8b93b8; margin-top:-0.5rem; letter-spacing:0.4px;">'
    'Laboratorio interactivo de '
    '<span style="color:#00e5ff; text-shadow:0 0 10px rgba(0,229,255,0.6);">ecuaciones diferenciales</span> '
    'aplicadas a circuitos '
    '<span style="color:#ff00e5; text-shadow:0 0 10px rgba(255,0,229,0.6);">RC</span> y '
    '<span style="color:#ff00e5; text-shadow:0 0 10px rgba(255,0,229,0.6);">RL</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    Esta aplicación une tres mundos que el proyecto de aula pide integrar:

    - **Electrónica** — circuitos RC (carga/descarga de un capacitor) y RL
      (respuesta de corriente en una bobina).
    - **Matemáticas** — ecuaciones diferenciales de primer orden, exactitud y
      factores integrantes.
    - **Computación** — cálculo simbólico (SymPy), simulación numérica (SciPy),
      regresión y visualización.

    El objetivo no es solo *mostrar* gráficas, sino **demostrar el
    procedimiento completo**: de la ley de Kirchhoff a la ecuación
    diferencial, de ahí a la solución analítica, y finalmente su verificación
    numérica y experimental.
    """
)

st.markdown("### 🗺️ ¿Por dónde empiezo?")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("pages/circuito_rc.py", label="🔋 Simulador RC", help="Carga y descarga del capacitor (problema real del proyecto)")
with col2:
    st.page_link("pages/circuito_rl.py", label="🧲 Simulador RL", help="Respuesta de corriente en la bobina (ejercicio complementario)")
with col3:
    st.page_link("pages/ecuaciones_exactas.py", label="🧮 Ecuaciones exactas", help="Criterio de exactitud y factores integrantes")
with col4:
    st.page_link("pages/datos_experimentales.py", label="📊 Datos experimentales", help="Regresión lineal de las 50 mediciones")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.page_link("pages/comparacion.py", label="⚖️ Comparación y validación", help="SymPy vs SciPy y cálculo de errores")
with col6:
    st.page_link("pages/campo_direcciones.py", label="🧭 Campo de direcciones", help="Campo de pendientes y variación de parámetros")
with col7:
    st.page_link("pages/informes.py", label="📄 Informes", help="Exportar resultados e informes")

st.divider()

st.markdown("### 📌 Parámetros de referencia del proyecto")

st.markdown(
    """
    | Circuito | Parámetros | Resultado clave |
    |----------|------------|-----------------|
    | **RC (descarga experimental)** | V₀ ≈ 9,2128 V, τ ≈ 0,4896 s, R² ≈ 0,9991 | V(t) = 9,2128·e^(−t/0,4896) |
    | **RL (ejercicio)** | R = 4 Ω, L = 2 H, E₀ = 12 V, i₀ = 0 A | i(t) = 3(1 − e^(−2t)) |
    """
)

st.info(
    "💡 **Tip:** el circuito RC es el *problema real* (datos medidos en el "
    "laboratorio) y el RL es el *ejercicio complementario* (parámetros "
    "nominales). No mezcles los datos experimentales del RC con los "
    "parámetros del RL."
)
