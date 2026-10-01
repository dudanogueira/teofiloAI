# Aulas

Mini cursos de **2 horas**, em notebooks Jupyter, para iniciantes. Cada aula está numa pasta
própria com o notebook, os arquivos de exemplo e um `README.md` com a preparação.
Tudo funciona em **Windows e Mac**.

| Aula | O que se aprende | Precisa de |
|---|---|---|
| [🐳 Docker do zero](docker/) | imagens, contêineres, portas, volumes, `Dockerfile`, redes, Docker Compose e o SDK de Python | Docker Desktop |
| [🤖 Automação com Python](automacao/) | Selenium, esperas, testes com pytest e Page Object; mouse e teclado com `pyautogui`; janelas com `pywinauto` (Windows) e AppleScript (Mac) | um navegador |

A aula de Docker é uma boa preparação para a [versão local](../curso_agente_leis_local_docker.ipynb)
e a [versão n8n](../n8n/) do curso principal, que sobem o Weaviate num contêiner.

## Como abrir um notebook

```bash
cd aulas/docker                      # ou aulas/automacao
python -m venv .venv
.venv\Scripts\activate               # Windows (PowerShell ou cmd)
source .venv/bin/activate            # Mac
pip install -r requirements.txt
jupyter notebook                     # ou abra o .ipynb no VS Code
```

> ⚠️ Abra o Jupyter **de dentro da pasta da aula**: os notebooks procuram os arquivos de
> exemplo a partir da pasta atual. No VS Code isso já acontece sozinho.
