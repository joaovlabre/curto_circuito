"""Testes dos fatores de correção IEC 60909."""

import math
import pytest
from curto_circuito.models.components import Transformer
from curto_circuito.engine.correction import kt_factor, kappa_factor
from curto_circuito.engine.impedance import transformer_z1


def test_kt_formula():
    """KT = 0,95 * cmax / (1 + 0,6 * xT)."""
    t = Transformer(id="T", name="T", sn_mva=0.63, un1_kv=13.8, un2_kv=0.4, z_pct=4.0, pk_kw=6.0)
    cmax = 1.10
    kt = kt_factor(t, cmax)
    z = transformer_z1(t)
    xt_rel = z.imag / abs(z)
    expected = 0.95 * cmax / (1.0 + 0.6 * xt_rel)
    assert kt == pytest.approx(expected, rel=1e-6)


def test_kappa_low_rx():
    """Para R/X → 0 (puramente reativo), κ → 1,02 + 0,98 = 2,0."""
    z = complex(0.001, 1.0)  # R/X ≈ 0
    k = kappa_factor(z)
    assert k == pytest.approx(2.0, abs=0.01)


def test_kappa_high_rx():
    """Para R/X → ∞ (puramente resistivo), κ → 1,02."""
    z = complex(1000.0, 0.001)  # R/X >> 1
    k = kappa_factor(z)
    assert k == pytest.approx(1.02, abs=0.01)


def test_kappa_typical():
    """κ para R/X = 0,1 → 1,02 + 0,98*exp(-0,3) ≈ 1,745."""
    z = complex(0.1, 1.0)   # R/X = 0,1
    k = kappa_factor(z)
    expected = 1.02 + 0.98 * math.exp(-3 * 0.1)
    assert k == pytest.approx(expected, rel=1e-6)
