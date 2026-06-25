"""Testes das constantes e tabelas de grupos vetoriais."""

import pytest
from curto_circuito.utils.constants import VECTOR_GROUP_PHASE_SHIFT


def test_dyn11_shift():
    assert VECTOR_GROUP_PHASE_SHIFT["Dyn11"] == pytest.approx(30.0)


def test_dyn1_shift():
    assert VECTOR_GROUP_PHASE_SHIFT["Dyn1"] == pytest.approx(-30.0)


def test_ynyn0_shift():
    assert VECTOR_GROUP_PHASE_SHIFT["YNyn0"] == pytest.approx(0.0)


def test_dd0_shift():
    assert VECTOR_GROUP_PHASE_SHIFT["Dd0"] == pytest.approx(0.0)
