"""
Cálculo de impedâncias por componente (IEC 60909:2016 §3).

Todos os resultados são em ohms referidos à tensão nominal do próprio componente.
A referência ao nível de tensão da barra de falta é feita em engine/reduction.py.
"""

import cmath
import math
from ..models.components import GridConnection, Transformer, Cable, Busbar
from ..utils.units import kv_to_v, mva_to_va, z_from_sk


def grid_z1(g: GridConnection) -> complex:
    """Impedância de seq. positiva da rede (Ω @ Un_grid)."""
    return z_from_sk(g.un_kv, g.sk_mva, g.rx_ratio)


def grid_z0(g: GridConnection) -> complex:
    """Impedância de seq. zero da rede; assume Z0 = Z1 para redes de AT."""
    return grid_z1(g)


def transformer_z1(t: Transformer) -> complex:
    """
    Impedância de curto-circuito do trafo referida ao secundário (Ω @ Un2).
    IEC 60909 §3.3.1: ZT = (uk%/100) * Un2² / Sn
                       RT = Pk * Un2² / Sn²
    """
    un2_v = kv_to_v(t.un2_kv)
    sn_va = mva_to_va(t.sn_mva)
    pk_w = t.pk_kw * 1e3

    zt_mag = (t.uk_pct / 100.0) * un2_v**2 / sn_va
    rt = pk_w * un2_v**2 / sn_va**2
    # garante que RT ≤ ZT (arredondamentos numéricos)
    rt = min(rt, zt_mag)
    xt = math.sqrt(max(zt_mag**2 - rt**2, 0.0))
    return complex(rt, xt)


def transformer_z0(t: Transformer) -> complex:
    """
    Impedância de seq. zero do trafo, referida ao secundário.
    Para grupos Dyn e Yzn: Z0 ≈ Z1 do lado do neutro aterrado.
    Para grupos Yyn (neutro BT isolado do primário): Z0 = Z1 (aproximação).
    O tratamento exato do bloqueio de Z0 é feito em engine/sequence.py.
    """
    return transformer_z1(t)


def cable_z1(c: Cable) -> complex:
    """Impedância de seq. positiva do cabo (Ω)."""
    return complex(c.r1_ohm_km, c.x1_ohm_km) * c.length_km


def cable_z0(c: Cable) -> complex:
    """Impedância de seq. zero do cabo (Ω)."""
    return complex(c.r0_ohm_km, c.x0_ohm_km) * c.length_km


def busbar_z1(_: Busbar) -> complex:
    return complex(0, 0)


def busbar_z0(_: Busbar) -> complex:
    return complex(0, 0)
