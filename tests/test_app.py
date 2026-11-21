"""
tests/test_app.py — Verificación de que cada página de Streamlit renderiza
sin excepciones y de que los flujos accionados por botones funcionan.

Usa AppTest (framework de test de Streamlit, sin navegador).

Ejecutar:  python tests/test_app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

# (ruta, pulsar_botón) — las páginas con análisis accionado por botón se
# marcan con True para simular también el clic.
PAGINAS = [
    ("pages/inicio.py", False),
    ("pages/circuito_rc.py", False),
    ("pages/circuito_rl.py", False),
    ("pages/ecuaciones_exactas.py", True),
    ("pages/datos_experimentales.py", False),
    ("pages/comparacion.py", True),
    ("pages/campo_direcciones.py", False),
    ("pages/informes.py", False),
]

fallos = 0


def reportar(nombre, at):
    """Imprime ✓/✗ para una página y devuelve True si hubo error."""
    global fallos
    if at.exception:
        print(f"✗ {nombre}: {at.exception[0].message}")
        fallos += 1
        return True
    print(f"✓ {nombre}")
    return False


# 1. Página principal (app.py con st.navigation).
at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
at.run()
reportar("app.py (Inicio)", at)

# 2. Cada página del menú.
for pagina, pulsar in PAGINAS:
    at.switch_page(str(ROOT / pagina))
    at.run()
    if reportar(pagina, at):
        continue

    # Si la página tiene un botón principal, simulamos el clic para ejercitar
    # el cálculo real (análisis de exactitud / comparación numérica).
    if pulsar and len(at.button) > 0:
        try:
            at.button[0].click().run()
            if at.exception:
                print(f"✗ {pagina} [botón]: {at.exception[0].message}")
                fallos += 1
            else:
                print(f"✓ {pagina} [botón]")
        except Exception as exc:
            print(f"✗ {pagina} [botón]: {exc}")
            fallos += 1

print()
if fallos:
    print(f"❌ {fallos} error(es).")
    sys.exit(1)
print("✅ Todas las páginas renderizan y sus botones funcionan sin excepciones.")
