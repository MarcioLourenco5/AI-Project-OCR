import json
import unittest
from unittest.mock import patch
from urllib import error

import llm


class FakeHTTPResponse:
    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class LLMTests(unittest.TestCase):
    def test_obter_atracoes_com_sucesso(self) -> None:
        resposta = {
            "response": "- Universidade de Coimbra\n- Biblioteca Joanina\n- Se Velha"
        }

        with patch("llm.request.urlopen", return_value=FakeHTTPResponse(json.dumps(resposta))):
            resultado = llm.obter_atracoes("Coimbra")

        self.assertTrue(resultado["disponivel"])
        self.assertEqual(resultado["cidade"], "Coimbra")
        self.assertEqual(
            resultado["atracoes"],
            ["Universidade de Coimbra", "Biblioteca Joanina", "Se Velha"],
        )
        self.assertIsNone(resultado["erro"])

    def test_obter_atracoes_trata_erro_de_ligacao(self) -> None:
        with patch(
            "llm.request.urlopen",
            side_effect=error.URLError("connection refused"),
        ):
            resultado = llm.obter_atracoes("Coimbra", timeout=0.1)

        self.assertFalse(resultado["disponivel"])
        self.assertEqual(resultado["atracoes"], [])
        self.assertIn("Nao foi possivel contactar o Ollama", resultado["erro"] or "")

    def test_obter_atracoes_trata_resposta_malformada(self) -> None:
        resposta = {"unexpected": "missing response field"}

        with patch("llm.request.urlopen", return_value=FakeHTTPResponse(json.dumps(resposta))):
            resultado = llm.obter_atracoes("Coimbra")

        self.assertFalse(resultado["disponivel"])
        self.assertEqual(resultado["atracoes"], [])
        self.assertIn("campo 'response'", resultado["erro"] or "")

    def test_obter_atracoes_rejeita_resposta_sem_tres_atracoes(self) -> None:
        resposta = {"response": "- Universidade de Coimbra\n- Biblioteca Joanina"}

        with patch("llm.request.urlopen", return_value=FakeHTTPResponse(json.dumps(resposta))):
            resultado = llm.obter_atracoes("Coimbra")

        self.assertFalse(resultado["disponivel"])
        self.assertEqual(resultado["atracoes"], [])
        self.assertIn("3 atracoes", resultado["erro"] or "")


if __name__ == "__main__":
    unittest.main()
