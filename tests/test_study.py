"""Teste de integração: estudo completo na rede simples."""

import pytest
from curto_circuito.engine.study import run_study


def test_study_returns_all_buses(simple_network):
    results = run_study(simple_network)
    node_ids = {br.node_id for br in results.buses}
    assert "GRID1" in node_ids
    assert "BUS_BT" in node_ids
    assert "BUS_LOAD" in node_ids


def test_study_all_fault_types(simple_network):
    results = run_study(simple_network)
    for bus_result in results.buses:
        types = {f.fault_type for f in bus_result.faults}
        assert {"3F", "2F", "1F-T", "2F-T"} == types


def test_study_ik3_decreases_downstream_same_voltage(simple_network):
    """Ik3'' decresce para barras mais afastadas da fonte no mesmo nível de tensão.
    BUS_BT (secundário do trafo) deve ter Ik'' maior que BUS_LOAD (BUS_BT + cabo).
    """
    results = run_study(simple_network)
    bus_bt = next(b for b in results.buses if b.node_id == "BUS_BT")
    bus_load = next(b for b in results.buses if b.node_id == "BUS_LOAD")
    ik_bt = bus_bt.get_fault("3F").ik_pp_ka
    ik_load = bus_load.get_fault("3F").ik_pp_ka
    assert ik_bt > ik_load


def test_study_ik2_less_than_ik3(simple_network):
    """Ik2'' < Ik3'' para todas as barras (relação √3/2)."""
    results = run_study(simple_network)
    import math
    for bus_result in results.buses:
        ik3 = bus_result.get_fault("3F").ik_pp_ka
        ik2 = bus_result.get_fault("2F").ik_pp_ka
        assert ik2 == pytest.approx(ik3 * math.sqrt(3) / 2, rel=1e-4)


def test_study_no_root_raises():
    from curto_circuito.models.network import Network
    net = Network(name="Vazia")
    with pytest.raises(ValueError, match="root_node_id"):
        run_study(net)
