from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union
from .components import GridConnection, Transformer, Cable, Busbar

ComponentType = Union[GridConnection, Transformer, Cable, Busbar]


@dataclass
class NetworkNode:
    """Nó da rede (barra ou elemento com terminal único)."""
    id: str
    name: str
    un_kv: float
    component: ComponentType | None = None


@dataclass
class Branch:
    """Ramo que conecta dois nós (transformador ou cabo)."""
    id: str
    from_node_id: str
    to_node_id: str
    component: Transformer | Cable


@dataclass
class Network:
    """Grafo radial da rede elétrica."""
    name: str
    nodes: dict[str, NetworkNode] = field(default_factory=dict)
    branches: list[Branch] = field(default_factory=list)
    root_node_id: str = ""   # nó da fonte (GridConnection)

    # ------------------------------------------------------------------ #
    # Helpers de construção                                                 #
    # ------------------------------------------------------------------ #

    def add_node(self, node: NetworkNode) -> None:
        self.nodes[node.id] = node

    def add_branch(self, branch: Branch) -> None:
        if branch.from_node_id not in self.nodes:
            raise KeyError(f"Nó origem '{branch.from_node_id}' não existe na rede")
        if branch.to_node_id not in self.nodes:
            raise KeyError(f"Nó destino '{branch.to_node_id}' não existe na rede")
        self.branches.append(branch)

    # ------------------------------------------------------------------ #
    # Navegação                                                             #
    # ------------------------------------------------------------------ #

    def children_of(self, node_id: str) -> list[tuple[Branch, NetworkNode]]:
        """Retorna (branch, nó_filho) para todos os filhos diretos de node_id."""
        result = []
        for br in self.branches:
            if br.from_node_id == node_id:
                result.append((br, self.nodes[br.to_node_id]))
        return result

    def path_to(self, target_id: str) -> list[tuple[Branch | None, NetworkNode]]:
        """BFS da raiz até target_id; retorna lista ordenada (branch, nó).
        O primeiro elemento tem branch=None (é a raiz)."""
        if not self.root_node_id:
            raise ValueError("root_node_id não definido")
        from collections import deque
        visited: dict[str, tuple[Branch | None, NetworkNode]] = {}
        parent: dict[str, str | None] = {self.root_node_id: None}
        edge_to: dict[str, Branch | None] = {self.root_node_id: None}
        queue: deque[str] = deque([self.root_node_id])
        while queue:
            nid = queue.popleft()
            for br, child in self.children_of(nid):
                if child.id not in parent:
                    parent[child.id] = nid
                    edge_to[child.id] = br
                    queue.append(child.id)
            if nid == target_id:
                break
        if target_id not in parent:
            raise ValueError(f"Nó '{target_id}' não alcançável a partir da raiz")
        # reconstrói caminho da raiz até target
        path = []
        cur = target_id
        while cur is not None:
            path.append((edge_to[cur], self.nodes[cur]))
            cur = parent[cur]
        path.reverse()
        return path

    def all_node_ids_bfs(self) -> list[str]:
        """Todos os nós em ordem BFS a partir da raiz."""
        from collections import deque
        visited: list[str] = []
        queue: deque[str] = deque([self.root_node_id])
        seen: set[str] = {self.root_node_id}
        while queue:
            nid = queue.popleft()
            visited.append(nid)
            for br, child in self.children_of(nid):
                if child.id not in seen:
                    seen.add(child.id)
                    queue.append(child.id)
        return visited
