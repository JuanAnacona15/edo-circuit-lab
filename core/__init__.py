"""core — Motor matemático y computacional de EDO Circuit Lab.

Esta carpeta contiene TODA la lógica de cálculo, separada de la interfaz
(Streamlit) y de las utilidades de visualización. Ningún archivo de aquí
depende de Streamlit: se pueden importar y probar por separado, por
ejemplo desde un script o desde tests/.

Módulos:
    rc_model          -> circuito RC (carga y descarga del capacitor)
    rl_model          -> circuito RL (respuesta de corriente en la bobina)
    exact_equations   -> ecuaciones exactas y factores integrantes
    symbolic_solver   -> resolución simbólica con SymPy
    numerical_solver  -> resolución numérica con SciPy (solve_ivp / RK45)
    regression        -> regresión lineal de ln(V) vs t (datos experimentales)
    validation        -> comparación de soluciones y cálculo de errores
"""
