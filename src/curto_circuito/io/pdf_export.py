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

_MT_THRESHOLD_KV = 1.0
_MT_COLOR = colors.HexColor("#D6E4F0")
_BT_COLOR = colors.HexColor("#D5F5E3")


def _fmt(val) -> str:
    if val is None:
        return "-"
    if val == float("inf"):
        return "∞"
    return f"{val:.3f}"


def export(results: StudyResults, path: str | Path) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Cabeçalho
    story.append(Paragraph("Relatório de Curto-Circuito MT/BT", styles["Title"]))
    story.append(Paragraph("Norma: IEC 60909:2016", styles["Normal"]))
    story.append(Paragraph(f"Rede: {results.network_name}", styles["Normal"]))
    story.append(Paragraph(f"Data: {results.timestamp}", styles["Normal"]))
    story.append(Paragraph(f"Fator c utilizado: {results.voltage_factor_c}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    # Tabela de resultados
    header = [
        "Nível", "Barra", "Un\n(kV)",
        "Icc_3φ''\n(kA)", "Icc_pico\n(kA)", "Icc_3φ-g''\n(kA)",
        "Icc_2φ''\n(kA)", "Icc_1φ''\n(kA)", "Icc_2φ-g''\n(kA)", "κ",
    ]

    buses_mt = [b for b in results.buses if b.un_kv > _MT_THRESHOLD_KV]
    buses_bt = [b for b in results.buses if b.un_kv <= _MT_THRESHOLD_KV]
    rows = [header]
    row_colors = []

    for br in buses_mt + buses_bt:
        is_mt = br.un_kv > _MT_THRESHOLD_KV
        row_colors.append(_MT_COLOR if is_mt else _BT_COLOR)
        f3  = br.get_fault("3F")
        f3t = br.get_fault("3F-T")
        f2  = br.get_fault("2F")
        f1  = br.get_fault("1F-T")
        f2e = br.get_fault("2F-T")
        rows.append([
            "MT" if is_mt else "BT",
            br.node_name,
            f"{br.un_kv:.3f}",
            _fmt(f3.ik_pp_ka   if f3  else None),
            _fmt(f3.ip_ka      if f3  else None),
            _fmt(f3t.ik_pp_ka  if f3t else None),
            _fmt(f2.ik_pp_ka   if f2  else None),
            _fmt(f1.ik_pp_ka   if f1  else None),
            _fmt(f2e.ik_pp_ka  if f2e else None),
            _fmt(f3.kappa      if f3  else None),
        ])

    col_widths = [1.2*cm, 3*cm, 1.3*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.7*cm, 1.2*cm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F497D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, bg in enumerate(row_colors, start=1):
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    tbl.setStyle(TableStyle(style_cmds))
    story.append(tbl)
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph(
        "Cálculos realizados conforme IEC 60909:2016 — Curto-circuitos em sistemas de corrente alternada.",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=7, textColor=colors.grey),
    ))

    doc.build(story)
