import unittest

from algoritmos import (
    a_estrela,
    custo_uniforme,
    profundidade_limitada,
    procura_sofrega,
)
from dados import BEJA, BRAGA, COIMBRA, FARO, GRAFO, HEURISTICA_FARO, LISBOA

CHAVES_RESULTADO = {
    "algoritmo",
    "inicio",
    "objetivo",
    "encontrado",
    "caminho_final",
    "distancia_total",
    "total_iteracoes",
    "iteracoes",
    "limite_profundidade",
    "motivo_falha",
}

CHAVES_ITERACAO = {
    "indice",
    "no_expandido",
    "caminho_expandido",
    "custo_acumulado",
    "profundidade",
    "prioridade_expandida",
    "heuristica_expandida",
    "fronteira",
}

CHAVES_ESTADO = {
    "no",
    "caminho",
    "custo",
    "profundidade",
    "prioridade",
    "heuristica",
}


class AlgoritmosFase2Tests(unittest.TestCase):
    def _assert_formato_resultado(self, resultado) -> None:
        self.assertEqual(set(resultado.keys()), CHAVES_RESULTADO)
        self.assertIsInstance(resultado["caminho_final"], tuple)
        self.assertIsInstance(resultado["iteracoes"], tuple)
        self.assertEqual(resultado["total_iteracoes"], len(resultado["iteracoes"]))

        for iteracao in resultado["iteracoes"]:
            self.assertEqual(set(iteracao.keys()), CHAVES_ITERACAO)
            self.assertIsInstance(iteracao["caminho_expandido"], tuple)
            self.assertIsInstance(iteracao["fronteira"], tuple)

            for estado in iteracao["fronteira"]:
                self.assertEqual(set(estado.keys()), CHAVES_ESTADO)
                self.assertIsInstance(estado["caminho"], tuple)

    def test_inicio_igual_objetivo_devolve_sucesso_imediato(self) -> None:
        resultados = [
            custo_uniforme(GRAFO, LISBOA, LISBOA),
            procura_sofrega(GRAFO, HEURISTICA_FARO, LISBOA, LISBOA),
            a_estrela(GRAFO, HEURISTICA_FARO, LISBOA, LISBOA),
            profundidade_limitada(GRAFO, LISBOA, LISBOA, 0),
        ]

        for resultado in resultados:
            self._assert_formato_resultado(resultado)
            self.assertTrue(resultado["encontrado"])
            self.assertEqual(resultado["caminho_final"], (LISBOA,))
            self.assertEqual(resultado["distancia_total"], 0)
            self.assertEqual(resultado["total_iteracoes"], 0)
            self.assertEqual(resultado["iteracoes"], ())
            self.assertIsNone(resultado["motivo_falha"])

    def test_custo_uniforme_encontra_caminho_otimo_para_faro(self) -> None:
        resultado = custo_uniforme(GRAFO, COIMBRA, FARO)

        self._assert_formato_resultado(resultado)
        self.assertEqual(resultado["algoritmo"], "custo_uniforme")
        self.assertTrue(resultado["encontrado"])
        self.assertEqual(
            resultado["caminho_final"],
            (COIMBRA, "Leiria", "Santarém", "Évora", "Beja", FARO),
        )
        self.assertEqual(resultado["distancia_total"], 484)
        self.assertIsNone(resultado["limite_profundidade"])

    def test_a_estrela_encontra_o_mesmo_caminho_otimo(self) -> None:
        resultado = a_estrela(GRAFO, HEURISTICA_FARO, COIMBRA, FARO)

        self._assert_formato_resultado(resultado)
        self.assertEqual(resultado["algoritmo"], "a_estrela")
        self.assertTrue(resultado["encontrado"])
        self.assertEqual(
            resultado["caminho_final"],
            (COIMBRA, "Leiria", "Santarém", "Évora", "Beja", FARO),
        )
        self.assertEqual(resultado["distancia_total"], 484)
        self.assertGreater(resultado["total_iteracoes"], 0)

    def test_procura_sofrega_devolve_caminho_heuristico_esperado(self) -> None:
        resultado = procura_sofrega(GRAFO, HEURISTICA_FARO, COIMBRA, FARO)

        self._assert_formato_resultado(resultado)
        self.assertEqual(resultado["algoritmo"], "procura_sofrega")
        self.assertTrue(resultado["encontrado"])
        self.assertEqual(
            resultado["caminho_final"],
            (COIMBRA, "Leiria", LISBOA, FARO),
        )
        self.assertEqual(resultado["distancia_total"], 495)

    def test_profundidade_limitada_respeita_limite_e_encontra_solucao(self) -> None:
        resultado = profundidade_limitada(GRAFO, COIMBRA, FARO, 3)

        self._assert_formato_resultado(resultado)
        self.assertEqual(resultado["algoritmo"], "profundidade_limitada")
        self.assertTrue(resultado["encontrado"])
        self.assertEqual(resultado["limite_profundidade"], 3)
        self.assertEqual(resultado["caminho_final"], (COIMBRA, "Leiria", LISBOA, FARO))
        self.assertEqual(resultado["distancia_total"], 495)

    def test_profundidade_limitada_devolve_falha_limpa(self) -> None:
        resultado = profundidade_limitada(GRAFO, BRAGA, FARO, 3)

        self._assert_formato_resultado(resultado)
        self.assertFalse(resultado["encontrado"])
        self.assertEqual(resultado["caminho_final"], ())
        self.assertIsNone(resultado["distancia_total"])
        self.assertEqual(resultado["limite_profundidade"], 3)
        self.assertEqual(
            resultado["motivo_falha"],
            "Objetivo nao encontrado dentro do limite de profundidade.",
        )

    def test_entradas_invalidas_geram_value_error(self) -> None:
        heuristica_incompleta = dict(HEURISTICA_FARO)
        heuristica_incompleta.pop(BEJA)

        with self.assertRaises(ValueError):
            custo_uniforme(GRAFO, "Cidade Inexistente", FARO)

        with self.assertRaises(ValueError):
            profundidade_limitada(GRAFO, COIMBRA, FARO, -1)

        with self.assertRaises(ValueError):
            procura_sofrega(GRAFO, heuristica_incompleta, COIMBRA, FARO)

        with self.assertRaises(ValueError):
            a_estrela(GRAFO, heuristica_incompleta, COIMBRA, FARO)


if __name__ == "__main__":
    unittest.main()
