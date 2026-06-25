"""Fixtures compartilhadas para os testes."""

import pytest
from curto_circuito.models.components import GridConnection, Transformer, Cable
from curto_circuito.models.network import Network, NetworkNode, Branch


@pytest.fixture
def simple_network():
    """
    Rede simples de referência para testes:
      Rede (13,8 kV, 500 MVA) → Trafo T1 (630 kVA, 13,8/0,4 kV) → Barra BT → Cabo C1 (100 m)
    """
    net = Network(name="Rede Teste")

    # Fonte
    # Z1 equivalente a Sk''=500 MVA, R/X=0.1 @ 13.8 kV: |Z|=380.9 mΩ, R=37.9 mΩ, X=379.0 mΩ
    grid = GridConnection(
        id="GRID1", name="Rede", un_kv=13.8,
        z1_r_mohm=37.9, z1_x_mohm=379.0,
        z0_r_mohm=37.9, z0_x_mohm=379.0,
    )
    n_grid = NetworkNode(id="GRID1", name="Barra MT", un_kv=13.8, component=grid)
    net.nodes["GRID1"] = n_grid
    net.root_node_id = "GRID1"

    # Trafo
    trafo = Transformer(
        id="T1", name="Trafo T1",
        sn_mva=0.63, un1_kv=13.8, un2_kv=0.4,
        z_pct=4.0, pk_kw=6.0,
        vector_group="Dyn11",
    )
    n_bt = NetworkNode(id="BUS_BT", name="Barra BT", un_kv=0.4)
    net.nodes["BUS_BT"] = n_bt
    net.branches.append(Branch(id="BR_T1", from_node_id="GRID1", to_node_id="BUS_BT", component=trafo))

    # Cabo
    cable = Cable(
        id="C1", name="Cabo C1", un_kv=0.4,
        r1_ohm_km=0.206, x1_ohm_km=0.08,
        r0_ohm_km=0.618, x0_ohm_km=0.24,
        length_m=100,
    )
    n_load = NetworkNode(id="BUS_LOAD", name="Barra Carga", un_kv=0.4)
    net.nodes["BUS_LOAD"] = n_load
    net.branches.append(Branch(id="BR_C1", from_node_id="BUS_BT", to_node_id="BUS_LOAD", component=cable))

    return net
