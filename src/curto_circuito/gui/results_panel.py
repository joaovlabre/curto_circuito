"""Painel inferior: tabela de resultados."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QTabWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..models.results import StudyResults
from ..utils.units import z_to_pu

_MT_THRESHOLD_KV = 1.0

_HEADERS_KA = [
    "Nível",
    "Barra",
    "Un (kV)",
    "Icc3φ (kA)",
    "Icc pico (kA)",
    "Icc3φ-g (kA)",
    "Icc2φ (kA)",
    "Icc1φ (kA)",
    "Icc2φ-g (kA)",
    "κ",
]

_HEADERS_ANG = [
    "Nível",
    "Barra",
    "Un (kV)",
    "|Z1| (p.u.)",
    "|Z0| (p.u.)",
    "θ3φ (°)",
    "θ2φ (°)",
    "θ1φ (°)",
    "θ2φ-g (°)",
    "Desl. (°)",
]


def _fmt(val: float | None, decimals: int = 3) -> str:
    if val is None:
        return "-"
    if val == float("inf"):
        return "∞"
    return f"{val:.{decimals}f}"


def _make_table(headers: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.setSortingEnabled(True)
    t.verticalHeader().setVisible(False)
    return t


class ResultsPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.label = QLabel("Resultados — execute o estudo para preencher")
        layout.addWidget(self.label)

        self._tabs = QTabWidget()
        self.table = _make_table(_HEADERS_KA)
        self.table_ang = _make_table(_HEADERS_ANG)
        self._tabs.addTab(self.table, "Correntes (kA)")
        self._tabs.addTab(self.table_ang, "Ângulos & p.u.")
        layout.addWidget(self._tabs)

    def show_results(self, results: StudyResults) -> None:
        self.label.setText(
            f"Resultados — {results.network_name} | c = {results.voltage_factor_c}"
            f" | Sbase = {results.s_base_mva:.1f} MVA | {results.timestamp}"
        )

        buses_mt = [b for b in results.buses if b.un_kv > _MT_THRESHOLD_KV]
        buses_bt = [b for b in results.buses if b.un_kv <= _MT_THRESHOLD_KV]
        ordered = buses_mt + buses_bt
        bold = QFont()
        bold.setBold(True)

        # ---- Aba 1: Correntes (kA) ----
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(ordered))
        for row, br in enumerate(ordered):
            is_mt = br.un_kv > _MT_THRESHOLD_KV
            f3  = br.get_fault("3F")
            f3t = br.get_fault("3F-T")
            f2  = br.get_fault("2F")
            f1  = br.get_fault("1F-T")
            f2e = br.get_fault("2F-T")

            values = [
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
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 0:
                    item.setFont(bold)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(1, min(self.table.columnWidth(1), 220))
        self.table.setSortingEnabled(True)

        # ---- Aba 2: Ângulos & p.u. ----
        self.table_ang.setSortingEnabled(False)
        self.table_ang.setRowCount(len(ordered))
        for row, br in enumerate(ordered):
            is_mt = br.un_kv > _MT_THRESHOLD_KV
            f3  = br.get_fault("3F")
            f2  = br.get_fault("2F")
            f1  = br.get_fault("1F-T")
            f2e = br.get_fault("2F-T")

            z1_pu = abs(z_to_pu(f3.z1_ohm, br.un_kv, results.s_base_mva)) if f3 else None
            z0_pu = abs(z_to_pu(f3.z0_ohm, br.un_kv, results.s_base_mva)) if f3 else None

            values = [
                "MT" if is_mt else "BT",
                br.node_name,
                f"{br.un_kv:.2f}",
                _fmt(z1_pu, 4),
                _fmt(z0_pu, 4),
                _fmt(f3.angle_deg  if f3  else None, 2),
                _fmt(f2.angle_deg  if f2  else None, 2),
                _fmt(f1.angle_deg  if f1  else None, 2),
                _fmt(f2e.angle_deg if f2e else None, 2),
                _fmt(br.phase_shift_deg, 1),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 0:
                    item.setFont(bold)
                self.table_ang.setItem(row, col, item)

        self.table_ang.resizeColumnsToContents()
        self.table_ang.setColumnWidth(1, min(self.table_ang.columnWidth(1), 220))
        self.table_ang.setSortingEnabled(True)

    def clear(self) -> None:
        self.table.setRowCount(0)
        self.table_ang.setRowCount(0)
        self.label.setText("Resultados — execute o estudo para preencher")
