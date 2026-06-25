"""
Cálculo das correntes de curto-circuito (IEC 60909:2016 §4).

Todas as correntes em kA; tensões em kV; impedâncias em Ω.
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
    return (c * un_kv) / (_SQRT3 * z_mag)   # resultado já em kA se Un em kV e Z em Ω


def fault_3ph(c: float, un_kv: float, z1: complex) -> FaultResult:
    """Curto-circuito trifásico simétrico (3F)."""
    ik = _ik_from_z(c, un_kv, z1)
    kappa = kappa_factor(z1)
    ip = kappa * _SQRT3 * ik   # Ip = κ * √2 * Ik'' (√2 * kA)
    # nota: IEC eq.17: Ip = κ√2 Ik''; aqui Ik'' já está em kA → Ip em kA
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="3F",
        ik_pp_ka=ik,
        ip_ka=ip_ka,
        ib_ka=ik,   # Ib ≈ Ik'' para fontes remotas (μ=1)
        kappa=kappa,
        z1_ohm=z1,
        z0_ohm=complex(0, 0),
    )


def fault_2ph(c: float, un_kv: float, z1: complex) -> FaultResult:
    """Curto-circuito bifásico (fase-fase, sem terra) (2F).
    IEC 60909 eq. (29): Ik2'' = c*Un / |Z1+Z2|  com Z2=Z1 → (√3/2)*Ik3''
    """
    ik = (_SQRT3 / 2.0) * _ik_from_z(c, un_kv, z1)
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="2F",
        ik_pp_ka=ik,
        ip_ka=ip_ka,
        ib_ka=ik,
        kappa=kappa,
        z1_ohm=z1,
        z0_ohm=complex(0, 0),
    )


def fault_1ph(c: float, un_kv: float, z1: complex, z0: complex) -> FaultResult:
    """Curto-circuito monofásico fase-terra (1F-T).
    IEC 60909 eq. (30): Ik1'' = √3 * c * Un / |2*Z1 + Z0|
    """
    z_total = 2 * z1 + z0
    z_mag = abs(z_total)
    if z_mag == 0:
        ik = float("inf")
    else:
        ik = (_SQRT3 * c * un_kv) / z_mag
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="1F-T",
        ik_pp_ka=ik,
        ip_ka=ip_ka,
        ib_ka=ik,
        kappa=kappa,
        z1_ohm=z1,
        z0_ohm=z0,
    )


def fault_2ph_earth(c: float, un_kv: float, z1: complex, z0: complex) -> FaultResult:
    """Curto-circuito bifásico com terra (2F-T).
    IEC 60909 eq. (31): corrente na fase em falta
      Ik2E'' = c*Un / (√3) * √(|Z2|² + Z2·Z0* + |Z0|²) / |Z1*(Z2+Z0) + Z2*Z0|
    com Z2 = Z1 para elementos passivos.
    """
    z2 = z1   # Z2 = Z1 para componentes passivos
    numerador_inner = abs(z2)**2 + (z2 * z0.conjugate()).real + abs(z0)**2
    numerador = (c * un_kv / _SQRT3) * math.sqrt(max(numerador_inner, 0.0))
    denominador = abs(z1 * (z2 + z0) + z2 * z0)
    if denominador == 0:
        ik = float("inf")
    else:
        ik = numerador / denominador
    kappa = kappa_factor(z1)
    ip_ka = kappa * math.sqrt(2) * ik
    return FaultResult(
        fault_type="2F-T",
        ik_pp_ka=ik,
        ip_ka=ip_ka,
        ib_ka=ik,
        kappa=kappa,
        z1_ohm=z1,
        z0_ohm=z0,
    )
