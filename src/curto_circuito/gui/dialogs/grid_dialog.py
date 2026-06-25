from __future__ import annotations
import math
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QDoubleSpinBox,
    QComboBox, QVBoxLayout, QGroupBox, QLabel,
)
from PyQt6.QtGui import QFont
from ...models.components import GridConnection

_SQRT3 = math.sqrt(3)


def _sb(lo, hi, suffix, decimals=4, value=0.0) -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(lo, hi)
    s.setSuffix(suffix)
    s.setDecimals(decimals)
    s.setValue(value)
    return s


class GridDialog(QDialog):
    def __init__(self, comp: GridConnection | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Conexão com a Rede")
        self._build_ui()
        if comp:
            self._populate(comp)
        else:
            self._update_computed()

    def _build_ui(self) -> None:
        # ---- Identificação ----
        grp_id = QGroupBox("Identificação")
        f_id = QFormLayout(grp_id)
        self.le_id   = QLineEdit("GRID1")
        self.le_name = QLineEdit("Rede Concessionária")
        self.sb_un   = _sb(0.1, 500, " kV", 2, 13.8)
        self.cb_cmax = QComboBox()
        self.cb_cmax.addItems(["1.10 (MT/AT)", "1.05 (BT)"])
        f_id.addRow("ID:", self.le_id)
        f_id.addRow("Nome:", self.le_name)
        f_id.addRow("Tensão nominal Un:", self.sb_un)
        f_id.addRow("Fator cmax:", self.cb_cmax)

        # ---- Impedância Z1 (seq. positiva) ----
        grp_z1 = QGroupBox("Impedância de sequência positiva Z1")
        f_z1 = QFormLayout(grp_z1)
        self.sb_r1 = _sb(0, 9999, " Ω", 4, 0.0379)
        self.sb_x1 = _sb(0, 9999, " Ω", 4, 0.3790)
        f_z1.addRow("R1:", self.sb_r1)
        f_z1.addRow("X1:", self.sb_x1)

        # ---- Impedância Z0 (seq. zero) ----
        grp_z0 = QGroupBox("Impedância de sequência zero Z0")
        f_z0 = QFormLayout(grp_z0)
        self.sb_r0 = _sb(0, 9999, " Ω", 4, 0.0379)
        self.sb_x0 = _sb(0, 9999, " Ω", 4, 0.3790)
        f_z0.addRow("R0:", self.sb_r0)
        f_z0.addRow("X0:", self.sb_x0)

        # ---- Valores calculados (somente leitura) ----
        grp_calc = QGroupBox("Valores calculados (conferência)")
        f_calc = QFormLayout(grp_calc)
        italic = QFont(); italic.setItalic(True)
        self.lbl_sk  = QLabel("-"); self.lbl_sk.setFont(italic)
        self.lbl_icc = QLabel("-"); self.lbl_icc.setFont(italic)
        self.lbl_z1  = QLabel("-"); self.lbl_z1.setFont(italic)
        self.lbl_xr  = QLabel("-"); self.lbl_xr.setFont(italic)
        f_calc.addRow("Sk'' (MVA):", self.lbl_sk)
        f_calc.addRow("Icc3φ (kA):", self.lbl_icc)
        f_calc.addRow("|Z1| (Ω):", self.lbl_z1)
        f_calc.addRow("X1/R1:", self.lbl_xr)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(grp_id)
        layout.addWidget(grp_z1)
        layout.addWidget(grp_z0)
        layout.addWidget(grp_calc)
        layout.addWidget(buttons)
        self.setLayout(layout)

        for w in (self.sb_r1, self.sb_x1, self.sb_un):
            w.valueChanged.connect(self._update_computed)

    def _update_computed(self) -> None:
        r1 = self.sb_r1.value()
        x1 = self.sb_x1.value()
        un_kv = self.sb_un.value()
        z1_mag = math.sqrt(r1**2 + x1**2)
        un_v = un_kv * 1e3

        if z1_mag > 0:
            sk_mva = un_v**2 / z1_mag / 1e6
            icc_ka = (1.1 * un_kv) / (_SQRT3 * z1_mag)
            xr = x1 / r1 if r1 > 0 else float("inf")
            self.lbl_sk.setText(f"{sk_mva:.1f}")
            self.lbl_icc.setText(f"{icc_ka:.3f}")
            self.lbl_z1.setText(f"{z1_mag:.4f}")
            self.lbl_xr.setText(f"{xr:.2f}" if xr != float("inf") else "∞")
        else:
            for lbl in (self.lbl_sk, self.lbl_icc, self.lbl_z1, self.lbl_xr):
                lbl.setText("—")

    def _populate(self, c: GridConnection) -> None:
        self.le_id.setText(c.id)
        self.le_name.setText(c.name)
        self.sb_un.setValue(c.un_kv)
        self.sb_r1.setValue(c.z1_r_ohm)
        self.sb_x1.setValue(c.z1_x_ohm)
        self.sb_r0.setValue(c.z0_r_ohm)
        self.sb_x0.setValue(c.z0_x_ohm)
        if c.cmax >= 1.09:
            self.cb_cmax.setCurrentIndex(0)
        else:
            self.cb_cmax.setCurrentIndex(1)

    def get_component(self) -> GridConnection:
        cmax = 1.10 if "1.10" in self.cb_cmax.currentText() else 1.05
        cmin = 1.00 if cmax == 1.10 else 0.95
        return GridConnection(
            id=self.le_id.text(),
            name=self.le_name.text(),
            un_kv=self.sb_un.value(),
            z1_r_ohm=self.sb_r1.value(),
            z1_x_ohm=self.sb_x1.value(),
            z0_r_ohm=self.sb_r0.value(),
            z0_x_ohm=self.sb_x0.value(),
            cmax=cmax,
            cmin=cmin,
        )
