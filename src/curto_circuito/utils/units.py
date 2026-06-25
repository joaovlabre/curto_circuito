"""Funções de conversão de unidades para cálculos IEC 60909."""

import cmath


def refer_impedance(z_ohm: complex, v_from_kv: float, v_to_kv: float) -> complex:
    """Refere impedância de v_from_kv para v_to_kv (método do quadrado da razão de tensão)."""
    ratio = v_to_kv / v_from_kv
    return z_ohm * ratio**2


def mva_to_va(mva: float) -> float:
    return mva * 1e6


def kv_to_v(kv: float) -> float:
    return kv * 1e3


def ka_to_a(ka: float) -> float:
    return ka * 1e3


def z_from_sk(un_kv: float, sk_mva: float, rx_ratio: float) -> complex:
    """Impedância da rede a partir de Sk'' e razão R/X (em ohms)."""
    if sk_mva == 0:
        return complex(0, 0)   # barra infinita
    un_v = kv_to_v(un_kv)
    z_mag = un_v**2 / mva_to_va(sk_mva)
    # Z = R + jX,  R/X = rx_ratio  =>  Z = X*(rx_ratio + j)
    # |Z|² = X²*(rx_ratio² + 1)  =>  X = |Z| / sqrt(rx² + 1)
    import math
    x = z_mag / math.sqrt(rx_ratio**2 + 1)
    r = rx_ratio * x
    return complex(r, x)
