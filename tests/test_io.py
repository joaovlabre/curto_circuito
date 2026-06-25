"""Teste de round-trip: salvar e carregar projeto JSON."""

import tempfile
from pathlib import Path
from curto_circuito.io.project_file import save, load


def test_roundtrip_json(simple_network):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)

    try:
        save(simple_network, path)
        loaded = load(path)

        assert loaded.name == simple_network.name
        assert loaded.root_node_id == simple_network.root_node_id
        assert set(loaded.nodes.keys()) == set(simple_network.nodes.keys())
        assert len(loaded.branches) == len(simple_network.branches)

        # Verifica que o GridConnection foi preservado
        orig_comp = simple_network.nodes["GRID1"].component
        loaded_comp = loaded.nodes["GRID1"].component
        assert loaded_comp.un_kv == orig_comp.un_kv
        assert loaded_comp.z1_r_ohm == orig_comp.z1_r_ohm
        assert loaded_comp.z1_x_ohm == orig_comp.z1_x_ohm
        assert loaded_comp.z0_r_ohm == orig_comp.z0_r_ohm
        assert loaded_comp.z0_x_ohm == orig_comp.z0_x_ohm
    finally:
        path.unlink(missing_ok=True)
