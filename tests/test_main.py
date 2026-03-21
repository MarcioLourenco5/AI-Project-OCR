import importlib
import unittest

from dados import FARO


class MainTests(unittest.TestCase):
    def test_main_e_importavel_e_expoe_o_fluxo_principal(self) -> None:
        main = importlib.import_module("main")

        self.assertTrue(callable(main.render_app))
        self.assertEqual(main.DESTINO_DEMONSTRACAO, FARO)
        self.assertIn("Custo Uniforme", main.ALGORITMOS_DISPONIVEIS)

        resultado = main.executar_procura("Custo Uniforme", "Coimbra")
        self.assertTrue(resultado["encontrado"])
        self.assertEqual(resultado["objetivo"], FARO)


if __name__ == "__main__":
    unittest.main()
