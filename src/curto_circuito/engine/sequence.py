"""
Montagem das redes de sequência zero (Z0) ao longo do caminho até a barra de falta.

Regras de grupo vetorial (IEC 60909:2016 §3.6):
- Lado com enrolamento em delta (D/d): bloqueia a seq. zero (abre o circuito Z0).
- Lado com estrela aterrada (YN/yn): fornece caminho para seq. zero.
- Lado com estrela sem aterramento (Y/y): bloqueia seq. zero.
"""

import cmath
from ..models.components import Transformer, Cable
from ..models.network import Branch, NetworkNode, Network
from ..utils.units import refer_impedance
from . import impedance as imp


def _primary_letter(vector_group: str) -> str:
    """Extrai a letra do lado primário (primeiro caractere, maiúsculo)."""
    return vector_group[0].upper() if vector_group else "D"


def _secondary_letter(vector_group: str) -> str:
    """Extrai a letra do lado secundário (segundo caractere, maiúsculo)."""
    return vector_group[1].upper() if len(vector_group) > 1 else "Y"


def primary_blocks_z0(t: Transformer) -> bool:
    """True se o enrolamento primário bloqueia a corrente de seq. zero."""
    return _primary_letter(t.vector_group) == "D"


def secondary_blocks_z0(t: Transformer) -> bool:
    """True se o enrolamento secundário bloqueia a corrente de seq. zero."""
    sec = _secondary_letter(t.vector_group)
    # 'Y' sem aterramento bloqueia; 'N' (estrela aterrada) ou 'Z' permitem
    if sec == "D":
        return True
    if sec == "Y":
        # verifica se há "N" explícito depois (ex.: "yn" → "YN")
        return "N" not in vector_group_upper(t.vector_group)
    return False


def vector_group_upper(vg: str) -> str:
    return vg.upper()


def build_z0_thevenin(
    path: list[tuple[Branch | None, NetworkNode]],
    fault_un_kv: float,
    z0_grid: complex,
) -> complex:
    """
    Monta Z0 de Thevenin na barra de falta percorrendo o caminho desde a raiz.

    A corrente de seq. zero é bloqueada quando o trafo tem primário em delta.
    Nesse caso, Z0 só considera os elementos do lado da barra de falta até
    o transformador bloqueador mais próximo.

    Retorna Z0 total referido a fault_un_kv.
    """
    # Percorre o caminho do fim (barra de falta) para o início (fonte),
    # acumulando impedâncias até encontrar um trafo que bloqueie Z0.
    z0 = complex(0, 0)
    blocked = False

    for branch, node in reversed(path):
        if branch is None:
            # raiz (grid connection) — só adiciona se não bloqueado
            if not blocked:
                z0_referred = refer_impedance(z0_grid, node.un_kv, fault_un_kv)
                z0 += z0_referred
            break

        comp = branch.component

        if isinstance(comp, Transformer):
            z0_comp = imp.transformer_z0(comp)
            # refere ao nível da barra de falta
            z0_comp_ref = refer_impedance(z0_comp, comp.un2_kv, fault_un_kv)

            if primary_blocks_z0(comp):
                # O primário delta bloqueia: só adiciona Z0 do trafo e para.
                z0 += z0_comp_ref
                blocked = True
                break
            else:
                z0 += z0_comp_ref

        elif isinstance(comp, Cable):
            if not blocked:
                z0_comp = imp.cable_z0(comp)
                z0_comp_ref = refer_impedance(z0_comp, comp.un_kv, fault_un_kv)
                z0 += z0_comp_ref

    return z0
