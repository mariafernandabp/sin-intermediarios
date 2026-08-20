from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from numero_a_letras import numero_a_letras

DATA_DIR = Path(__file__).parent / "data" / "cuentas_cobro"
DATA_DIR.mkdir(parents=True, exist_ok=True)

VERDE = HexColor("#166534")
GRIS = HexColor("#374151")
NEGRO = HexColor("#0D1B2A")


def _money(n):
    return "$ {:,.0f}".format(n).replace(",", ".")


def generar_cuenta_cobro(consecutivo, creador, concepto, monto, fecha):
    """Genera el PDF de cuenta de cobro y devuelve el nombre de archivo (relativo a DATA_DIR)."""
    filename = f"cuenta-cobro-{consecutivo:05d}.pdf"
    path = DATA_DIR / filename

    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    margin = 2.2 * cm
    y = height - 2.5 * cm

    c.setFillColor(NEGRO)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, y, "LA REAL")
    c.setFont("Helvetica", 9)
    c.setFillColor(GRIS)
    c.drawRightString(width - margin, y, "Cuenta de cobro generada automaticamente")

    y -= 0.9 * cm
    c.setStrokeColor(VERDE)
    c.setLineWidth(1.2)
    c.line(margin, y, width - margin, y)

    y -= 1.2 * cm
    c.setFillColor(NEGRO)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(margin, y, f"CUENTA DE COBRO No. {consecutivo:05d}")

    y -= 0.7 * cm
    c.setFont("Helvetica", 10.5)
    c.setFillColor(GRIS)
    c.drawString(margin, y, f"Fecha: {fecha}")

    y -= 1.0 * cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NEGRO)
    c.drawString(margin, y, "Debe a:")
    y -= 0.55 * cm
    c.setFont("Helvetica", 10.5)
    c.setFillColor(GRIS)
    c.drawString(margin, y, f"{creador['nombre_completo']}")
    y -= 0.5 * cm
    c.drawString(margin, y, f"{creador['tipo_documento']} No. {creador['numero_documento']}")

    y -= 1.0 * cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NEGRO)
    c.drawString(margin, y, "La suma de:")
    y -= 0.55 * cm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(VERDE)
    c.drawString(margin, y, _money(monto))

    y -= 0.6 * cm
    c.setFont("Helvetica-Oblique", 9.5)
    c.setFillColor(GRIS)
    texto_letras = numero_a_letras(monto)
    c.drawString(margin, y, f"({texto_letras})")

    y -= 1.0 * cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NEGRO)
    c.drawString(margin, y, "Por concepto de:")
    y -= 0.55 * cm
    c.setFont("Helvetica", 10.5)
    c.setFillColor(GRIS)

    text_obj = c.beginText(margin, y)
    text_obj.setFont("Helvetica", 10.5)
    max_chars = 95
    for i in range(0, len(concepto), max_chars):
        text_obj.textLine(concepto[i:i + max_chars])
    c.drawText(text_obj)
    y -= 0.6 * cm * (1 + len(concepto) // max_chars)

    y -= 0.8 * cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NEGRO)
    c.drawString(margin, y, "Datos para el pago (uso interno LA REAL):")
    y -= 0.55 * cm
    c.setFont("Helvetica", 10)
    c.setFillColor(GRIS)
    c.drawString(margin, y, f"Banco: {creador['banco']}   |   Tipo de cuenta: {creador['tipo_cuenta']}")
    y -= 0.5 * cm
    c.drawString(margin, y, f"Numero de cuenta: {creador['numero_cuenta']}")

    y -= 2.2 * cm
    c.setStrokeColor(GRIS)
    c.setLineWidth(0.6)
    c.line(margin, y, margin + 7 * cm, y)
    y -= 0.45 * cm
    c.setFont("Helvetica", 9.5)
    c.drawString(margin, y, "Firma del beneficiario")

    c.setFont("Helvetica", 7.5)
    c.setFillColor(GRIS)
    c.drawCentredString(width / 2, 1.4 * cm,
                         "Documento generado por la herramienta interna de LA REAL - Sin Intermediarios")

    c.showPage()
    c.save()
    return filename
