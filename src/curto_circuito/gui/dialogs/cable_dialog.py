from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QDoubleSpinBox, QVBoxLayout,
)
from ...models.components import Cable


class CableDialog(QDialog):
    def __init__(self, comp: Cable | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cabo")
        self._build_ui()
        if comp:
            self._populate(comp)

    def _build_ui(self) -> None:
        form = QFormLayout()

        self.le_id = QLineEdit("C1")
        self.le_name = QLineEdit("Cabo 1")
        self.sb_un = QDoubleSpinBox(); self.sb_un.setRange(0.1, 500); self.sb_un.setSuffix(" kV"); self.sb_un.setValue(0.4)
        self.sb_r1 = QDoubleSpinBox(); self.sb_r1.setRange(0, 9999); self.sb_r1.setSuffix(" Ω/km"); self.sb_r1.setDecimals(4); self.sb_r1.setValue(0.206)
        self.sb_x1 = QDoubleSpinBox(); self.sb_x1.setRange(0, 9999); self.sb_x1.setSuffix(" Ω/km"); self.sb_x1.setDecimals(4); self.sb_x1.setValue(0.08)
        self.sb_r0 = QDoubleSpinBox(); self.sb_r0.setRange(0, 9999); self.sb_r0.setSuffix(" Ω/km"); self.sb_r0.setDecimals(4); self.sb_r0.setValue(0.618)
        self.sb_x0 = QDoubleSpinBox(); self.sb_x0.setRange(0, 9999); self.sb_x0.setSuffix(" Ω/km"); self.sb_x0.setDecimals(4); self.sb_x0.setValue(0.24)
        self.sb_len = QDoubleSpinBox(); self.sb_len.setRange(1, 1e6); self.sb_len.setSuffix(" m"); self.sb_len.setValue(100)

        form.addRow("ID:", self.le_id)
        form.addRow("Nome:", self.le_name)
        form.addRow("Tensão nominal Un:", self.sb_un)
        form.addRow("R1 (seq. positiva):", self.sb_r1)
        form.addRow("X1 (seq. positiva):", self.sb_x1)
        form.addRow("R0 (seq. zero):", self.sb_r0)
        form.addRow("X0 (seq. zero):", self.sb_x0)
        form.addRow("Comprimento:", self.sb_len)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _populate(self, c: Cable) -> None:
        self.le_id.setText(c.id)
        self.le_name.setText(c.name)
        self.sb_un.setValue(c.un_kv)
        self.sb_r1.setValue(c.r1_ohm_km)
        self.sb_x1.setValue(c.x1_ohm_km)
        self.sb_r0.setValue(c.r0_ohm_km)
        self.sb_x0.setValue(c.x0_ohm_km)
        self.sb_len.setValue(c.length_m)

    def get_component(self) -> Cable:
        return Cable(
            id=self.le_id.text(),
            name=self.le_name.text(),
            un_kv=self.sb_un.value(),
            r1_ohm_km=self.sb_r1.value(),
            x1_ohm_km=self.sb_x1.value(),
            r0_ohm_km=self.sb_r0.value(),
            x0_ohm_km=self.sb_x0.value(),
            length_m=self.sb_len.value(),
        )
