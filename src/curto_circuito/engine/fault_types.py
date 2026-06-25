"""
Cálculo das correntes de curto-circuito (IEC 60909:2016 §4).

Todas as correntes em kA; tensões em kV; impedâncias em Ω.
O ângulo de fase angle_deg é o ângulo de Icc'' = −arg(Z_falta).
"""

import math
import cmath
from ..models.results import FaultResult
from .correction import kappa_factor

_SQRT3 = math.sqrt(3)


def _ik_from_z(c: float, un_kv: float, z: complex) -> float:
    """Ik'' = c * Un / (sqrt(3) * |Z|)  [kA]"""
    z_mag = abs(z)
    if z_mag == 0:
        return float("inf")
    return (c * un_kv) / (_SQRT3 * z_mag)


def _angle(z: complex) -> float:
    """Ângulo de Icc'' = −arg(Z) em graus."""
    if abs(z) == 0:
        return 0.0
    return -math.degrees(cmath.phase(z))


def fault_3ph(c: float, un_kv: float, z1: complex) -> FaultResult:
    """Curto-circuito trifásico simétrico (3F)."""
    ik = _ik_from_z(c, un_kv, z1)
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="3F",
        ik_pp_ka=ik, ip_ka=ip_ka, ib_ka=ik,
        kappa=kappa, z1_ohm=z1, z0_ohm=complex(0, 0),
        angle_deg=_angle(z1),
    )


def fault_3ph_earth(c: float, un_kv: float, z1: complex, z0: complex) -> FaultResult:
    """Curto-circuito trifásico com terra (3F-T).
    Para redes passivas simétricas as correntes de fase são iguais ao 3F.
    """
    ik = _ik_from_z(c, un_kv, z1)
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="3F-T",
        ik_pp_ka=ik, ip_ka=ip_ka, ib_ka=ik,
        kappa=kappa, z1_ohm=z1, z0_ohm=z0,
        angle_deg=_angle(z1),
    )


def fault_2ph(c: float, un_kv: float, z1: complex) -> FaultResult:
    """Curto-circuito bifásico fase-fase (2F).
    IEC 60909 eq. (29): Z_eq = Z1 + Z2 = 2·Z1
    """
    z_eq = 2 * z1
    ik = (_SQRT3 / 2.0) * _ik_from_z(c, un_kv, z1)
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="2F",
        ik_pp_ka=ik, ip_ka=ip_ka, ib_ka=ik,
        kappa=kappa, z1_ohm=z1, z0_ohm=complex(0, 0),
        angle_deg=_angle(z_eq),
    )


def fault_1ph(c: float, un_kv: float, z1: complex, z0: complex) -> FaultResult:
    """Curto-circuito monofásico fase-terra (1F-T).
    IEC 60909 eq. (30): Z_eq = 2·Z1 + Z0
    """
    z_eq = 2 * z1 + z0
    z_mag = abs(z_eq)
    ik = (_SQRT3 * c * un_kv) / z_mag if z_mag != 0 else float("inf")
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="1F-T",
        ik_pp_ka=ik, ip_ka=ip_ka, ib_ka=ik,
        kappa=kappa, z1_ohm=z1, z0_ohm=z0,
        angle_deg=_angle(z_eq),
    )


def fault_2ph_earth(c: float, un_kv: float, z1: complex, z0: complex) -> FaultResult:
    """Curto-circuito bifásico com terra (2F-T).
    IEC 60909 eq. (31); Z2 = Z1 para elementos passivos.
    """
    z2 = z1
    numerador_inner = abs(z2)**2 + (z2 * z0.conjugate()).real + abs(z0)**2
    numerador = (c * un_kv / _SQRT3) * math.sqrt(max(numerador_inner, 0.0))
    z_den = z1 * (z2 + z0) + z2 * z0
    denominador = abs(z_den)
    ik = numerador / denominador if denominador != 0 else float("inf")
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="2F-T",
        ik_pp_ka=ik, ip_ka=ip_ka, ib_ka=ik,
        kappa=kappa, z1_ohm=z1, z0_ohm=z0,
        angle_deg=_angle(z_den),
    )
