

import heapq

def a_estrela(grafo, heuristica, inicio, objetivo):
    fila = []
    heapq.heappush(fila, (0, inicio, [inicio], 0))

    visitados = set()

    while fila:
        _, atual, caminho, custo = heapq.heappop(fila)

        if atual == objetivo:
            return caminho, custo

        if atual in visitados:
            continue

        visitados.add(atual)

        for vizinho, distancia in grafo[atual].items():
            novo_custo = custo + distancia
            prioridade = novo_custo + heuristica[vizinho]

            heapq.heappush(fila, (prioridade, vizinho, caminho + [vizinho], novo_custo))

    return None, float("inf")