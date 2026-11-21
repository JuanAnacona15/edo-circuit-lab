"""
app.py — Punto de entrada de EDO Circuit Lab
=============================================

Arranca la aplicación Streamlit y define la navegación lateral. La interfaz
se separa de la lógica: cada página de pages/ solo orquesta la interacción y
llama a las funciones matemáticas de core/ y a las gráficas de utils/.

Ejecutar con:

    streamlit run app.py
"""

import streamlit as st

# Configuración global (tema, layout). Debe llamarse ANTES de cualquier otro
# comando de Streamlit y solo aquí, en el punto de entrada.
st.set_page_config(
    page_title="EDO Circuit Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Navegación: un st.Page por cada módulo del proyecto. El orden de la lista
# define el orden del menú lateral.
navegacion = st.navigation(
    [
        st.Page("pages/inicio.py", title="Inicio", icon="🏠", default=True),
        st.Page("pages/circuito_rc.py", title="Simulador RC", icon="🔋"),
        st.Page("pages/circuito_rl.py", title="Simulador RL", icon="🧲"),
        st.Page("pages/ecuaciones_exactas.py", title="Ecuaciones exactas", icon="🧮"),
        st.Page("pages/datos_experimentales.py", title="Datos experimentales", icon="📊"),
        st.Page("pages/comparacion.py", title="Comparación y validación", icon="⚖️"),
        st.Page("pages/campo_direcciones.py", title="Campo de direcciones", icon="🧭"),
        st.Page("pages/informes.py", title="Informes", icon="📄"),
    ]
)

navegacion.run()
