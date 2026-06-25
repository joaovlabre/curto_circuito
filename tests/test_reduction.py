"""Testes da redução de Thevenin."""

import pytest
from curto_circuito.models.components import GridConnection, Transformer, Cable
from curto_circuito.models.network import Network, NetworkNode, Branch
from curto_circuito.engine.reduction import build_z1_thevenin
from curto_circuito.engine.impedance import grid_z1, transformer_z1, cable_z1
from curto_circuito.engine.correction import kt_factor
from curto_circuito.utils.units import refer_impedance


def test_z1_series_sum(simple_network):
    """Z_th na barra de carga = Z_grid + ZT*KT + Z_cabo (todos referidos a 0,4 kV)."""
    net = simple_network
    path = net.path_to("BUS_LOAD")

    z1_th = build_z1_thevenin(path, fault_un_kv=0.4, cmax=1.1)

    # cálculo manual
    grid = net.nodes["GRID1"].component
    trafo = net.branches[0].component
    cabo = net.branches[1].component

    z_grid = refer_impedance(grid_z1(grid), grid.un_kv, 0.4)
    kt = kt_factor(trafo, 1.1)
    z_trafo = refer_impedance(transformer_z1(trafo) * kt, trafo.un2_kv, 0.4)
    z_cabo = refer_impedance(cable_z1(cabo), cabo.un_kv, 0.4)
    z_expected = z_grid + z_trafo + z_cabo

    assert z1_th.real == pytest.approx(z_expected.real, rel=1e-4)
    assert z1_th.imag == pytest.approx(z_expected.imag, rel=1e-4)


def test_z1_at_root(simple_network):
    """Z_th na barra da fonte = só Z_grid."""
    net = simple_network
    path = net.path_to("GRID1")
    z1_th = build_z1_thevenin(path, fault_un_kv=13.8, cmax=1.1)
    grid = net.nodes["GRID1"].component
    z_expected = grid_z1(grid)   # já em 13,8 kV
    assert abs(z1_th) == pytest.approx(abs(z_expected), rel=1e-4)
