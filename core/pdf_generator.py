from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO


def generar_pdf_contribuciones(salario, contribuciones):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------
    # Título
    # -------------------------

    elements.append(Paragraph(
        "<b>Recibo mensual de contribuciones a la seguridad social</b>",
        styles["Title"]
    ))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"<b>Salario Base de Cotización (SBC):</b> ${salario:,.2f}",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 12))

    # -------------------------
    # Tablas por grupo
    # -------------------------

    for grupo, conceptos in contribuciones.items():
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"<b>{grupo.capitalize()}</b>",
            styles["Heading2"]
        ))

        table_data = [["Concepto", "Monto mensual ($)"]]

        total = 0
        for concepto, info in conceptos.items():
            monto = info["monto"]
            table_data.append([concepto, f"${monto:,.2f}"])
            total += monto

        table_data.append(["TOTAL", f"${total:,.2f}"])

        table = Table(table_data, colWidths=[300, 150])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]))

        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer