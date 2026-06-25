from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QDoubleSpinBox, QComboBox, QVBoxLayout,
)
from ...models.components import Transformer


class TransformerDialog(QDialog):
    def __init__(self, comp: Transformer | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Transformador")
        self._build_ui()
        if comp:
            self._populate(comp)

    def _build_ui(self) -> None:
        form = QFormLayout()

        self.le_id = QLineEdit("T1")
        self.le_name = QLineEdit("Transformador 1")
        self.sb_sn = QDoubleSpinBox(); self.sb_sn.setRange(0.001, 9999); self.sb_sn.setSuffix(" MVA"); self.sb_sn.setDecimals(3); self.sb_sn.setValue(0.63)
        self.sb_un1 = QDoubleSpinBox(); self.sb_un1.setRange(0.1, 500); self.sb_un1.setSuffix(" kV"); self.sb_un1.setValue(13.8)
        self.sb_un2 = QDoubleSpinBox(); self.sb_un2.setRange(0.1, 500); self.sb_un2.setSuffix(" kV"); self.sb_un2.setValue(0.4)
        self.sb_uk = QDoubleSpinBox(); self.sb_uk.setRange(0.1, 20); self.sb_uk.setSuffix(" %"); self.sb_uk.setValue(4.0)
        self.sb_pk = QDoubleSpinBox(); self.sb_pk.setRange(0, 9999); self.sb_pk.setSuffix(" kW"); self.sb_pk.setValue(6.0)
        self.cb_vg = QComboBox()
        self.cb_vg.addItems(["Dyn11", "Dyn1", "YNyn0", "Yzn11", "Dd0"])
        self.cb_gnd = QComboBox()
        self.cb_gnd.addItems(["solid", "resistance", "isolated"])

        form.addRow("ID:", self.le_id)
        form.addRow("Nome:", self.le_name)
        form.addRow("Potência nominal Sn:", self.sb_sn)
        form.addRow("Tensão primário Un1:", self.sb_un1)
        form.addRow("Tensão secundário Un2:", self.sb_un2)
        form.addRow("Tensão CC uk%:", self.sb_uk)
        form.addRow("Perdas em carga Pk:", self.sb_pk)
        form.addRow("Grupo vetorial:", self.cb_vg)
        form.addRow("Aterramento neutro:", self.cb_gnd)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _populate(self, c: Transformer) -> None:
        self.le_id.setText(c.id)
        self.le_name.setText(c.name)
        self.sb_sn.setValue(c.sn_mva)
        self.sb_un1.setValue(c.un1_kv)
        self.sb_un2.setValue(c.un2_kv)
        self.sb_uk.setValue(c.uk_pct)
        self.sb_pk.setValue(c.pk_kw)
        idx = self.cb_vg.findText(c.vector_group)
        if idx >= 0:
            self.cb_vg.setCurrentIndex(idx)
        idx = self.cb_gnd.findText(c.grounding)
        if idx >= 0:
            self.cb_gnd.setCurrentIndex(idx)

    def get_component(self) -> Transformer:
        return Transformer(
            id=self.le_id.text(),
            name=self.le_name.text(),
            sn_mva=self.sb_sn.value(),
            un1_kv=self.sb_un1.value(),
            un2_kv=self.sb_un2.value(),
            uk_pct=self.sb_uk.value(),
            pk_kw=self.sb_pk.value(),
            vector_group=self.cb_vg.currentText(),
            grounding=self.cb_gnd.currentText(),
        )
