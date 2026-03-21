"""Integracao com um LLM local via Ollama."""

from __future__ import annotations

import json
import os
import re
from typing import TypedDict
from urllib import error, request

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b")


class ResultadoLLM(TypedDict):
    cidade: str
    atracoes: list[str]
    resposta_bruta: str
    disponivel: bool
    erro: str | None


def _montar_prompt(cidade: str) -> str:
    return (
        f"Diz-me de forma muito resumida quais sao as 3 principais atracoes "
        f"turisticas de {cidade}. Responde exatamente com 3 linhas, uma atracao "
        "por linha, sem introducao nem conclusao."
    )


def _limpar_linha_atracao(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r"^[-*•]+\s*", "", texto)
    texto = re.sub(r"^\d+[\).\-\:]*\s*", "", texto)
    return texto.strip(" -")


def _extrair_atracoes(texto: str) -> list[str]:
    candidatos = [_limpar_linha_atracao(linha) for linha in texto.splitlines()]
    candidatos = [linha for linha in candidatos if linha]

    if len(candidatos) < 3:
        segmentos = [
            _limpar_linha_atracao(segmento)
            for segmento in re.split(r"[;\n]+", texto)
        ]
        candidatos = [segmento for segmento in segmentos if segmento]

    if len(candidatos) < 3:
        frases = [
            _limpar_linha_atracao(frase)
            for frase in re.split(r"(?<=[\.\!\?])\s+", texto)
        ]
        candidatos = [frase.rstrip(".") for frase in frases if frase]

    if len(candidatos) < 3:
        return []

    return candidatos[:3]


def verificar_disponibilidade_ollama(timeout: float = 1.0) -> tuple[bool, str | None]:
    url = f"{OLLAMA_BASE_URL}/api/tags"
    pedido = request.Request(url, method="GET")

    try:
        with request.urlopen(pedido, timeout=timeout):
            return True, None
    except error.URLError as exc:
        return False, f"Ollama indisponivel em {OLLAMA_BASE_URL}: {exc.reason}"
    except TimeoutError:
        return False, f"Ollama indisponivel em {OLLAMA_BASE_URL}: timeout."
    except Exception as exc:  # pragma: no cover - protecao de runtime
        return False, f"Ollama indisponivel em {OLLAMA_BASE_URL}: {exc}"


def obter_atracoes(cidade: str, timeout: float = 10.0) -> ResultadoLLM:
    if not cidade.strip():
        raise ValueError("A cidade nao pode ser vazia.")

    corpo = {
        "model": OLLAMA_MODEL,
        "prompt": _montar_prompt(cidade),
        "stream": False,
    }
    dados = json.dumps(corpo).encode("utf-8")
    pedido = request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=dados,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(pedido, timeout=timeout) as resposta_http:
            resposta_bruta = resposta_http.read().decode("utf-8")
    except error.URLError as exc:
        return {
            "cidade": cidade,
            "atracoes": [],
            "resposta_bruta": "",
            "disponivel": False,
            "erro": f"Nao foi possivel contactar o Ollama: {exc.reason}",
        }
    except TimeoutError:
        return {
            "cidade": cidade,
            "atracoes": [],
            "resposta_bruta": "",
            "disponivel": False,
            "erro": "O pedido ao Ollama excedeu o tempo limite.",
        }
    except Exception as exc:  # pragma: no cover - protecao de runtime
        return {
            "cidade": cidade,
            "atracoes": [],
            "resposta_bruta": "",
            "disponivel": False,
            "erro": f"Falha inesperada ao consultar o Ollama: {exc}",
        }

    try:
        resposta_json = json.loads(resposta_bruta)
    except json.JSONDecodeError:
        return {
            "cidade": cidade,
            "atracoes": [],
            "resposta_bruta": resposta_bruta,
            "disponivel": False,
            "erro": "O Ollama devolveu uma resposta que nao e JSON valido.",
        }

    texto_resposta = resposta_json.get("response")
    if not isinstance(texto_resposta, str):
        return {
            "cidade": cidade,
            "atracoes": [],
            "resposta_bruta": resposta_bruta,
            "disponivel": False,
            "erro": "A resposta do Ollama nao contem o campo 'response' esperado.",
        }

    atracoes = _extrair_atracoes(texto_resposta)
    if len(atracoes) != 3:
        return {
            "cidade": cidade,
            "atracoes": [],
            "resposta_bruta": texto_resposta,
            "disponivel": False,
            "erro": "Nao foi possivel extrair exatamente 3 atracoes da resposta do LLM.",
        }

    return {
        "cidade": cidade,
        "atracoes": atracoes,
        "resposta_bruta": texto_resposta,
        "disponivel": True,
        "erro": None,
    }


__all__ = [
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "ResultadoLLM",
    "obter_atracoes",
    "verificar_disponibilidade_ollama",
]
