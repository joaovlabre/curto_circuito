"""
Orquestrador do estudo de curto-circuito (IEC 60909).
"""

from __future__ import annotations
import datetime
from ..models.network import Network
from ..models.results import BusResult, StudyResults
from ..models.components import GridConnection, Transformer
from ..utils.constants import get_c_factors, VECTOR_GROUP_PHASE_SHIFT
from ..utils.units import refer_impedance
from . import impedance as imp
from .reduction import build_z1_thevenin
from .sequence import build_z0_thevenin
from .fault_types import fault_3ph, fault_3ph_earth, fault_2ph, fault_1ph, fault_2ph_earth


def _cumulative_phase_shift(path) -> float:
    """Soma os deslocamentos de fase dos transformadores no caminho raiz → barra."""
    total = 0.0
    for branch, _node in path:
        if branch is not None and isinstance(branch.component, Transformer):
            total += VECTOR_GROUP_PHASE_SHIFT.get(branch.component.vector_group, 0.0)
    return total


def run_study(network: Network, use_cmax: bool = True, s_base_mva: float = 100.0) -> StudyResults:
    """
    Executa o estudo de curto-circuito para todas as barras da rede.

    use_cmax=True  → cmax (correntes máximas)
    use_cmax=False → cmin (correntes mínimas)
    s_base_mva     → base de potência para conversão p.u.
    """
    if not network.root_node_id:
        raise ValueError("A rede não possui raiz definida (root_node_id vazio)")

    root_node = network.nodes.get(network.root_node_id)
    if root_node is None:
        raise ValueError(f"Nó raiz '{network.root_node_id}' não encontrado")

    grid = root_node.component
    if not isinstance(grid, GridConnection):
        raise TypeError("O nó raiz deve ter um componente GridConnection")

    cmax, cmin = get_c_factors(grid.un_kv)
    c = cmax if use_cmax else cmin

    z0_grid = imp.grid_z0(grid)
    bus_results: list[BusResult] = []

    for node_id in network.all_node_ids_bfs():
        node = network.nodes[node_id]
        path = network.path_to(node_id)

        z1 = build_z1_thevenin(path, node.un_kv, cmax)
        z0 = build_z0_thevenin(path, node.un_kv, z0_grid)
        shift = _cumulative_phase_shift(path)

        faults = [
            fault_3ph(c, node.un_kv, z1),
            fault_3ph_earth(c, node.un_kv, z1, z0),
            fault_2ph(c, node.un_kv, z1),
            fault_1ph(c, node.un_kv, z1, z0),
            fault_2ph_earth(c, node.un_kv, z1, z0),
        ]

        bus_results.append(BusResult(
            node_id=node_id,
            node_name=node.name,
            un_kv=node.un_kv,
            faults=faults,
            phase_shift_deg=shift,
        ))

    return StudyResults(
        network_name=network.name,
        timestamp=datetime.datetime.now().isoformat(timespec="seconds"),
        voltage_factor_c=c,
        s_base_mva=s_base_mva,
        buses=bus_results,
    )
