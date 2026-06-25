from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class GridConnection:
    """Ponto de conexão com a rede da concessionária (fonte)."""
    id: str
    name: str
    un_kv: float          # tensão nominal fase-fase (kV)
    sk_mva: float         # potência de curto-circuito inicial (MVA); 0 = barra infinita
    rx_ratio: float       # razão R/X da rede
    cmax: float = 1.1     # fator de tensão máximo (IEC 60909 Tabela 1)
    cmin: float = 0.95    # fator de tensão mínimo

    def __post_init__(self) -> None:
        if self.un_kv <= 0:
            raise ValueError("un_kv deve ser positivo")
        if self.sk_mva < 0:
            raise ValueError("sk_mva não pode ser negativo")
        if self.rx_ratio < 0:
            raise ValueError("rx_ratio não pode ser negativo")


@dataclass
class Transformer:
    """Transformador MT/BT ou AT/MT."""
    id: str
    name: str
    sn_mva: float         # potência nominal (MVA)
    un1_kv: float         # tensão nominal primário (kV)
    un2_kv: float         # tensão nominal secundário (kV)
    z_pct: float         # impedância de curto-circuito (%)
    pk_kw: float          # perdas em carga na corrente nominal (kW)
    vector_group: str = "Dyn11"   # grupo vetorial; afeta caminho de Z0
    grounding: str = "solid"      # aterramento do neutro: "solid", "resistance", "isolated"

    def __post_init__(self) -> None:
        if self.sn_mva <= 0:
            raise ValueError("sn_mva deve ser positivo")
        if self.z_pct <= 0:
            raise ValueError("z_pct (Z%) deve ser positivo")
        if self.pk_kw < 0:
            raise ValueError("pk_kw não pode ser negativo")


@dataclass
class Cable:
    """Cabo elétrico de MT ou BT."""
    id: str
    name: str
    un_kv: float          # tensão nominal (kV)
    r1_ohm_km: float      # resistência seq. positiva (Ω/km)
    x1_ohm_km: float      # reatância seq. positiva (Ω/km)
    r0_ohm_km: float      # resistência seq. zero (Ω/km)
    x0_ohm_km: float      # reatância seq. zero (Ω/km)
    length_m: float       # comprimento (m)

    def __post_init__(self) -> None:
        if self.length_m <= 0:
            raise ValueError("length_m deve ser positivo")
        if self.r1_ohm_km < 0 or self.x1_ohm_km < 0:
            raise ValueError("impedâncias de sequência positiva não podem ser negativas")

    @property
    def length_km(self) -> float:
        return self.length_m / 1000.0


@dataclass
class Busbar:
    """Barra de barramento (impedância desprezível)."""
    id: str
    name: str
    un_kv: float          # tensão nominal (kV)
    description: str = ""
