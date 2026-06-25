"""Testes das funções utilitárias de unidades."""

import pytest
from curto_circuito.utils.units import z_to_pu


def test_z_to_pu_known_value():
    """Z_base = (0.4e3)² / 100e6 = 1.6e-3 Ω → Z = 1.6e-3 → 1.0 p.u."""
    z_base = (0.4e3) ** 2 / 100e6   # = 1.6e-3 Ω
    z_ohm = complex(z_base, 0)
    result = z_to_pu(z_ohm, v_base_kv=0.4, s_base_mva=100.0)
    assert abs(result) == pytest.approx(1.0, rel=1e-6)


def test_z_to_pu_complex():
    """Conversão preserva argumento (ângulo) da impedância."""
    import cmath, math
    z_ohm = complex(1.0e-3, 2.0e-3)
    result = z_to_pu(z_ohm, v_base_kv=0.4, s_base_mva=100.0)
    assert cmath.phase(result) == pytest.approx(cmath.phase(z_ohm), abs=1e-9)


def test_z_to_pu_scaling():
    """Dobrando Sbase reduz Z_pu à metade."""
    z_ohm = complex(1.0e-3, 0)
    r1 = abs(z_to_pu(z_ohm, v_base_kv=0.4, s_base_mva=100.0))
    r2 = abs(z_to_pu(z_ohm, v_base_kv=0.4, s_base_mva=200.0))
    assert r2 == pytest.approx(r1 * 2, rel=1e-6)
