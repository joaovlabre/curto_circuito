"""Testes das fórmulas de impedância por componente."""

import math
import pytest
from curto_circuito.models.components import GridConnection, Transformer, Cable
from curto_circuito.engine.impedance import grid_z1, transformer_z1, cable_z1, cable_z0
from curto_circuito.utils.units import kv_to_v, mva_to_va


def test_grid_z1_zero_impedance():
    """R1=X1=0 → Z1 nulo (barra infinita)."""
    g = GridConnection(id="G", name="G", un_kv=13.8,
                       z1_r_ohm=0, z1_x_ohm=0, z0_r_ohm=0, z0_x_ohm=0)
    z = grid_z1(g)
    assert z == complex(0, 0)


def test_grid_z1_magnitude():
    """Z1 armazenado em Ω deve ser retornado diretamente com R e X corretos."""
    g = GridConnection(id="G", name="G", un_kv=13.8,
                       z1_r_ohm=0.0379, z1_x_ohm=0.3790,
                       z0_r_ohm=0.0379, z0_x_ohm=0.3790)
    z = grid_z1(g)
    assert z.real == pytest.approx(0.0379, rel=1e-4)
    assert z.imag == pytest.approx(0.3790, rel=1e-4)


def test_grid_z0_independent():
    """Z0 deve ser independente de Z1."""
    g = GridConnection(id="G", name="G", un_kv=13.8,
                       z1_r_ohm=0.010, z1_x_ohm=0.100,
                       z0_r_ohm=0.030, z0_x_ohm=0.300)
    from curto_circuito.engine.impedance import grid_z0
    z0 = grid_z0(g)
    assert z0.real == pytest.approx(0.030, rel=1e-4)
    assert z0.imag == pytest.approx(0.300, rel=1e-4)


def test_transformer_z1_magnitude():
    """ZT = (uk%/100) * Un2² / Sn  (eq. IEC 60909 §3.3.1)."""
    t = Transformer(id="T", name="T", sn_mva=0.63, un1_kv=13.8, un2_kv=0.4, z_pct=4.0, pk_kw=6.0)
    z = transformer_z1(t)
    un2_v = kv_to_v(0.4)
    sn_va = mva_to_va(0.63)
    zt_expected = (4.0 / 100.0) * un2_v**2 / sn_va
    assert abs(z) == pytest.approx(zt_expected, rel=1e-4)


def test_transformer_z1_rt():
    """RT = Pk * Un2² / Sn²."""
    t = Transformer(id="T", name="T", sn_mva=0.63, un1_kv=13.8, un2_kv=0.4, z_pct=4.0, pk_kw=6.0)
    z = transformer_z1(t)
    un2_v = kv_to_v(0.4)
    sn_va = mva_to_va(0.63)
    pk_w = 6.0e3
    rt_expected = pk_w * un2_v**2 / sn_va**2
    assert z.real == pytest.approx(rt_expected, rel=1e-4)


def test_cable_z1():
    c = Cable(id="C", name="C", un_kv=0.4, r1_ohm_km=0.206, x1_ohm_km=0.08,
              r0_ohm_km=0.618, x0_ohm_km=0.24, length_m=100)
    z1 = cable_z1(c)
    assert z1.real == pytest.approx(0.206 * 0.1, rel=1e-6)   # 100 m = 0,1 km
    assert z1.imag == pytest.approx(0.08 * 0.1, rel=1e-6)


def test_cable_z0():
    c = Cable(id="C", name="C", un_kv=0.4, r1_ohm_km=0.206, x1_ohm_km=0.08,
              r0_ohm_km=0.618, x0_ohm_km=0.24, length_m=100)
    z0 = cable_z0(c)
    assert z0.real == pytest.approx(0.618 * 0.1, rel=1e-6)
    assert z0.imag == pytest.approx(0.24 * 0.1, rel=1e-6)
