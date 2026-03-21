"""Aplicacao Streamlit para demonstracao do trabalho."""

from __future__ import annotations

from typing import Any

try:
    import streamlit as st
except ModuleNotFoundError:  # pragma: no cover - o ambiente de testes nao tem Streamlit
    st = None

from algoritmos import (
    ResultadoProcura,
    a_estrela,
    custo_uniforme,
    profundidade_limitada,
    procura_sofrega,
)
from dados import CIDADES, FARO, GRAFO, HEURISTICA_FARO
from llm import obter_atracoes, verificar_disponibilidade_ollama
from ocr import ler_matricula_de_upload, obter_status_motor_ocr

DESTINO_DEMONSTRACAO = FARO
ALGORITMOS_DISPONIVEIS = (
    "Custo Uniforme",
    "Profundidade Limitada",
    "Procura Sôfrega",
    "A*",
)


def executar_procura(
    algoritmo: str,
    origem: str,
    limite: int | None = None,
) -> ResultadoProcura:
    if algoritmo == "Custo Uniforme":
        return custo_uniforme(GRAFO, origem, DESTINO_DEMONSTRACAO)
    if algoritmo == "Profundidade Limitada":
        if limite is None:
            raise ValueError("O algoritmo de profundidade limitada exige um limite.")
        return profundidade_limitada(GRAFO, origem, DESTINO_DEMONSTRACAO, limite)
    if algoritmo == "Procura Sôfrega":
        return procura_sofrega(GRAFO, HEURISTICA_FARO, origem, DESTINO_DEMONSTRACAO)
    if algoritmo == "A*":
        return a_estrela(GRAFO, HEURISTICA_FARO, origem, DESTINO_DEMONSTRACAO)

    raise ValueError(f"Algoritmo desconhecido: {algoritmo}")


def _resultado_para_tabela(resultado: ResultadoProcura) -> list[dict[str, Any]]:
    tabela: list[dict[str, Any]] = []
    for iteracao in resultado["iteracoes"]:
        fronteira = " | ".join(
            f"{estado['no']} ({estado['custo']})" for estado in iteracao["fronteira"]
        )
        tabela.append(
            {
                "Iteracao": iteracao["indice"],
                "No Expandido": iteracao["no_expandido"],
                "Caminho": " -> ".join(iteracao["caminho_expandido"]),
                "Custo": iteracao["custo_acumulado"],
                "Profundidade": iteracao["profundidade"],
                "Prioridade": iteracao["prioridade_expandida"],
                "Heuristica": iteracao["heuristica_expandida"],
                "Fronteira": fronteira,
            }
        )
    return tabela


def render_app() -> None:
    if st is None:
        raise RuntimeError(
            "Streamlit nao esta instalado. Instale as dependencias e execute "
            "`streamlit run main.py`."
        )

    st.set_page_config(page_title="Painel de Frota Turistica", layout="wide")
    st.title("Painel de Frota Turistica")
    st.caption(
        "Login por OCR da matricula, procura de rotas para Faro e resumo "
        "turistico com LLM local."
    )

    ocr_disponivel, ocr_erro = obter_status_motor_ocr()
    ollama_disponivel, ollama_erro = verificar_disponibilidade_ollama(timeout=0.5)

    if not ocr_disponivel:
        st.warning(f"OCR indisponivel neste ambiente: {ocr_erro}")
    if not ollama_disponivel:
        st.warning(f"LLM local indisponivel neste ambiente: {ollama_erro}")

    st.subheader("Login por OCR")
    imagem = st.file_uploader(
        "Faz upload de uma imagem com a matricula do veiculo",
        type=["png", "jpg", "jpeg"],
    )

    if imagem is not None:
        resultado_ocr = ler_matricula_de_upload(imagem.getvalue())
        if resultado_ocr["texto_bruto"]:
            st.write(f"Texto OCR: `{resultado_ocr['texto_bruto']}`")
        if resultado_ocr["valida"]:
            st.success(
                f"Matricula validada: `{resultado_ocr['matricula_normalizada']}` "
                f"via {resultado_ocr['motor']}"
            )
        else:
            st.error(resultado_ocr["erro"] or "Nao foi possivel validar a matricula.")

    st.subheader("Procura de Rotas")
    col_origem, col_destino, col_algoritmo = st.columns(3)

    with col_origem:
        origem = st.selectbox("Cidade de origem", CIDADES, index=0)
    with col_destino:
        st.text_input("Destino", value=DESTINO_DEMONSTRACAO, disabled=True)
    with col_algoritmo:
        algoritmo = st.selectbox("Algoritmo", ALGORITMOS_DISPONIVEIS)

    limite = None
    if algoritmo == "Profundidade Limitada":
        limite = int(
            st.number_input(
                "Limite de profundidade",
                min_value=0,
                value=3,
                step=1,
            )
        )

    if st.button("Calcular percurso", type="primary"):
        try:
            resultado = executar_procura(algoritmo, origem, limite)
        except ValueError as exc:
            st.error(str(exc))
            return

        st.write(
            f"Algoritmo executado: `{resultado['algoritmo']}` | "
            f"Iteracoes: `{resultado['total_iteracoes']}`"
        )

        if resultado["encontrado"]:
            st.success(
                "Caminho encontrado: "
                + " -> ".join(resultado["caminho_final"])
            )
            st.metric("Distancia Total", f"{resultado['distancia_total']} km")
        else:
            st.error(resultado["motivo_falha"] or "Nao foi possivel encontrar um caminho.")

        with st.expander("Iteracoes da procura", expanded=True):
            st.dataframe(_resultado_para_tabela(resultado), use_container_width=True)

        if resultado["encontrado"]:
            st.subheader("Atracoes Turisticas")
            if not ollama_disponivel:
                st.info(
                    "O percurso foi calculado, mas o Ollama nao esta disponivel "
                    "para gerar as atracoes turisticas."
                )
            else:
                for cidade in resultado["caminho_final"]:
                    resposta = obter_atracoes(cidade)
                    if resposta["disponivel"]:
                        st.markdown(f"**{cidade}**")
                        for atracao in resposta["atracoes"]:
                            st.write(f"- {atracao}")
                    else:
                        st.info(f"{cidade}: {resposta['erro']}")


if __name__ == "__main__":
    if st is None:
        print(
            "Streamlit nao esta instalado. Instale as dependencias e execute "
            "`streamlit run main.py`."
        )
    else:
        render_app()
