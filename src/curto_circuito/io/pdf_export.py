"""Exportação de resultados para PDF (reportlab)."""

from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from ..models.results import StudyResults


def export(results: StudyResults, path: str | Path) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Cabeçalho
    story.append(Paragraph("Relatório de Curto-Circuito MT/BT", styles["Title"]))
    story.append(Paragraph(f"Norma: IEC 60909:2016", styles["Normal"]))
    story.append(Paragraph(f"Rede: {results.network_name}", styles["Normal"]))
    story.append(Paragraph(f"Data: {results.timestamp}", styles["Normal"]))
    story.append(Paragraph(f"Fator c utilizado: {results.voltage_factor_c}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    # Tabela de resultados
    header = ["Barra", "Un\n(kV)", "Ik3''\n(kA)", "Ip\n(kA)", "Ik2''\n(kA)", "Ik1''\n(kA)", "Ik2E''\n(kA)", "κ"]
    rows = [header]
    for br in results.buses:
        f3 = br.get_fault("3F")
        f2 = br.get_fault("2F")
        f1 = br.get_fault("1F-T")
        f2e = br.get_fault("2F-T")
        rows.append([
            br.node_name,
            f"{br.un_kv:.3f}",
            f"{f3.ik_pp_ka:.3f}" if f3 else "-",
            f"{f3.ip_ka:.3f}" if f3 else "-",
            f"{f2.ik_pp_ka:.3f}" if f2 else "-",
            f"{f1.ik_pp_ka:.3f}" if f1 else "-",
            f"{f2e.ik_pp_ka:.3f}" if f2e else "-",
            f"{f3.kappa:.3f}" if f3 else "-",
        ])

    col_widths = [3.5*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 1.5*cm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F497D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EBF0F8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 1*cm))

    # Rodapé informativo
    story.append(Paragraph(
        "Cálculos realizados conforme IEC 60909:2016 — Curto-circuitos em sistemas de corrente alternada.",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=7, textColor=colors.grey),
    ))

    doc.build(story)
