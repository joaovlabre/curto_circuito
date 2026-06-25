from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FaultResult:
    """Correntes de curto-circuito para um tipo de falta em uma barra."""
    fault_type: str        # "3F", "3F-T", "2F", "1F-T", "2F-T"
    ik_pp_ka: float        # corrente simétrica inicial Ik'' (kA)
    ip_ka: float           # corrente de pico Ip (kA)
    ib_ka: float           # corrente de abertura Ib (kA)
    kappa: float           # fator de pico κ
    z1_ohm: complex        # impedância de Thevenin seq. positiva (Ω)
    z0_ohm: complex        # impedância de Thevenin seq. zero (Ω)
    angle_deg: float = 0.0 # ângulo de fase de Icc'' (graus); negativo de arg(Z_falta)


@dataclass
class BusResult:
    """Resultados de todas as faltas para uma barra."""
    node_id: str
    node_name: str
    un_kv: float
    faults: list[FaultResult] = field(default_factory=list)
    phase_shift_deg: float = 0.0   # deslocamento acumulado de fase via grupo vetorial (graus)

    def get_fault(self, fault_type: str) -> FaultResult | None:
        for f in self.faults:
            if f.fault_type == fault_type:
                return f
        return None


@dataclass
class StudyResults:
    """Resultado completo de um estudo de curto-circuito."""
    network_name: str
    timestamp: str          # ISO 8601
    voltage_factor_c: float
    s_base_mva: float = 100.0  # base de potência para conversão p.u.
    buses: list[BusResult] = field(default_factory=list)
