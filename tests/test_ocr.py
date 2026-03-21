import unittest
from unittest.mock import patch

import ocr


class FakeEasyOCR:
    class Reader:
        def __init__(self, languages, gpu=False):
            self.languages = languages
            self.gpu = gpu

        def readtext(self, path, detail=0, paragraph=False):
            return ["aa 00 aa"]


class OCRTests(unittest.TestCase):
    def test_valida_os_quatro_formatos_classicos(self) -> None:
        matriculas = ("AA-00-AA", "00-AA-00", "00-00-AA", "AA-00-00")

        for matricula in matriculas:
            with self.subTest(matricula=matricula):
                self.assertTrue(ocr.validar_matricula(matricula))
                self.assertEqual(ocr.normalizar_matricula(matricula), matricula)

    def test_normaliza_ruido_tipico_de_ocr(self) -> None:
        self.assertEqual(ocr.normalizar_matricula(" aa 00 aa "), "AA-00-AA")
        self.assertEqual(ocr.normalizar_matricula("12ab34"), "12-AB-34")
        self.assertEqual(ocr.normalizar_matricula("ab0000"), "AB-00-00")

    def test_rejeita_textos_invalidos(self) -> None:
        invalidos = ("", "ABC1234", "WXYZJK", "12CDXY", "###")

        for texto in invalidos:
            with self.subTest(texto=texto):
                self.assertFalse(ocr.validar_matricula(texto))
                self.assertIsNone(ocr.normalizar_matricula(texto))

    def test_ler_matricula_de_upload_faz_fallback_quando_easyocr_falta(self) -> None:
        with patch(
            "ocr._carregar_easyocr",
            side_effect=ModuleNotFoundError("EasyOCR nao esta instalado."),
        ):
            resultado = ocr.ler_matricula_de_upload(b"imagem")

        self.assertFalse(resultado["valida"])
        self.assertIsNone(resultado["matricula_normalizada"])
        self.assertEqual(resultado["motor"], "easyocr")
        self.assertIn("EasyOCR", resultado["erro"] or "")

    def test_ler_matricula_de_upload_normaliza_resultado_quando_ocr_funciona(self) -> None:
        with patch("ocr._carregar_easyocr", return_value=FakeEasyOCR):
            resultado = ocr.ler_matricula_de_upload(b"imagem")

        self.assertTrue(resultado["valida"])
        self.assertEqual(resultado["matricula_normalizada"], "AA-00-AA")
        self.assertEqual(resultado["texto_bruto"], "aa 00 aa")
        self.assertIsNone(resultado["erro"])


if __name__ == "__main__":
    unittest.main()
