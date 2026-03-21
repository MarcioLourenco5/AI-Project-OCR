
## Resumo
- O projeto ja tem as Fases 1 e 2 implementadas e testadas.
- As Fases 3, 4 e 5 ficaram com uma implementacao inicial, mas o ambiente atual ainda nao tem as dependencias externas necessarias para executar OCR real, UI Streamlit e LLM local.
- Neste momento, a base do dominio, os algoritmos de procura, o OCR por upload, a integracao com Ollama e a orquestracao da UI ja existem em codigo.

## Estado Atual
### Ja implementado
- `dados.py`
  - Cidades canonicas, grafo bidirecional, heuristica para Faro e validacao tipada.
- `algoritmos.py`
  - `custo_uniforme`, `profundidade_limitada`, `procura_sofrega` e `a_estrela`.
  - Contrato uniforme de saida com rastreio por iteracao.
- `ocr.py`
  - OCR apenas por upload.
  - Validacao das matriculas nos 4 formatos classicos: `AA-00-AA`, `00-AA-00`, `00-00-AA`, `AA-00-00`.
  - Normalizacao de ruido tipico de OCR.
  - Fallback quando o `EasyOCR` nao esta instalado.
- `llm.py`
  - Integracao com Ollama por HTTP usando `urllib.request`.
  - Parsing de 3 atracoes resumidas por cidade.
  - Tratamento elegante de indisponibilidade, timeout e resposta malformada.
- `main.py`
  - Aplicacao Streamlit ja estruturada.
  - Upload da imagem, execucao dos algoritmos, destino fixo em Faro, limite para profundidade limitada e area para atracoes turisticas.
  - Importavel mesmo sem `streamlit` instalado.

### Estado dos testes
- No arranque desta etapa havia 12 testes a passar.
- Depois desta implementacao existem 22 testes automatizados a passar.
- Comando validado:

```bash
python3 -m unittest discover -v
```

## Dependencias Externas
### Ausentes no ambiente atual
- `streamlit`
- `easyocr`
- `pillow`
- `ollama`
- `cv2`
- `pytesseract`
- binario `tesseract`

### Manifesto do projeto
- O ficheiro [requirements.txt](/home/abner/code/uni/ia/AI-Project-OCR/requirements.txt) inclui:
  - `streamlit`
  - `easyocr`
  - `pillow`

### Observacoes
- `opencv-python`, `pytesseract` e `tesseract` nao fazem parte do caminho principal desta versao.
- O Ollama nao e uma dependencia Python do `requirements.txt`; deve ser instalado separadamente na maquina.

## Como Validar
### Validacao automatica

```bash
python3 -m py_compile dados.py algoritmos.py ocr.py llm.py main.py tests/test_dados.py tests/test_algoritmos.py tests/test_ocr.py tests/test_llm.py tests/test_main.py
python3 -m unittest discover -v
```

### Validacao manual depois de instalar dependencias
1. Instalar as dependencias Python:

```bash
pip install -r requirements.txt
```

2. Instalar e arrancar o Ollama localmente.
3. Fazer download de um modelo leve, por exemplo `llama3:8b`.
4. Iniciar a app:

```bash
streamlit run main.py
```

5. Testar o fluxo:
- fazer upload de uma imagem com matricula
- confirmar se o OCR devolve uma matricula valida
- escolher a cidade de origem
- manter `Faro` como destino
- selecionar o algoritmo
- definir o limite se o algoritmo for profundidade limitada
- verificar caminho final, distancia e iteracoes
- verificar as atracoes turisticas geradas por cidade

## Como as Proximas Fases Foram Implementadas
### Fase 3 - OCR
- Implementada com `upload` apenas.
- O backend principal e `EasyOCR`, carregado de forma tardia.
- Quando o backend nao existe, a funcao devolve erro em vez de crash.

### Fase 4 - LLM
- Implementada com Ollama local via HTTP.
- O codigo pede exatamente 3 atracoes resumidas.
- Se o Ollama nao estiver disponivel, o modulo devolve um resultado controlado com erro explicito.

### Fase 5 - Interface
- A UI principal esta em `main.py`.
- O destino de demonstracao continua fixo em `Faro`.
- A app usa diretamente os contratos publicos de `dados.py`, `algoritmos.py`, `ocr.py` e `llm.py`.

## Proximos Passos Recomendados
- Instalar `streamlit`, `easyocr` e `pillow`.
- Instalar e configurar o Ollama com um modelo local.
- Fazer um teste manual ponta a ponta com uma imagem real de matricula.
- Refinar o layout da interface para a apresentacao final.
- Adicionar testes de interface mais proximos do uso real quando o ambiente de UI estiver pronto.
