"""Painel esquerdo: árvore da rede elétrica."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QToolBar, QMenu, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QIcon
from ..models.network import Network, NetworkNode, Branch
from ..models.components import GridConnection, Transformer, Cable, Busbar
from .dialogs.grid_dialog import GridDialog
from .dialogs.transformer_dialog import TransformerDialog
from .dialogs.cable_dialog import CableDialog
from .dialogs.busbar_dialog import BusbarDialog
import uuid


def _new_id() -> str:
    return str(uuid.uuid4())[:8]


class NetworkPanel(QWidget):
    network_changed = pyqtSignal()

    def __init__(self, network: Network, parent=None) -> None:
        super().__init__(parent)
        self.network = network
        self._build_ui()
        self.refresh_tree()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QToolBar()
        act_add_grid = QAction("+ Rede", self)
        act_add_trafo = QAction("+ Trafo", self)
        act_add_cable = QAction("+ Cabo", self)
        act_add_bus = QAction("+ Barra", self)
        act_remove = QAction("Remover", self)

        act_add_grid.triggered.connect(self._add_grid)
        act_add_trafo.triggered.connect(self._add_transformer)
        act_add_cable.triggered.connect(self._add_cable)
        act_add_bus.triggered.connect(self._add_busbar)
        act_remove.triggered.connect(self._remove_selected)

        for act in [act_add_grid, act_add_trafo, act_add_cable, act_add_bus, act_remove]:
            toolbar.addAction(act)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Rede Elétrica")
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._context_menu)

        layout.addWidget(toolbar)
        layout.addWidget(self.tree)

    # ------------------------------------------------------------------ #
    # Atualização da árvore                                               #
    # ------------------------------------------------------------------ #

    def refresh_tree(self) -> None:
        self.tree.clear()
        if not self.network.root_node_id:
            return
        root_node = self.network.nodes.get(self.network.root_node_id)
        if root_node is None:
            return
        root_item = QTreeWidgetItem([root_node.name])
        root_item.setData(0, Qt.ItemDataRole.UserRole, root_node.id)
        self.tree.addTopLevelItem(root_item)
        self._add_children(root_item, root_node.id)
        self.tree.expandAll()

    def _add_children(self, parent_item: QTreeWidgetItem, node_id: str) -> None:
        for branch, child_node in self.network.children_of(node_id):
            label = f"[{type(branch.component).__name__}] {branch.component.name} → {child_node.name}"
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.ItemDataRole.UserRole, child_node.id)
            parent_item.addChild(item)
            self._add_children(item, child_node.id)

    # ------------------------------------------------------------------ #
    # Ações de adição                                                      #
    # ------------------------------------------------------------------ #

    def _selected_node_id(self) -> str | None:
        items = self.tree.selectedItems()
        if not items:
            return None
        return items[0].data(0, Qt.ItemDataRole.UserRole)

    def _add_grid(self) -> None:
        if self.network.root_node_id:
            QMessageBox.warning(self, "Aviso", "Já existe uma conexão de rede. Remova-a antes de adicionar outra.")
            return
        dlg = GridDialog(parent=self)
        if dlg.exec():
            comp = dlg.get_component()
            node = NetworkNode(id=comp.id, name=comp.name, un_kv=comp.un_kv, component=comp)
            self.network.nodes[node.id] = node
            self.network.root_node_id = node.id
            self.refresh_tree()
            self.network_changed.emit()

    def _add_transformer(self) -> None:
        parent_id = self._selected_node_id()
        if not parent_id:
            QMessageBox.information(self, "Seleção", "Selecione o nó pai na árvore.")
            return
        dlg = TransformerDialog(parent=self)
        if dlg.exec():
            comp = dlg.get_component()
            # nó de chegada (secundário do trafo)
            child_node = NetworkNode(
                id=f"BUS_{comp.id}",
                name=f"Barra {comp.name} (BT)",
                un_kv=comp.un2_kv,
            )
            self.network.nodes[child_node.id] = child_node
            branch = Branch(
                id=f"BR_{comp.id}",
                from_node_id=parent_id,
                to_node_id=child_node.id,
                component=comp,
            )
            self.network.branches.append(branch)
            self.refresh_tree()
            self.network_changed.emit()

    def _add_cable(self) -> None:
        parent_id = self._selected_node_id()
        if not parent_id:
            QMessageBox.information(self, "Seleção", "Selecione o nó pai na árvore.")
            return
        dlg = CableDialog(parent=self)
        if dlg.exec():
            comp = dlg.get_component()
            child_node = NetworkNode(
                id=f"BUS_{comp.id}",
                name=f"Barra {comp.name} (carga)",
                un_kv=comp.un_kv,
            )
            self.network.nodes[child_node.id] = child_node
            branch = Branch(
                id=f"BR_{comp.id}",
                from_node_id=parent_id,
                to_node_id=child_node.id,
                component=comp,
            )
            self.network.branches.append(branch)
            self.refresh_tree()
            self.network_changed.emit()

    def _add_busbar(self) -> None:
        parent_id = self._selected_node_id()
        if not parent_id:
            QMessageBox.information(self, "Seleção", "Selecione o nó pai na árvore.")
            return
        dlg = BusbarDialog(parent=self)
        if dlg.exec():
            comp = dlg.get_component()
            # busbar sem branch — apenas nó adicional
            node = NetworkNode(id=comp.id, name=comp.name, un_kv=comp.un_kv, component=comp)
            self.network.nodes[node.id] = node
            # cria branch com cabo de impedância zero fictício para manter o grafo
            from ..models.components import Cable as _Cable
            dummy_cable = _Cable(
                id=f"DUMMY_{comp.id}", name="Conexão", un_kv=comp.un_kv,
                r1_ohm_km=0, x1_ohm_km=0, r0_ohm_km=0, x0_ohm_km=0, length_m=1,
            )
            branch = Branch(
                id=f"BR_{comp.id}",
                from_node_id=parent_id,
                to_node_id=node.id,
                component=dummy_cable,
            )
            self.network.branches.append(branch)
            self.refresh_tree()
            self.network_changed.emit()

    def _remove_selected(self) -> None:
        node_id = self._selected_node_id()
        if not node_id:
            return
        if node_id == self.network.root_node_id:
            # remove tudo
            self.network.nodes.clear()
            self.network.branches.clear()
            self.network.root_node_id = ""
        else:
            # remove nó e todos os filhos (BFS)
            from collections import deque
            to_remove = set()
            queue = deque([node_id])
            while queue:
                nid = queue.popleft()
                to_remove.add(nid)
                for br, child in self.network.children_of(nid):
                    queue.append(child.id)
            self.network.branches = [
                b for b in self.network.branches
                if b.from_node_id not in to_remove and b.to_node_id not in to_remove
            ]
            for nid in to_remove:
                self.network.nodes.pop(nid, None)
        self.refresh_tree()
        self.network_changed.emit()

    def _context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.addAction("+ Transformador", self._add_transformer)
        menu.addAction("+ Cabo", self._add_cable)
        menu.addAction("Remover", self._remove_selected)
        menu.exec(self.tree.viewport().mapToGlobal(pos))
