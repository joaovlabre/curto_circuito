from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QDoubleSpinBox, QVBoxLayout,
)
from ...models.components import Busbar


class BusbarDialog(QDialog):
    def __init__(self, comp: Busbar | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Barra")
        self._build_ui()
        if comp:
            self._populate(comp)

    def _build_ui(self) -> None:
        form = QFormLayout()

        self.le_id = QLineEdit("BUS1")
        self.le_name = QLineEdit("Barra 1")
        self.sb_un = QDoubleSpinBox(); self.sb_un.setRange(0.1, 500); self.sb_un.setSuffix(" kV"); self.sb_un.setValue(0.4)
        self.le_desc = QLineEdit()

        form.addRow("ID:", self.le_id)
        form.addRow("Nome:", self.le_name)
        form.addRow("Tensão nominal Un:", self.sb_un)
        form.addRow("Descrição:", self.le_desc)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _populate(self, c: Busbar) -> None:
        self.le_id.setText(c.id)
        self.le_name.setText(c.name)
        self.sb_un.setValue(c.un_kv)
        self.le_desc.setText(c.description)

    def get_component(self) -> Busbar:
        return Busbar(
            id=self.le_id.text(),
            name=self.le_name.text(),
            un_kv=self.sb_un.value(),
            description=self.le_desc.text(),
        )
