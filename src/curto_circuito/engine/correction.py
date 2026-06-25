"""
Fatores de correção de impedâncias (IEC 60909:2016 §3.3.3 e §4).
"""

import math
import cmath
from ..models.components import Transformer


def kt_factor(t: Transformer, cmax: float) -> float:
    """
    Fator de correção de impedância do transformador (KT).
    IEC 60909 eq. (12): KT = 0,95 * cmax / (1 + 0,6 * xT)
    onde xT = XT / ZT (fração reativa relativa).
    """
    z1 = _zt_components(t)
    zt_mag = abs(z1)
    if zt_mag == 0:
        return 1.0
    xt = z1.imag
    xt_rel = xt / zt_mag   # xT adimensional
    return 0.95 * cmax / (1.0 + 0.6 * xt_rel)


def kappa_factor(z_thevenin: complex) -> float:
    """
    Fator de pico κ para cálculo da corrente de pico Ip.
    IEC 60909 eq. (18): κ = 1,02 + 0,98 * exp(-3 * R/X)
    """
    if z_thevenin.imag == 0:
        return 1.02   # puramente resistivo → mínimo
    rx = z_thevenin.real / z_thevenin.imag
    return 1.02 + 0.98 * math.exp(-3.0 * rx)


def _zt_components(t: Transformer) -> complex:
    """ZT bruto (sem correção) para uso interno."""
    from .impedance import transformer_z1
    return transformer_z1(t)
