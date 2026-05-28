"""Mock da API Serasa — consulta por CPF."""

from dataclasses import dataclass
from datetime import datetime

CPFS_NEGATIVADOS = {
    "47210388290",
    "11111111111",
}


@dataclass
class ResultadoSerasa:
    cpf: str
    negativado: bool
    score: int
    restricoes: int
    consultado_em: datetime


def _limpar_cpf(cpf: str) -> str:
    return "".join(c for c in cpf if c.isdigit())


def consultar_cpf(cpf: str) -> ResultadoSerasa:
    limpo = _limpar_cpf(cpf)
    agora = datetime.now()

    if limpo in CPFS_NEGATIVADOS or limpo.endswith("999"):
        return ResultadoSerasa(
            cpf=limpo,
            negativado=True,
            score=312,
            restricoes=2,
            consultado_em=agora,
        )

    score = 650 + (int(limpo[-3:]) % 350) if len(limpo) >= 3 else 720
    return ResultadoSerasa(
        cpf=limpo,
        negativado=False,
        score=min(score, 1000),
        restricoes=0,
        consultado_em=agora,
    )
