"""Dados do dominio do trabalho pratico.

Este modulo concentra as cidades canonicas, as ligacoes base entre cidades,
o grafo bidirecional derivado dessas ligacoes e a heuristica de distancia em
linha reta ate Faro.
"""

from __future__ import annotations

from typing import Iterable, Mapping, TypeAlias, TypedDict

ArestaAssimetrica: TypeAlias = tuple[str, str, int, int | None]


class RelatorioValidacao(TypedDict):
    total_cidades: int
    total_ligacoes_nao_direcionadas: int
    cidades_orfas: tuple[str, ...]
    cidades_canonicas_sem_grafo: tuple[str, ...]
    cidades_grafo_nao_canonicas: tuple[str, ...]
    cidades_canonicas_sem_heuristica: tuple[str, ...]
    cidades_heuristica_nao_canonicas: tuple[str, ...]
    arestas_assimetricas: tuple[ArestaAssimetrica, ...]
    heuristica_faro: int | None

CIDADES = (
    "Aveiro",
    "Braga",
    "Bragança",
    "Beja",
    "Castelo Branco",
    "Coimbra",
    "Évora",
    "Faro",
    "Guarda",
    "Leiria",
    "Lisboa",
    "Portalegre",
    "Porto",
    "Santarém",
    "Setúbal",
    "Viana do Castelo",
    "Vila Real",
    "Viseu",
)

(
    AVEIRO,
    BRAGA,
    BRAGANCA,
    BEJA,
    CASTELO_BRANCO,
    COIMBRA,
    EVORA,
    FARO,
    GUARDA,
    LEIRIA,
    LISBOA,
    PORTALEGRE,
    PORTO,
    SANTAREM,
    SETUBAL,
    VIANA,
    VILA_REAL,
    VISEU,
) = CIDADES

# As ligacoes sao declaradas uma vez e o grafo final e construido
# automaticamente nos dois sentidos.
ARESTAS_BASE = (
    (AVEIRO, PORTO, 68),
    (AVEIRO, VISEU, 95),
    (AVEIRO, COIMBRA, 68),
    (AVEIRO, LEIRIA, 115),
    (BRAGA, VIANA, 48),
    (BRAGA, VILA_REAL, 106),
    (BRAGA, PORTO, 53),
    (BRAGANCA, VILA_REAL, 137),
    (BRAGANCA, GUARDA, 202),
    (BEJA, EVORA, 78),
    (BEJA, FARO, 152),
    (BEJA, SETUBAL, 142),
    (CASTELO_BRANCO, COIMBRA, 159),
    (CASTELO_BRANCO, GUARDA, 106),
    (CASTELO_BRANCO, PORTALEGRE, 80),
    (CASTELO_BRANCO, EVORA, 203),
    (COIMBRA, VISEU, 96),
    (COIMBRA, LEIRIA, 67),
    (EVORA, LISBOA, 150),
    (EVORA, SANTAREM, 117),
    (EVORA, PORTALEGRE, 131),
    (EVORA, SETUBAL, 103),
    (FARO, SETUBAL, 249),
    (FARO, LISBOA, 299),
    (GUARDA, VILA_REAL, 157),
    (GUARDA, VISEU, 85),
    (LEIRIA, LISBOA, 129),
    (LEIRIA, SANTAREM, 70),
    (LISBOA, SANTAREM, 78),
    (LISBOA, SETUBAL, 50),
    (PORTO, VIANA, 71),
    (PORTO, VILA_REAL, 116),
    (PORTO, VISEU, 133),
    (VILA_REAL, VISEU, 110),
)

HEURISTICA_FARO = {
    AVEIRO: 366,
    BRAGA: 454,
    BRAGANCA: 487,
    BEJA: 99,
    CASTELO_BRANCO: 280,
    COIMBRA: 319,
    EVORA: 157,
    FARO: 0,
    GUARDA: 352,
    LEIRIA: 278,
    LISBOA: 195,
    PORTALEGRE: 228,
    PORTO: 418,
    SANTAREM: 231,
    SETUBAL: 168,
    VIANA: 473,
    VILA_REAL: 429,
    VISEU: 363,
}


def _adicionar_aresta(
    grafo: dict[str, dict[str, int]],
    origem: str,
    destino: str,
    distancia: int,
) -> None:
    distancia_existente = grafo[origem].get(destino)
    if distancia_existente is not None and distancia_existente != distancia:
        raise ValueError(
            f"Aresta inconsistente para {origem} -> {destino}: "
            f"{distancia_existente} != {distancia}"
        )

    grafo[origem][destino] = distancia


def construir_grafo_bidirecional(
    arestas: Iterable[tuple[str, str, int]],
    cidades: Iterable[str] = CIDADES,
) -> dict[str, dict[str, int]]:
    """Constroi um grafo com ligacoes nos dois sentidos a partir das arestas base."""

    cidades_canonicas = tuple(cidades)
    cidades_conhecidas = set(cidades_canonicas)
    grafo = {cidade: {} for cidade in cidades_canonicas}

    for origem, destino, distancia in arestas:
        if origem not in cidades_conhecidas:
            raise ValueError(f"Cidade desconhecida nas arestas base: {origem}")
        if destino not in cidades_conhecidas:
            raise ValueError(f"Cidade desconhecida nas arestas base: {destino}")
        if origem == destino:
            raise ValueError(f"Aresta invalida em lacete: {origem} -> {destino}")
        if distancia <= 0:
            raise ValueError(
                f"Distancia invalida para {origem} -> {destino}: {distancia}"
            )

        _adicionar_aresta(grafo, origem, destino, distancia)
        _adicionar_aresta(grafo, destino, origem, distancia)

    return grafo


def contar_ligacoes_nao_direcionadas(grafo: Mapping[str, Mapping[str, int]]) -> int:
    """Conta ligacoes unicas ignorando a direcao."""

    ligacoes = {
        (tuple(sorted((origem, destino))), distancia)
        for origem, vizinhos in grafo.items()
        for destino, distancia in vizinhos.items()
    }
    return len(ligacoes)


def gerar_relatorio_validacao(
    cidades: Iterable[str],
    grafo: Mapping[str, Mapping[str, int]],
    heuristica: Mapping[str, int],
) -> RelatorioValidacao:
    """Gera um relatorio com os principais indicadores de consistencia."""

    cidades_canonicas = tuple(cidades)
    conjunto_canonico = set(cidades_canonicas)
    cidades_do_grafo = set(grafo)
    cidades_da_heuristica = set(heuristica)

    arestas_assimetricas: set[ArestaAssimetrica] = set()
    for origem, vizinhos in grafo.items():
        for destino, distancia in vizinhos.items():
            distancia_inversa = grafo.get(destino, {}).get(origem)
            if distancia_inversa != distancia:
                arestas_assimetricas.add((origem, destino, distancia, distancia_inversa))

    return {
        "total_cidades": len(cidades_canonicas),
        "total_ligacoes_nao_direcionadas": contar_ligacoes_nao_direcionadas(grafo),
        "cidades_orfas": tuple(
            sorted(cidade for cidade, vizinhos in grafo.items() if not vizinhos)
        ),
        "cidades_canonicas_sem_grafo": tuple(
            sorted(conjunto_canonico - cidades_do_grafo)
        ),
        "cidades_grafo_nao_canonicas": tuple(
            sorted(cidades_do_grafo - conjunto_canonico)
        ),
        "cidades_canonicas_sem_heuristica": tuple(
            sorted(conjunto_canonico - cidades_da_heuristica)
        ),
        "cidades_heuristica_nao_canonicas": tuple(
            sorted(cidades_da_heuristica - conjunto_canonico)
        ),
        "arestas_assimetricas": tuple(sorted(arestas_assimetricas)),
        "heuristica_faro": heuristica.get(FARO),
    }


def validar_dados(
    cidades: Iterable[str] = CIDADES,
    grafo: Mapping[str, Mapping[str, int]] | None = None,
    heuristica: Mapping[str, int] = HEURISTICA_FARO,
) -> RelatorioValidacao:
    """Valida o conjunto de dados e devolve um resumo util para inspeccao."""

    if grafo is None:
        grafo = GRAFO

    relatorio = gerar_relatorio_validacao(cidades, grafo, heuristica)
    problemas: list[str] = []

    if relatorio["cidades_orfas"]:
        problemas.append(
            f"Existem cidades sem ligacoes: {', '.join(relatorio['cidades_orfas'])}"
        )
    if relatorio["cidades_canonicas_sem_grafo"]:
        problemas.append(
            "Cidades canonicas ausentes do grafo: "
            f"{', '.join(relatorio['cidades_canonicas_sem_grafo'])}"
        )
    if relatorio["cidades_grafo_nao_canonicas"]:
        problemas.append(
            "Grafo contem cidades nao canonicas: "
            f"{', '.join(relatorio['cidades_grafo_nao_canonicas'])}"
        )
    if relatorio["cidades_canonicas_sem_heuristica"]:
        problemas.append(
            "Cidades sem heuristica para Faro: "
            f"{', '.join(relatorio['cidades_canonicas_sem_heuristica'])}"
        )
    if relatorio["cidades_heuristica_nao_canonicas"]:
        problemas.append(
            "Heuristica contem cidades nao canonicas: "
            f"{', '.join(relatorio['cidades_heuristica_nao_canonicas'])}"
        )
    if relatorio["arestas_assimetricas"]:
        arestas = ", ".join(
            f"{origem}->{destino} ({distancia} / {inversa})"
            for origem, destino, distancia, inversa in relatorio["arestas_assimetricas"]
        )
        problemas.append(f"Existem arestas assimetricas: {arestas}")
    if relatorio["heuristica_faro"] != 0:
        problemas.append("A heuristica de Faro deve ser igual a 0.")

    if problemas:
        raise ValueError("Dados invalidos:\n- " + "\n- ".join(problemas))

    return relatorio


GRAFO = construir_grafo_bidirecional(ARESTAS_BASE, CIDADES)
VALIDACAO_DADOS = validar_dados(CIDADES, GRAFO, HEURISTICA_FARO)

__all__ = [
    "AVEIRO",
    "BRAGA",
    "BRAGANCA",
    "BEJA",
    "CASTELO_BRANCO",
    "COIMBRA",
    "EVORA",
    "FARO",
    "GUARDA",
    "LEIRIA",
    "LISBOA",
    "PORTALEGRE",
    "PORTO",
    "SANTAREM",
    "SETUBAL",
    "VIANA",
    "VILA_REAL",
    "VISEU",
    "ArestaAssimetrica",
    "ARESTAS_BASE",
    "CIDADES",
    "GRAFO",
    "HEURISTICA_FARO",
    "RelatorioValidacao",
    "VALIDACAO_DADOS",
    "construir_grafo_bidirecional",
    "contar_ligacoes_nao_direcionadas",
    "gerar_relatorio_validacao",
    "validar_dados",
]
