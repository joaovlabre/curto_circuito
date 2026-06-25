"""
Redução de Thevenin para rede radial (IEC 60909:2016 §4.3).

Para rede radial, Z_th é a soma em série de todas as impedâncias ao longo
do caminho raiz → barra de falta, referidas ao nível de tensão da falta.
"""

import cmath
from ..models.components import GridConnection, Transformer, Cable, Busbar
from ..models.network import Branch, NetworkNode
from ..utils.units import refer_impedance
from . import impedance as imp
from .correction import kt_factor


def build_z1_thevenin(
    path: list[tuple[Branch | None, NetworkNode]],
    fault_un_kv: float,
    cmax: float,
) -> complex:
    """
    Calcula Z1 de Thevenin na barra de falta.

    path: lista [(branch, node)] da raiz até a barra de falta
          (primeiro elemento tem branch=None → raiz / GridConnection).
    fault_un_kv: tensão nominal da barra de falta (kV).
    cmax: fator de tensão máximo (IEC 60909 Tabela 1).
    """
    z1 = complex(0, 0)

    for branch, node in path:
        if branch is None:
            # nó raiz: GridConnection
            comp = node.component
            if isinstance(comp, GridConnection):
                z0_grid = imp.grid_z1(comp)
                z1 += refer_impedance(z0_grid, comp.un_kv, fault_un_kv)
            # se comp for None (barra sem componente associado), nada a adicionar
            continue

        comp = branch.component

        if isinstance(comp, Transformer):
            kt = kt_factor(comp, cmax)
            zt = imp.transformer_z1(comp) * kt
            z1 += refer_impedance(zt, comp.un2_kv, fault_un_kv)

        elif isinstance(comp, Cable):
            z_cab = imp.cable_z1(comp)
            z1 += refer_impedance(z_cab, comp.un_kv, fault_un_kv)

    return z1
