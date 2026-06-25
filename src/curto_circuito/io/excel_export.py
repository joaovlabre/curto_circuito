"""Exportação de resultados para Excel (openpyxl)."""

from __future__ import annotations
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from ..models.network import Network
from ..models.results import StudyResults


_HEADER_FILL = PatternFill("solid", fgColor="1F497D")
_HEADER_FONT = Font(bold=True, color="FFFFFF")
_WARN_FILL = PatternFill("solid", fgColor="FFEB9C")


def _header_row(ws, values: list[str]) -> None:
    ws.append(values)
    for cell in ws[ws.max_row]:
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        cell.alignment = Alignment(horizontal="center")


def export(results: StudyResults, network: Network, path: str | Path) -> None:
    wb = Workbook()

    # ---- Aba Resultados ----
    ws_res = wb.active
    ws_res.title = "Resultados"
    _header_row(ws_res, [
        "Barra", "Un (kV)", "Ik3'' (kA)", "Ip 3F (kA)",
        "Ik2'' (kA)", "Ik1'' (kA)", "Ik2E'' (kA)", "κ",
    ])
    for br in results.buses:
        f3 = br.get_fault("3F")
        f2 = br.get_fault("2F")
        f1 = br.get_fault("1F-T")
        f2e = br.get_fault("2F-T")
        ws_res.append([
            br.node_name,
            round(br.un_kv, 3),
            round(f3.ik_pp_ka, 3) if f3 else "-",
            round(f3.ip_ka, 3) if f3 else "-",
            round(f2.ik_pp_ka, 3) if f2 else "-",
            round(f1.ik_pp_ka, 3) if f1 else "-",
            round(f2e.ik_pp_ka, 3) if f2e else "-",
            round(f3.kappa, 3) if f3 else "-",
        ])

    # ---- Aba Impedâncias ----
    ws_imp = wb.create_sheet("Impedâncias")
    _header_row(ws_imp, [
        "Barra", "Un (kV)", "R1 (mΩ)", "X1 (mΩ)", "|Z1| (mΩ)", "R0 (mΩ)", "X0 (mΩ)", "|Z0| (mΩ)",
    ])
    for br in results.buses:
        f3 = br.get_fault("3F")
        f1 = br.get_fault("1F-T")
        if f3:
            z1 = f3.z1_ohm * 1000
            z0 = (f1.z0_ohm if f1 else 0+0j) * 1000
            ws_imp.append([
                br.node_name, round(br.un_kv, 3),
                round(z1.real, 4), round(z1.imag, 4), round(abs(z1), 4),
                round(z0.real, 4), round(z0.imag, 4), round(abs(z0), 4),
            ])

    # ---- Aba Rede ----
    ws_net = wb.create_sheet("Rede")
    _header_row(ws_net, ["Tipo", "ID", "Nome", "Parâmetros"])
    for node in network.nodes.values():
        comp = node.component
        if comp is not None:
            ws_net.append([type(comp).__name__, comp.id, comp.name, str(comp.__dict__)])

    # Auto-width
    for ws in [ws_res, ws_imp, ws_net]:
        for col in ws.columns:
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 2, 40)

    wb.save(path)
