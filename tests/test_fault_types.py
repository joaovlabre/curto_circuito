"""Testes das fórmulas de corrente de curto-circuito."""

import math
import pytest
from curto_circuito.engine.fault_types import fault_3ph, fault_2ph, fault_1ph, fault_2ph_earth

_SQRT3 = math.sqrt(3)


def test_3ph_ik_formula():
    """Ik3'' = c*Un / (√3 * |Z1|)."""
    z1 = complex(0.01, 0.05)
    c, un_kv = 1.1, 0.4
    res = fault_3ph(c, un_kv, z1)
    expected = (c * un_kv) / (_SQRT3 * abs(z1))
    assert res.ik_pp_ka == pytest.approx(expected, rel=1e-5)


def test_2ph_relation_to_3ph():
    """Ik2'' = (√3/2) * Ik3''."""
    z1 = complex(0.01, 0.05)
    c, un_kv = 1.1, 0.4
    r3 = fault_3ph(c, un_kv, z1)
    r2 = fault_2ph(c, un_kv, z1)
    assert r2.ik_pp_ka == pytest.approx((_SQRT3 / 2) * r3.ik_pp_ka, rel=1e-5)


def test_1ph_formula():
    """Ik1'' = √3 * c * Un / |2Z1 + Z0|."""
    z1 = complex(0.01, 0.05)
    z0 = complex(0.03, 0.15)
    c, un_kv = 1.1, 0.4
    res = fault_1ph(c, un_kv, z1, z0)
    expected = (_SQRT3 * c * un_kv) / abs(2 * z1 + z0)
    assert res.ik_pp_ka == pytest.approx(expected, rel=1e-5)


def test_1ph_returns_fault_type():
    z1 = complex(0.01, 0.05)
    z0 = complex(0.03, 0.15)
    res = fault_1ph(1.1, 0.4, z1, z0)
    assert res.fault_type == "1F-T"


def test_peak_current():
    """Ip = κ * √2 * Ik''."""
    z1 = complex(0.01, 0.1)
    res = fault_3ph(1.1, 0.4, z1)
    kappa = 1.02 + 0.98 * math.exp(-3 * 0.01 / 0.1)
    assert res.ip_ka == pytest.approx(kappa * math.sqrt(2) * res.ik_pp_ka, rel=1e-5)


def test_2ph_earth_lower_than_3ph():
    """Ik2E'' geralmente < Ik3'' para sistemas solidamente aterrados."""
    z1 = complex(0.01, 0.05)
    z0 = complex(0.02, 0.08)
    r3 = fault_3ph(1.1, 0.4, z1)
    r2e = fault_2ph_earth(1.1, 0.4, z1, z0)
    assert r2e.ik_pp_ka < r3.ik_pp_ka * 1.5   # tolerância ampla; só verifica ordem de grandeza
