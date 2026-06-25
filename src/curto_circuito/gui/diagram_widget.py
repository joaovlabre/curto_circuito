"""Diagrama unifilar simplificado (QGraphicsScene)."""

from __future__ import annotations
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from ..models.network import Network
from ..models.components import GridConnection, Transformer, Cable


_COLOR_GRID = QColor("#1F497D")
_COLOR_TRAFO = QColor("#F59B00")
_COLOR_CABLE = QColor("#00A651")
_COLOR_BUS = QColor("#444444")

_NODE_W = 120
_NODE_H = 36
_V_STEP = 80


class DiagramWidget(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(self.renderHints() | self.renderHints())
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def render_network(self, network: Network) -> None:
        self._scene.clear()
        if not network.root_node_id:
            return
        positions: dict[str, tuple[float, float]] = {}
        self._layout(network, network.root_node_id, 0, 0, positions)
        self._draw(network, positions)
        self.fitInView(self._scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _layout(self, network: Network, node_id: str, x: float, y: float, pos: dict, col_offset: list | None = None) -> float:
        """Layout em árvore top-down; retorna largura ocupada."""
        children = network.children_of(node_id)
        if not children:
            pos[node_id] = (x, y)
            return _NODE_W + 20
        total_w = 0.0
        cx = x
        for _, child in children:
            w = self._layout(network, child.id, cx, y + _NODE_H + _V_STEP, pos)
            total_w += w
            cx += w
        center_x = x + (total_w - _NODE_W) / 2
        pos[node_id] = (center_x, y)
        return max(total_w, _NODE_W + 20)

    def _draw(self, network: Network, pos: dict) -> None:
        pen_line = QPen(QColor("#888888"), 1.5)

        for node_id, (x, y) in pos.items():
            node = network.nodes[node_id]
            comp = node.component
            if isinstance(comp, GridConnection):
                color = _COLOR_GRID
            elif isinstance(comp, Transformer):
                color = _COLOR_TRAFO
            else:
                color = _COLOR_BUS

            rect = QRectF(x, y, _NODE_W, _NODE_H)
            self._scene.addRect(rect, QPen(color, 1.5), QBrush(color.lighter(170)))
            txt = QGraphicsTextItem(f"{node.name}\n{node.un_kv:.1f} kV")
            txt.setFont(QFont("Arial", 7))
            txt.setPos(x + 4, y + 2)
            self._scene.addItem(txt)

        for branch in network.branches:
            if branch.from_node_id not in pos or branch.to_node_id not in pos:
                continue
            x1, y1 = pos[branch.from_node_id]
            x2, y2 = pos[branch.to_node_id]
            mx1, my1 = x1 + _NODE_W / 2, y1 + _NODE_H
            mx2, my2 = x2 + _NODE_W / 2, y2
            self._scene.addLine(mx1, my1, mx2, my2, pen_line)
            # rótulo do ramo
            lx = (mx1 + mx2) / 2
            ly = (my1 + my2) / 2
            comp = branch.component
            color = _COLOR_TRAFO if isinstance(comp, Transformer) else _COLOR_CABLE
            lbl = QGraphicsTextItem(comp.name)
            lbl.setFont(QFont("Arial", 7))
            lbl.setDefaultTextColor(color)
            lbl.setPos(lx + 2, ly - 8)
            self._scene.addItem(lbl)
