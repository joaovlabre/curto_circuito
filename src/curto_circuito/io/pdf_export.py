"""Exportação de resultados para PDF (reportlab)."""

from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
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
_HDR_COLOR = colors.HexColor("#1F497D")


def _fmt(val, decimals: int = 3) -> str:
    if val is None:
        return "-"
    if val == float("inf"):
        return "∞"
    return f"{val:.{decimals}f}"


def _build_style(row_colors) -> TableStyle:
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), _HDR_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, bg in enumerate(row_colors, start=1):
        cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    return TableStyle(cmds)


def export(results: StudyResults, path: str | Path) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=landscape(A4),
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Relatório de Curto-Circuito MT/BT", styles["Title"]))
    story.append(Paragraph("Norma: IEC 60909:2016", styles["Normal"]))
    story.append(Paragraph(f"Rede: {results.network_name}", styles["Normal"]))
    story.append(Paragraph(f"Data: {results.timestamp}", styles["Normal"]))
    story.append(Paragraph(
        f"Fator c: {results.voltage_factor_c}  |  Sbase: {results.s_base_mva:.1f} MVA",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.5*cm))

    # ---- Tabela de correntes ----
    buses_mt = [b for b in results.buses if b.un_kv > _MT_THRESHOLD_KV]
    buses_bt = [b for b in results.buses if b.un_kv <= _MT_THRESHOLD_KV]
    ordered = buses_mt + buses_bt

    header = [
        "Nível", "Barra", "Un\n(kV)",
        "Icc3φ\n(kA)", "Icc pico\n(kA)", "Icc3φ-g\n(kA)",
        "Icc2φ\n(kA)", "Icc1φ\n(kA)", "Icc2φ-g\n(kA)", "κ",
        "θ3φ\n(°)", "Desl.\n(°)",
    ]
    rows = [header]
    row_colors = []

    for br in ordered:
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
            f"{br.un_kv:.2f}",
            _fmt(f3.ik_pp_ka   if f3  else None),
            _fmt(f3.ip_ka      if f3  else None),
            _fmt(f3t.ik_pp_ka  if f3t else None),
            _fmt(f2.ik_pp_ka   if f2  else None),
            _fmt(f1.ik_pp_ka   if f1  else None),
            _fmt(f2e.ik_pp_ka  if f2e else None),
            _fmt(f3.kappa      if f3  else None),
            _fmt(f3.angle_deg  if f3  else None, 1),
            _fmt(br.phase_shift_deg, 1),
        ])

    col_widths = [1.1*cm, 3*cm, 1.2*cm, 1.6*cm, 1.6*cm, 1.6*cm,
                  1.6*cm, 1.6*cm, 1.6*cm, 1.1*cm, 1.3*cm, 1.3*cm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(_build_style(row_colors))
    story.append(tbl)
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph(
        "Cálculos realizados conforme IEC 60909:2016 — Curto-circuitos em sistemas de corrente alternada.",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=7, textColor=colors.grey),
    ))

    doc.build(story)
