"""
Constantes da IEC 60909:2016.

Tabela 1 — Fatores de tensão c para cálculo de correntes de curto-circuito.
"""

# Fator c por faixa de tensão nominal Un
# Formato: (Un_min_kV, Un_max_kV, cmax, cmin)
# Un_max_kV = inf indica "acima de"
_C_TABLE = [
    (0.0,    1.0,   1.05, 0.95),   # BT até 1 kV (Europa/internacional)
    (1.0,  35.0,   1.10, 1.00),   # MT: 1 kV < Un ≤ 35 kV
    (35.0, float("inf"), 1.10, 1.00),  # AT: Un > 35 kV
]


def get_c_factors(un_kv: float) -> tuple[float, float]:
    """Retorna (cmax, cmin) para a tensão nominal dada (kV)."""
    for un_min, un_max, cmax, cmin in _C_TABLE:
        if un_min <= un_kv < un_max:
            return cmax, cmin
    # acima de qualquer faixa → AT
    return 1.10, 1.00


# Grupos vetoriais que bloqueiam a sequência zero no primário
# (ex.: D = delta; sem caminho para neutro do lado primário)
ZERO_SEQ_BLOCKING_PRIMARY = {"D", "d"}

# Deslocamento de fase do secundário em relação ao primário (graus)
# Sentido positivo: secundário adianta o primário (convencional IEC)
VECTOR_GROUP_PHASE_SHIFT: dict[str, float] = {
    "Dyn1":  -30.0,
    "Dyn11":  30.0,
    "YNyn0":   0.0,
    "Yzn11":  30.0,
    "Dd0":     0.0,
}
