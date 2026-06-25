from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox, QVBoxLayout,
)
from ...models.components import GridConnection


class GridDialog(QDialog):
    def __init__(self, comp: GridConnection | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Conexão com a Rede")
        self._build_ui()
        if comp:
            self._populate(comp)

    def _build_ui(self) -> None:
        form = QFormLayout()

        self.le_id = QLineEdit("GRID1")
        self.le_name = QLineEdit("Rede Concessionária")
        self.sb_un = QDoubleSpinBox(); self.sb_un.setRange(0.1, 500); self.sb_un.setSuffix(" kV"); self.sb_un.setValue(13.8)
        self.sb_sk = QDoubleSpinBox(); self.sb_sk.setRange(0, 99999); self.sb_sk.setSuffix(" MVA"); self.sb_sk.setValue(500)
        self.sb_rx = QDoubleSpinBox(); self.sb_rx.setRange(0, 10); self.sb_rx.setDecimals(3); self.sb_rx.setValue(0.1)

        self.cb_cmax = QComboBox()
        self.cb_cmax.addItems(["1.10 (MT/AT)", "1.05 (BT)"])

        form.addRow("ID:", self.le_id)
        form.addRow("Nome:", self.le_name)
        form.addRow("Tensão nominal Un:", self.sb_un)
        form.addRow("Potência de CC Sk'':", self.sb_sk)
        form.addRow("Razão R/X:", self.sb_rx)
        form.addRow("Fator cmax:", self.cb_cmax)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _populate(self, c: GridConnection) -> None:
        self.le_id.setText(c.id)
        self.le_name.setText(c.name)
        self.sb_un.setValue(c.un_kv)
        self.sb_sk.setValue(c.sk_mva)
        self.sb_rx.setValue(c.rx_ratio)

    def get_component(self) -> GridConnection:
        cmax = 1.10 if "1.10" in self.cb_cmax.currentText() else 1.05
        cmin = 1.00 if cmax == 1.10 else 0.95
        return GridConnection(
            id=self.le_id.text(),
            name=self.le_name.text(),
            un_kv=self.sb_un.value(),
            sk_mva=self.sb_sk.value(),
            rx_ratio=self.sb_rx.value(),
            cmax=cmax,
            cmin=cmin,
        )
