"""Janela principal do aplicativo."""

from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QStatusBar, QToolBar, QMessageBox,
    QFileDialog, QCheckBox, QWidget, QVBoxLayout, QDoubleSpinBox, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from ..models.network import Network, Branch
from ..models.components import GridConnection, Transformer, Cable, Busbar
from ..models.results import StudyResults
from .network_panel import NetworkPanel
from .diagram_widget import DiagramWidget
from .results_panel import ResultsPanel
from .workers import StudyWorker
from .dialogs.grid_dialog import GridDialog
from .dialogs.transformer_dialog import TransformerDialog
from .dialogs.cable_dialog import CableDialog
from .dialogs.busbar_dialog import BusbarDialog
from ..io import project_file, excel_export, pdf_export


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Curto-Circuito MT/BT — IEC 60909")
        self.resize(1280, 800)

        self._network = Network(name="Novo Projeto")
        self._results: StudyResults | None = None
        self._worker: StudyWorker | None = None

        self._build_menu()
        self._build_toolbar()
        self._build_central()
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto.")

    # ------------------------------------------------------------------ #
    # Construção da UI                                                     #
    # ------------------------------------------------------------------ #

    def _build_menu(self) -> None:
        mb = self.menuBar()
        file_menu = mb.addMenu("Arquivo")
        file_menu.addAction("Novo", self._new_project)
        file_menu.addAction("Abrir...", self._open_project)
        file_menu.addAction("Salvar...", self._save_project)
        file_menu.addSeparator()
        file_menu.addAction("Sair", self.close)

        study_menu = mb.addMenu("Estudo")
        study_menu.addAction("Executar (Imáx)", lambda: self._run_study(use_cmax=True))
        study_menu.addAction("Executar (Imín)", lambda: self._run_study(use_cmax=False))

        export_menu = mb.addMenu("Exportar")
        export_menu.addAction("Excel...", self._export_excel)
        export_menu.addAction("PDF...", self._export_pdf)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Principal")
        tb.setMovable(False)
        self.addToolBar(tb)

        act_run = QAction("▶ Executar Estudo", self)
        act_run.triggered.connect(lambda: self._run_study(use_cmax=True))
        act_excel = QAction("Excel", self)
        act_excel.triggered.connect(self._export_excel)
        act_pdf = QAction("PDF", self)
        act_pdf.triggered.connect(self._export_pdf)

        self._sb_sbase = QDoubleSpinBox()
        self._sb_sbase.setRange(1.0, 99999.0)
        self._sb_sbase.setSuffix(" MVA")
        self._sb_sbase.setDecimals(1)
        self._sb_sbase.setValue(100.0)
        self._sb_sbase.setToolTip("Potência de base para conversão p.u.")

        tb.addAction(act_run)
        tb.addSeparator()
        tb.addWidget(QLabel("Sbase:"))
        tb.addWidget(self._sb_sbase)
        tb.addSeparator()
        tb.addAction(act_excel)
        tb.addAction(act_pdf)

    def _build_central(self) -> None:
        # Splitter vertical: topo (árvore | diagrama) | resultados
        v_split = QSplitter(Qt.Orientation.Vertical)

        # Splitter horizontal: árvore | diagrama
        h_split = QSplitter(Qt.Orientation.Horizontal)

        self._net_panel = NetworkPanel(self._network)
        self._net_panel.network_changed.connect(self._on_network_changed)
        self._net_panel.edit_requested.connect(self._edit_component)

        self._diagram = DiagramWidget()
        self._diagram.edit_requested.connect(self._edit_component)

        h_split.addWidget(self._net_panel)
        h_split.addWidget(self._diagram)
        h_split.setSizes([280, 700])

        self._results_panel = ResultsPanel()

        v_split.addWidget(h_split)
        v_split.addWidget(self._results_panel)
        v_split.setSizes([500, 250])

        self.setCentralWidget(v_split)

    # ------------------------------------------------------------------ #
    # Slots                                                                #
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    # Edição de componentes                                               #
    # ------------------------------------------------------------------ #

    def _find_incoming_branch(self, node_id: str) -> Branch | None:
        for branch in self._network.branches:
            if branch.to_node_id == node_id:
                return branch
        return None

    def _edit_component(self, node_id: str) -> None:
        node = self._network.nodes.get(node_id)
        if node is None:
            return

        branch = self._find_incoming_branch(node_id)

        # Determina o que editar e qual diálogo abrir
        if branch is None:
            # Nó raiz — edita o GridConnection
            comp = node.component
            if not isinstance(comp, GridConnection):
                return
            dlg = GridDialog(comp, parent=self)
            if dlg.exec():
                new_comp = dlg.get_component()
                node.component = new_comp
                node.name = new_comp.name
                node.un_kv = new_comp.un_kv
        elif isinstance(branch.component, Transformer):
            dlg = TransformerDialog(branch.component, parent=self)
            if dlg.exec():
                new_comp = dlg.get_component()
                branch.component = new_comp
                # atualiza o nó secundário com nova tensão/nome se mudou
                sec_node = self._network.nodes[branch.to_node_id]
                sec_node.un_kv = new_comp.un2_kv
                sec_node.name = f"Barra {new_comp.name} — {new_comp.un2_kv:.2f} kV (Sec.)"
        elif isinstance(branch.component, Cable):
            dlg = CableDialog(branch.component, parent=self)
            if dlg.exec():
                new_comp = dlg.get_component()
                branch.component = new_comp
                dest_node = self._network.nodes[branch.to_node_id]
                dest_node.un_kv = new_comp.un_kv
        else:
            # Busbar (cabo fictício de barra)
            comp = node.component
            if isinstance(comp, Busbar):
                dlg = BusbarDialog(comp, parent=self)
                if dlg.exec():
                    new_comp = dlg.get_component()
                    node.component = new_comp
                    node.name = new_comp.name
                    node.un_kv = new_comp.un_kv
            return

        self._net_panel.refresh_tree()
        self._diagram.render_network(self._network)
        self._results_panel.clear()
        self._results = None
        self.statusBar().showMessage(f"Componente '{node.name}' atualizado.")

    def _on_network_changed(self) -> None:
        self._diagram.render_network(self._network)
        self._results_panel.clear()
        self._results = None
        self.statusBar().showMessage("Rede alterada — execute o estudo para atualizar resultados.")

    def _run_study(self, use_cmax: bool = True) -> None:
        if not self._network.root_node_id:
            QMessageBox.warning(self, "Rede vazia", "Adicione uma conexão de rede antes de executar o estudo.")
            return
        self.statusBar().showMessage("Executando estudo...")
        self._worker = StudyWorker(self._network, use_cmax, s_base_mva=self._sb_sbase.value())
        self._worker.result_ready.connect(self._on_study_done)
        self._worker.error.connect(self._on_study_error)
        self._worker.start()

    def _on_study_done(self, results: StudyResults) -> None:
        self._results = results
        self._results_panel.show_results(results)
        self.statusBar().showMessage(
            f"Estudo concluído — {len(results.buses)} barras calculadas."
        )

    def _on_study_error(self, msg: str) -> None:
        QMessageBox.critical(self, "Erro no estudo", msg)
        self.statusBar().showMessage("Erro no estudo.")

    # ------------------------------------------------------------------ #
    # Arquivo                                                              #
    # ------------------------------------------------------------------ #

    def _new_project(self) -> None:
        self._network = Network(name="Novo Projeto")
        self._net_panel.network = self._network
        self._net_panel.refresh_tree()
        self._diagram.render_network(self._network)
        self._results_panel.clear()
        self._results = None

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Projeto", "", "JSON (*.json)")
        if path:
            try:
                self._network = project_file.load(path)
                self._net_panel.network = self._network
                self._net_panel.refresh_tree()
                self._diagram.render_network(self._network)
                self._results_panel.clear()
                self.statusBar().showMessage(f"Projeto aberto: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao abrir", str(e))

    def _save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Projeto", "", "JSON (*.json)")
        if path:
            try:
                project_file.save(self._network, path)
                self.statusBar().showMessage(f"Projeto salvo: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao salvar", str(e))

    # ------------------------------------------------------------------ #
    # Exportação                                                           #
    # ------------------------------------------------------------------ #

    def _export_excel(self) -> None:
        if not self._results:
            QMessageBox.information(self, "Sem resultados", "Execute o estudo antes de exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Excel", "", "Excel (*.xlsx)")
        if path:
            try:
                excel_export.export(self._results, self._network, path)
                self.statusBar().showMessage(f"Excel exportado: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao exportar Excel", str(e))

    def _export_pdf(self) -> None:
        if not self._results:
            QMessageBox.information(self, "Sem resultados", "Execute o estudo antes de exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", "", "PDF (*.pdf)")
        if path:
            try:
                pdf_export.export(self._results, path)
                self.statusBar().showMessage(f"PDF exportado: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao exportar PDF", str(e))
