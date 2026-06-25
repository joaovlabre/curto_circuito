"""Painel inferior: tabela de resultados."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..models.results import StudyResults

_MT_THRESHOLD_KV = 1.0

_HEADERS = [
    "Nível",
    "Barra",
    "Un (kV)",
    "Icc_3φ'' (kA)",
    "Icc_pico (kA)",
    "Icc_3φ-g'' (kA)",
    "Icc_2φ'' (kA)",
    "Icc_1φ'' (kA)",
    "Icc_2φ-g'' (kA)",
    "κ",
]


def _fmt(val: float | None) -> str:
    if val is None:
        return "-"
    if val == float("inf"):
        return "∞"
    return f"{val:.3f}"


class ResultsPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.label = QLabel("Resultados — execute o estudo para preencher")
        self.table = QTableWidget(0, len(_HEADERS))
        self.table.setHorizontalHeaderLabels(_HEADERS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.label)
        layout.addWidget(self.table)

    def show_results(self, results: StudyResults) -> None:
        self.label.setText(
            f"Resultados — {results.network_name} | c = {results.voltage_factor_c} | {results.timestamp}"
        )

        buses_mt = [b for b in results.buses if b.un_kv > _MT_THRESHOLD_KV]
        buses_bt = [b for b in results.buses if b.un_kv <= _MT_THRESHOLD_KV]
        ordered = buses_mt + buses_bt

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(ordered))
        bold = QFont()
        bold.setBold(True)

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
                f"{br.un_kv:.3f}",
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
        # limita a coluna Barra a no máximo 220 px
        self.table.setColumnWidth(1, min(self.table.columnWidth(1), 220))
        self.table.setSortingEnabled(True)

    def clear(self) -> None:
        self.table.setRowCount(0)
        self.label.setText("Resultados — execute o estudo para preencher")
