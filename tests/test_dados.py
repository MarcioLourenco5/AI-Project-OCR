import unittest

import dados


class DadosFase1Tests(unittest.TestCase):
    def test_total_de_cidades_e_ligacoes(self) -> None:
        self.assertEqual(len(dados.CIDADES), 18)
        self.assertEqual(dados.VALIDACAO_DADOS["total_cidades"], 18)
        self.assertEqual(dados.VALIDACAO_DADOS["total_ligacoes_nao_direcionadas"], 34)

    def test_grafo_e_totalmente_simetrico(self) -> None:
        for origem, vizinhos in dados.GRAFO.items():
            for destino, distancia in vizinhos.items():
                self.assertIn(destino, dados.GRAFO)
                self.assertIn(origem, dados.GRAFO[destino])
                self.assertEqual(dados.GRAFO[destino][origem], distancia)

    def test_heuristica_cobre_as_mesmas_cidades_do_grafo(self) -> None:
        cidades = set(dados.CIDADES)
        self.assertEqual(cidades, set(dados.GRAFO))
        self.assertEqual(cidades, set(dados.HEURISTICA_FARO))
        self.assertEqual(dados.HEURISTICA_FARO[dados.FARO], 0)

    def test_arestas_criticas_do_enunciado(self) -> None:
        self.assertEqual(dados.GRAFO[dados.AVEIRO][dados.PORTO], 68)
        self.assertEqual(dados.GRAFO[dados.PORTO][dados.AVEIRO], 68)

        self.assertEqual(dados.GRAFO[dados.CASTELO_BRANCO][dados.COIMBRA], 159)
        self.assertEqual(dados.GRAFO[dados.COIMBRA][dados.CASTELO_BRANCO], 159)

        self.assertEqual(dados.GRAFO[dados.LISBOA][dados.SETUBAL], 50)
        self.assertEqual(dados.GRAFO[dados.SETUBAL][dados.LISBOA], 50)

    def test_validacao_nao_reporta_problemas(self) -> None:
        self.assertEqual(dados.VALIDACAO_DADOS["cidades_orfas"], ())
        self.assertEqual(dados.VALIDACAO_DADOS["arestas_assimetricas"], ())
        self.assertEqual(dados.VALIDACAO_DADOS["cidades_canonicas_sem_heuristica"], ())
        self.assertEqual(dados.VALIDACAO_DADOS["cidades_heuristica_nao_canonicas"], ())


if __name__ == "__main__":
    unittest.main()
