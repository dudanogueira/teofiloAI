# 🤖 Automação com Python: navegador e desktop

Aula de **2 horas** para iniciantes. Notebook: [`aula_automacao.ipynb`](aula_automacao.ipynb).

- **Parte A — Selenium:** controlar o navegador, localizadores, formulários, esperas e testes
  automatizados com **pytest** e **Page Object**, num site de treino local.
- **Parte B — Interface do sistema:** mouse, teclado e capturas com **pyautogui**; janelas e
  controles "por dentro" com **pywinauto** (Windows) e **AppleScript** (Mac); fecha com um robô
  que lê um CSV e escreve um relatório no editor de texto.

## Preparação (faça antes da aula)

### 1. Python e bibliotecas

```bash
cd aulas/automacao
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac
pip install -r requirements.txt
jupyter notebook aula_automacao.ipynb
```

O `requirements.txt` só instala o `pywinauto` no Windows. A primeira célula do notebook faz a
mesma escolha sozinha.

### 2. Navegador

| | Padrão do notebook | Observação |
|---|---|---|
| 🪟 Windows | **Edge** (já vem instalado) | |
| 🍎 Mac | **Chrome** | Sem Chrome, o Selenium Manager baixa um "Chrome for Testing" sozinho. Para usar **Safari**, rode uma vez `safaridriver --enable` no Terminal. |

Não é preciso baixar `chromedriver`: o **Selenium Manager** (Selenium 4.11+) cuida disso. Na
primeira execução ele baixa o driver, então a máquina precisa de internet.

### 3. Permissões no Mac (Parte B)

Em **Ajustes do Sistema → Privacidade e Segurança**, ative o programa que roda o notebook
(Terminal, VS Code, iTerm...) em:

| Permissão | Para quê | Sem ela |
|---|---|---|
| **Acessibilidade** | `pyautogui` mover o mouse e digitar; System Events ler janelas | o mouse não se mexe, ou erro `-1719` |
| **Gravação de Tela** | `pyautogui.screenshot()` | erro, ou imagem só com o papel de parede |
| **Automação** | AppleScript controlar o TextEdit | o macOS pergunta na hora; responda **OK** |

Depois de ativar, **feche e abra de novo** o programa. No Windows não há nada a configurar.

## Roteiro

| Parte | Assunto | Tempo |
|---|---|---|
| 0 | Instalação e pastas | 10 min |
| A.1–A.3 | O que é Selenium; site de treino local; abrir o navegador | 10 min |
| A.4–A.7 | Localizadores, digitar e clicar, formulários, ler tabela | 20 min |
| A.8 | Esperas explícitas × `time.sleep` · 🎯 Exercício A1 | 15 min |
| A.9 | De script a teste: `assert`, pytest, fixtures, Page Object · 🎯 A2 e A3 | 20 min |
| B.1 | `pyautogui`: freio de emergência, mouse, captura, teclado | 15 min |
| B.2 | Árvore de acessibilidade: `pywinauto` (Bloco de Notas, Calculadora) e AppleScript (TextEdit, System Events) | 20 min |
| B.3 | Juntando tudo: CSV → relatório escrito no editor e conferido · 🎯 B1 | 10 min |

## Arquivos

```
automacao/
├── aula_automacao.ipynb
├── requirements.txt
├── diagramas/              ← SVGs usados no notebook
├── site_teste/index.html   ← a "Loja Teste": login, formulário, tabela, botão lento
├── testes/
│   ├── conftest.py         ← fixtures: servidor do site + navegador
│   └── test_site.py        ← 7 testes + Page Object
├── dados/vendas.csv        ← entrada do robô da Parte B
└── saida/                  ← criada pelo notebook (screenshots, relatórios); fora do git
```

Login da Loja Teste: **`aluno`** / **`selenium123`**.

Os testes rodam também fora do notebook:

```bash
python -m pytest testes -v                       # headless, navegador padrão do sistema
HEADLESS=0 NAVEGADOR=firefox python -m pytest testes -v           # Mac: com janela, Firefox
$env:HEADLESS="0"; python -m pytest testes -v                     # Windows (PowerShell)
```

## Avisos para quem dá a aula

- Nas células do `pyautogui`, **o mouse e o teclado são do script**. Avise a turma para não
  clicar em nada enquanto a célula roda; mouse num **canto da tela** interrompe tudo (`FAILSAFE`).
- O `pyautogui.write()` não digita acentos: o notebook mostra o truque de colar pela área de
  transferência. O `pywinauto` e o AppleScript não têm esse problema.
- No Windows 11, o Bloco de Notas abre arquivos em **abas**. O notebook acha a janela pelo nome do
  arquivo, então funciona mesmo com outras abas abertas.
- Nomes de botões e menus mudam com o **idioma do sistema**. Por isso a Calculadora é controlada
  pelo `auto_id` e o TextEdit pelo dicionário AppleScript, que não mudam.

## Status de validação

| | macOS (Apple Silicon) | Windows |
|---|---|---|
| Parte A (Chrome headless) | ✅ todas as células | não executado |
| `pytest testes` | ✅ 7/7 | não executado |
| B.1 `pyautogui` | ✅ tamanho da tela e tratamento da falta de permissão; mouse e digitação **não** executados (tomariam a tela de quem validou) | não executado |
| B.2 / B.3 AppleScript | ✅ TextEdit escreve e salva; relatório conferido com `assert` | — |
| B.2 / B.3 `pywinauto` | — | **não executado**: escrito pela API atual (`Desktop(backend="uia")`, `auto_id` da Calculadora) e revisado, mas precisa de um teste numa máquina Windows antes da aula |
