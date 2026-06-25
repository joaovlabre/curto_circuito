"""Painel inferior: tabela de resultados."""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ..models.results import StudyResults


_HEADERS = ["Barra", "Un (kV)", "Ik3'' (kA)", "Ip (kA)", "Ik2'' (kA)", "Ik1'' (kA)", "Ik2E'' (kA)", "κ"]


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
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.label)
        layout.addWidget(self.table)

    def show_results(self, results: StudyResults) -> None:
        self.label.setText(
            f"Resultados — {results.network_name} | c={results.voltage_factor_c} | {results.timestamp}"
        )
        self.table.setRowCount(len(results.buses))
        for row, br in enumerate(results.buses):
            f3 = br.get_fault("3F")
            f2 = br.get_fault("2F")
            f1 = br.get_fault("1F-T")
            f2e = br.get_fault("2F-T")
            values = [
                br.node_name,
                f"{br.un_kv:.3f}",
                f"{f3.ik_pp_ka:.3f}" if f3 else "-",
                f"{f3.ip_ka:.3f}" if f3 else "-",
                f"{f2.ik_pp_ka:.3f}" if f2 else "-",
                f"{f1.ik_pp_ka:.3f}" if f1 else "-",
                f"{f2e.ik_pp_ka:.3f}" if f2e else "-",
                f"{f3.kappa:.3f}" if f3 else "-",
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def clear(self) -> None:
        self.table.setRowCount(0)
        self.label.setText("Resultados — execute o estudo para preencher")
