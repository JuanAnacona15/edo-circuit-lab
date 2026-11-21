"""
utils/export.py — Exportación de datos e informes
==================================================

Permite descargar los resultados en CSV (abierto en Excel/Google Sheets) y
generar un informe en Markdown con el procedimiento completo. La exportación
a PDF es OPCIONAL: solo se activa si la librería `reportlab` está instalada
(no forma parte de las dependencias obligatorias).
"""

from __future__ import annotations

import io

import pandas as pd


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes CSV listos para st.download_button.

    Usa codificación UTF-8 con BOM (utf-8-sig) para que Excel reconozca bien
    los acentos. El separador decimal es el punto (estándar CSV).
    """
    return df.to_csv(index=False).encode("utf-8-sig")


def df_to_csv_es_bytes(df: pd.DataFrame) -> bytes:
    """Igual que df_to_csv_bytes pero con coma decimal y punto y coma como
    separador (formato español habitual en Excel de Latinoamérica)."""
    return df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


def build_markdown_report(secciones: list[tuple[str, str]]) -> str:
    """Construye un informe en Markdown a partir de pares (título, contenido).

    `secciones` es una lista de tuplas (encabezado, cuerpo). El resultado se
    puede mostrar en la app y descargar como archivo .md.
    """
    lineas: list[str] = [
        "# EDO Circuit Lab — Informe de resultados",
        "",
        "Generado por EDO Circuit Lab (proyecto de aula de Ecuaciones Diferenciales).",
        "",
    ]
    for titulo, cuerpo in secciones:
        lineas.append(f"## {titulo}")
        lineas.append("")
        lineas.append(cuerpo.strip())
        lineas.append("")
    return "\n".join(lineas)


def text_to_pdf(texto: str) -> bytes | None:
    """Convierte texto plano a un PDF sencillo. Devuelve None si reportlab
    no está instalado (dependencia opcional)."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
    except ImportError:
        return None

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    ancho, alto = A4
    y = alto - 2 * cm

    for linea in texto.split("\n"):
        if y < 2 * cm:  # salto de página
            c.showPage()
            y = alto - 2 * cm
        c.setFont("Helvetica", 9)
        c.drawString(2 * cm, y, linea[:110])  # recorta líneas muy largas
        y -= 12
    c.save()
    return buf.getvalue()
