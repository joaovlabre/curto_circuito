"""Salvar e carregar projetos em JSON."""

from __future__ import annotations
import json
from pathlib import Path
from ..models.components import GridConnection, Transformer, Cable, Busbar
from ..models.network import Network, NetworkNode, Branch


def _comp_to_dict(comp) -> dict | None:
    if comp is None:
        return None
    d = comp.__dict__.copy()
    d["_type"] = type(comp).__name__
    return d


def _dict_to_comp(d: dict):
    if d is None:
        return None
    t = d.pop("_type")
    classes = {
        "GridConnection": GridConnection,
        "Transformer": Transformer,
        "Cable": Cable,
        "Busbar": Busbar,
    }
    return classes[t](**d)


def save(network: Network, path: str | Path) -> None:
    data = {
        "name": network.name,
        "root_node_id": network.root_node_id,
        "nodes": [
            {
                "id": n.id,
                "name": n.name,
                "un_kv": n.un_kv,
                "component": _comp_to_dict(n.component),
            }
            for n in network.nodes.values()
        ],
        "branches": [
            {
                "id": b.id,
                "from_node_id": b.from_node_id,
                "to_node_id": b.to_node_id,
                "component": _comp_to_dict(b.component),
            }
            for b in network.branches
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load(path: str | Path) -> Network:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    net = Network(name=data["name"], root_node_id=data["root_node_id"])
    for nd in data["nodes"]:
        comp_d = nd.get("component")
        comp = _dict_to_comp(comp_d) if comp_d else None
        net.nodes[nd["id"]] = NetworkNode(
            id=nd["id"], name=nd["name"], un_kv=nd["un_kv"], component=comp
        )
    for bd in data["branches"]:
        comp = _dict_to_comp(bd["component"])
        net.branches.append(Branch(
            id=bd["id"],
            from_node_id=bd["from_node_id"],
            to_node_id=bd["to_node_id"],
            component=comp,
        ))
    return net
