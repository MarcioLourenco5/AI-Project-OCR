"""Utilitarios de OCR para leitura de matriculas por upload."""

from __future__ import annotations

import os
import re
import tempfile
from types import ModuleType
from typing import TypedDict

FORMAS_MATRICULA = ("LLDDLL", "DDLLDD", "DDDDLL", "LLDDDD")
MAPA_LETRAS = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "4": "A",
    "5": "S",
    "6": "G",
    "7": "T",
    "8": "B",
}
MAPA_DIGITOS = {
    "A": "4",
    "B": "8",
    "D": "0",
    "G": "6",
    "I": "1",
    "L": "1",
    "O": "0",
    "Q": "0",
    "S": "5",
    "T": "1",
    "U": "0",
    "Z": "2",
}


class ResultadoOCR(TypedDict):
    texto_bruto: str
    matricula_normalizada: str | None
    valida: bool
    motor: str
    erro: str | None


def _carregar_easyocr() -> ModuleType:
    try:
        import easyocr
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "EasyOCR nao esta instalado. Instale as dependencias para ativar o OCR."
        ) from exc

    return easyocr


def obter_status_motor_ocr() -> tuple[bool, str | None]:
    try:
        _carregar_easyocr()
    except ModuleNotFoundError as exc:
        return False, str(exc)

    return True, None


def _limpar_texto(texto: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", texto.upper())


def _normalizar_caractere(caractere: str, tipo: str) -> tuple[str | None, int]:
    if tipo == "L":
        normalizado = MAPA_LETRAS.get(caractere, caractere)
        if not normalizado.isalpha():
            return None, 0
        return normalizado, int(normalizado != caractere)

    normalizado = MAPA_DIGITOS.get(caractere, caractere)
    if not normalizado.isdigit():
        return None, 0
    return normalizado, int(normalizado != caractere)


def _formatar_matricula(caracteres: str) -> str:
    return f"{caracteres[:2]}-{caracteres[2:4]}-{caracteres[4:6]}"


def normalizar_matricula(texto: str) -> str | None:
    texto_limpo = _limpar_texto(texto)
    if len(texto_limpo) != 6:
        return None

    candidatos: list[tuple[int, int, str]] = []

    for ordem, padrao in enumerate(FORMAS_MATRICULA):
        caracteres_normalizados: list[str] = []
        substituicoes = 0

        for caractere, tipo in zip(texto_limpo, padrao, strict=True):
            normalizado, custo = _normalizar_caractere(caractere, tipo)
            if normalizado is None:
                break
            caracteres_normalizados.append(normalizado)
            substituicoes += custo
        else:
            candidatos.append(
                (substituicoes, ordem, _formatar_matricula("".join(caracteres_normalizados)))
            )

    if not candidatos:
        return None

    _, _, matricula = min(candidatos)
    return matricula


def validar_matricula(texto: str) -> bool:
    return normalizar_matricula(texto) is not None


def _extrair_texto_com_easyocr(imagem_bytes: bytes) -> list[str]:
    easyocr = _carregar_easyocr()
    caminho_temporario = ""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as ficheiro:
            ficheiro.write(imagem_bytes)
            caminho_temporario = ficheiro.name

        leitor = easyocr.Reader(["en"], gpu=False)
        texto_extraido = leitor.readtext(caminho_temporario, detail=0, paragraph=False)
        return [str(item) for item in texto_extraido]
    finally:
        if caminho_temporario and os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)


def ler_matricula_de_upload(imagem_bytes: bytes) -> ResultadoOCR:
    if not imagem_bytes:
        return {
            "texto_bruto": "",
            "matricula_normalizada": None,
            "valida": False,
            "motor": "easyocr",
            "erro": "Nenhuma imagem foi enviada para OCR.",
        }

    try:
        fragmentos = _extrair_texto_com_easyocr(imagem_bytes)
    except ModuleNotFoundError as exc:
        return {
            "texto_bruto": "",
            "matricula_normalizada": None,
            "valida": False,
            "motor": "easyocr",
            "erro": str(exc),
        }
    except Exception as exc:  # pragma: no cover - protecao de runtime
        return {
            "texto_bruto": "",
            "matricula_normalizada": None,
            "valida": False,
            "motor": "easyocr",
            "erro": f"Falha ao processar a imagem com OCR: {exc}",
        }

    texto_bruto = " ".join(fragmentos).strip()
    matricula = normalizar_matricula(texto_bruto)

    return {
        "texto_bruto": texto_bruto,
        "matricula_normalizada": matricula,
        "valida": matricula is not None,
        "motor": "easyocr",
        "erro": None if matricula else "Nao foi possivel identificar uma matricula valida.",
    }


__all__ = [
    "ResultadoOCR",
    "ler_matricula_de_upload",
    "normalizar_matricula",
    "obter_status_motor_ocr",
    "validar_matricula",
]
