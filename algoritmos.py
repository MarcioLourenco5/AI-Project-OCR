"""Motor de procura da Fase 2.

Implementa os algoritmos pedidos no enunciado com um formato de saida
uniforme e rastreio por iteracao.
"""

from __future__ import annotations

import heapq
from itertools import count
from typing import Mapping, TypeAlias, TypedDict

Caminho: TypeAlias = tuple[str, ...]
FilaPrioridadeItem: TypeAlias = tuple[int, int, str, Caminho, int, int, int | None]
PilhaItem: TypeAlias = tuple[str, Caminho, int, int]


class EstadoFronteira(TypedDict):
    no: str
    caminho: Caminho
    custo: int
    profundidade: int
    prioridade: int | None
    heuristica: int | None


class IteracaoProcura(TypedDict):
    indice: int
    no_expandido: str
    caminho_expandido: Caminho
    custo_acumulado: int
    profundidade: int
    prioridade_expandida: int | None
    heuristica_expandida: int | None
    fronteira: tuple[EstadoFronteira, ...]


class ResultadoProcura(TypedDict):
    algoritmo: str
    inicio: str
    objetivo: str
    encontrado: bool
    caminho_final: Caminho
    distancia_total: int | None
    total_iteracoes: int
    iteracoes: tuple[IteracaoProcura, ...]
    limite_profundidade: int | None
    motivo_falha: str | None


def _validar_cidades(
    grafo: Mapping[str, Mapping[str, int]],
    inicio: str,
    objetivo: str,
) -> None:
    if inicio not in grafo:
        raise ValueError(f"Cidade inicial desconhecida: {inicio}")
    if objetivo not in grafo:
        raise ValueError(f"Cidade objetivo desconhecida: {objetivo}")


def _validar_limite(limite: int) -> None:
    if limite < 0:
        raise ValueError("O limite de profundidade nao pode ser negativo.")


def _validar_heuristica(
    grafo: Mapping[str, Mapping[str, int]],
    heuristica: Mapping[str, int],
) -> None:
    cidades_em_falta = sorted(set(grafo) - set(heuristica))
    if cidades_em_falta:
        raise ValueError(
            "A heuristica nao cobre todas as cidades do grafo: "
            + ", ".join(cidades_em_falta)
        )


def _vizinhos_ordenados(
    grafo: Mapping[str, Mapping[str, int]],
    no: str,
) -> list[tuple[str, int]]:
    return sorted(grafo[no].items())


def _criar_estado_fronteira(
    no: str,
    caminho: Caminho,
    custo: int,
    profundidade: int,
    prioridade: int | None,
    heuristica: int | None,
) -> EstadoFronteira:
    return {
        "no": no,
        "caminho": caminho,
        "custo": custo,
        "profundidade": profundidade,
        "prioridade": prioridade,
        "heuristica": heuristica,
    }


def _snapshot_fila_prioridade(
    fila: list[FilaPrioridadeItem],
) -> tuple[EstadoFronteira, ...]:
    return tuple(
        _criar_estado_fronteira(no, caminho, custo, profundidade, prioridade, heuristica)
        for prioridade, _, no, caminho, custo, profundidade, heuristica in sorted(fila)
    )


def _snapshot_pilha(pilha: list[PilhaItem]) -> tuple[EstadoFronteira, ...]:
    return tuple(
        _criar_estado_fronteira(no, caminho, custo, profundidade, None, None)
        for no, caminho, custo, profundidade in reversed(pilha)
    )


def _registar_iteracao(
    iteracoes: list[IteracaoProcura],
    no: str,
    caminho: Caminho,
    custo: int,
    profundidade: int,
    prioridade: int | None,
    heuristica: int | None,
    fronteira: tuple[EstadoFronteira, ...],
) -> None:
    iteracoes.append(
        {
            "indice": len(iteracoes) + 1,
            "no_expandido": no,
            "caminho_expandido": caminho,
            "custo_acumulado": custo,
            "profundidade": profundidade,
            "prioridade_expandida": prioridade,
            "heuristica_expandida": heuristica,
            "fronteira": fronteira,
        }
    )


def _resultado(
    algoritmo: str,
    inicio: str,
    objetivo: str,
    iteracoes: list[IteracaoProcura],
    encontrado: bool,
    caminho_final: Caminho = (),
    distancia_total: int | None = None,
    limite_profundidade: int | None = None,
    motivo_falha: str | None = None,
) -> ResultadoProcura:
    return {
        "algoritmo": algoritmo,
        "inicio": inicio,
        "objetivo": objetivo,
        "encontrado": encontrado,
        "caminho_final": caminho_final,
        "distancia_total": distancia_total,
        "total_iteracoes": len(iteracoes),
        "iteracoes": tuple(iteracoes),
        "limite_profundidade": limite_profundidade,
        "motivo_falha": motivo_falha,
    }


def _resultado_inicio_igual_objetivo(
    algoritmo: str,
    inicio: str,
    objetivo: str,
    limite_profundidade: int | None = None,
) -> ResultadoProcura:
    return _resultado(
        algoritmo=algoritmo,
        inicio=inicio,
        objetivo=objetivo,
        iteracoes=[],
        encontrado=True,
        caminho_final=(inicio,),
        distancia_total=0,
        limite_profundidade=limite_profundidade,
    )


def custo_uniforme(
    grafo: Mapping[str, Mapping[str, int]],
    inicio: str,
    objetivo: str,
) -> ResultadoProcura:
    _validar_cidades(grafo, inicio, objetivo)

    if inicio == objetivo:
        return _resultado_inicio_igual_objetivo("custo_uniforme", inicio, objetivo)

    iteracoes: list[IteracaoProcura] = []
    melhor_custo_por_no = {inicio: 0}
    contador = count()
    fila: list[FilaPrioridadeItem] = [(0, next(contador), inicio, (inicio,), 0, 0, None)]

    while fila:
        prioridade, _, no, caminho, custo, profundidade, heuristica = heapq.heappop(fila)

        if custo != melhor_custo_por_no.get(no):
            continue

        if no == objetivo:
            _registar_iteracao(
                iteracoes,
                no,
                caminho,
                custo,
                profundidade,
                prioridade,
                heuristica,
                _snapshot_fila_prioridade(fila),
            )
            return _resultado(
                algoritmo="custo_uniforme",
                inicio=inicio,
                objetivo=objetivo,
                iteracoes=iteracoes,
                encontrado=True,
                caminho_final=caminho,
                distancia_total=custo,
            )

        for vizinho, distancia in _vizinhos_ordenados(grafo, no):
            if vizinho in caminho:
                continue

            novo_custo = custo + distancia
            if novo_custo < melhor_custo_por_no.get(vizinho, float("inf")):
                melhor_custo_por_no[vizinho] = novo_custo
                heapq.heappush(
                    fila,
                    (
                        novo_custo,
                        next(contador),
                        vizinho,
                        caminho + (vizinho,),
                        novo_custo,
                        profundidade + 1,
                        None,
                    ),
                )

        _registar_iteracao(
            iteracoes,
            no,
            caminho,
            custo,
            profundidade,
            prioridade,
            heuristica,
            _snapshot_fila_prioridade(fila),
        )

    return _resultado(
        algoritmo="custo_uniforme",
        inicio=inicio,
        objetivo=objetivo,
        iteracoes=iteracoes,
        encontrado=False,
        motivo_falha="Objetivo nao encontrado.",
    )


def procura_sofrega(
    grafo: Mapping[str, Mapping[str, int]],
    heuristica: Mapping[str, int],
    inicio: str,
    objetivo: str,
) -> ResultadoProcura:
    _validar_cidades(grafo, inicio, objetivo)
    _validar_heuristica(grafo, heuristica)

    if inicio == objetivo:
        return _resultado_inicio_igual_objetivo("procura_sofrega", inicio, objetivo)

    iteracoes: list[IteracaoProcura] = []
    expandidos: set[str] = set()
    contador = count()
    fila: list[FilaPrioridadeItem] = [
        (
            heuristica[inicio],
            next(contador),
            inicio,
            (inicio,),
            0,
            0,
            heuristica[inicio],
        )
    ]

    while fila:
        prioridade, _, no, caminho, custo, profundidade, heuristica_no = heapq.heappop(fila)

        if no in expandidos:
            continue

        if no == objetivo:
            _registar_iteracao(
                iteracoes,
                no,
                caminho,
                custo,
                profundidade,
                prioridade,
                heuristica_no,
                _snapshot_fila_prioridade(fila),
            )
            return _resultado(
                algoritmo="procura_sofrega",
                inicio=inicio,
                objetivo=objetivo,
                iteracoes=iteracoes,
                encontrado=True,
                caminho_final=caminho,
                distancia_total=custo,
            )

        expandidos.add(no)

        for vizinho, distancia in _vizinhos_ordenados(grafo, no):
            if vizinho in caminho or vizinho in expandidos:
                continue

            heapq.heappush(
                fila,
                (
                    heuristica[vizinho],
                    next(contador),
                    vizinho,
                    caminho + (vizinho,),
                    custo + distancia,
                    profundidade + 1,
                    heuristica[vizinho],
                ),
            )

        _registar_iteracao(
            iteracoes,
            no,
            caminho,
            custo,
            profundidade,
            prioridade,
            heuristica_no,
            _snapshot_fila_prioridade(fila),
        )

    return _resultado(
        algoritmo="procura_sofrega",
        inicio=inicio,
        objetivo=objetivo,
        iteracoes=iteracoes,
        encontrado=False,
        motivo_falha="Objetivo nao encontrado.",
    )


def a_estrela(
    grafo: Mapping[str, Mapping[str, int]],
    heuristica: Mapping[str, int],
    inicio: str,
    objetivo: str,
) -> ResultadoProcura:
    _validar_cidades(grafo, inicio, objetivo)
    _validar_heuristica(grafo, heuristica)

    if inicio == objetivo:
        return _resultado_inicio_igual_objetivo("a_estrela", inicio, objetivo)

    iteracoes: list[IteracaoProcura] = []
    melhor_custo_por_no = {inicio: 0}
    contador = count()
    fila: list[FilaPrioridadeItem] = [
        (
            heuristica[inicio],
            next(contador),
            inicio,
            (inicio,),
            0,
            0,
            heuristica[inicio],
        )
    ]

    while fila:
        prioridade, _, no, caminho, custo, profundidade, heuristica_no = heapq.heappop(fila)

        if custo != melhor_custo_por_no.get(no):
            continue

        if no == objetivo:
            _registar_iteracao(
                iteracoes,
                no,
                caminho,
                custo,
                profundidade,
                prioridade,
                heuristica_no,
                _snapshot_fila_prioridade(fila),
            )
            return _resultado(
                algoritmo="a_estrela",
                inicio=inicio,
                objetivo=objetivo,
                iteracoes=iteracoes,
                encontrado=True,
                caminho_final=caminho,
                distancia_total=custo,
            )

        for vizinho, distancia in _vizinhos_ordenados(grafo, no):
            if vizinho in caminho:
                continue

            novo_custo = custo + distancia
            if novo_custo < melhor_custo_por_no.get(vizinho, float("inf")):
                melhor_custo_por_no[vizinho] = novo_custo
                heuristica_vizinho = heuristica[vizinho]
                heapq.heappush(
                    fila,
                    (
                        novo_custo + heuristica_vizinho,
                        next(contador),
                        vizinho,
                        caminho + (vizinho,),
                        novo_custo,
                        profundidade + 1,
                        heuristica_vizinho,
                    ),
                )

        _registar_iteracao(
            iteracoes,
            no,
            caminho,
            custo,
            profundidade,
            prioridade,
            heuristica_no,
            _snapshot_fila_prioridade(fila),
        )

    return _resultado(
        algoritmo="a_estrela",
        inicio=inicio,
        objetivo=objetivo,
        iteracoes=iteracoes,
        encontrado=False,
        motivo_falha="Objetivo nao encontrado.",
    )


def profundidade_limitada(
    grafo: Mapping[str, Mapping[str, int]],
    inicio: str,
    objetivo: str,
    limite: int,
) -> ResultadoProcura:
    _validar_cidades(grafo, inicio, objetivo)
    _validar_limite(limite)

    if inicio == objetivo:
        return _resultado_inicio_igual_objetivo(
            "profundidade_limitada",
            inicio,
            objetivo,
            limite_profundidade=limite,
        )

    iteracoes: list[IteracaoProcura] = []
    pilha: list[PilhaItem] = [(inicio, (inicio,), 0, 0)]

    while pilha:
        no, caminho, custo, profundidade = pilha.pop()

        if no == objetivo:
            _registar_iteracao(
                iteracoes,
                no,
                caminho,
                custo,
                profundidade,
                None,
                None,
                _snapshot_pilha(pilha),
            )
            return _resultado(
                algoritmo="profundidade_limitada",
                inicio=inicio,
                objetivo=objetivo,
                iteracoes=iteracoes,
                encontrado=True,
                caminho_final=caminho,
                distancia_total=custo,
                limite_profundidade=limite,
            )

        if profundidade < limite:
            sucessores: list[PilhaItem] = []
            for vizinho, distancia in _vizinhos_ordenados(grafo, no):
                if vizinho in caminho:
                    continue
                sucessores.append(
                    (vizinho, caminho + (vizinho,), custo + distancia, profundidade + 1)
                )

            for sucessor in reversed(sucessores):
                pilha.append(sucessor)

        _registar_iteracao(
            iteracoes,
            no,
            caminho,
            custo,
            profundidade,
            None,
            None,
            _snapshot_pilha(pilha),
        )

    return _resultado(
        algoritmo="profundidade_limitada",
        inicio=inicio,
        objetivo=objetivo,
        iteracoes=iteracoes,
        encontrado=False,
        limite_profundidade=limite,
        motivo_falha="Objetivo nao encontrado dentro do limite de profundidade.",
    )


__all__ = [
    "Caminho",
    "EstadoFronteira",
    "IteracaoProcura",
    "ResultadoProcura",
    "a_estrela",
    "custo_uniforme",
    "procura_sofrega",
    "profundidade_limitada",
]
