# Mini curso: Agente de IA para a legislação de Teófilo Otoni

Notebook de 2 horas que ensina **Python + LangChain + Weaviate** construindo um agente
que responde perguntas sobre as leis do município de Teófilo Otoni/MG, citando a fonte.

## Escolha a sua versão

O curso existe em **duas versões com o mesmo conteúdo**. Mudam 6 células de código (de 54) — o resto
(coleta, parsing, chunking, schema, busca, tools, agente, memória) é idêntico, de propósito:
a arquitetura não depende do fornecedor.

| | ☁️ Nuvem | 🐳 Local |
|---|---|---|
| **Notebook** | [`curso_agente_leis_teofilo_otoni.ipynb`](curso_agente_leis_teofilo_otoni.ipynb) | [`curso_agente_leis_local_docker.ipynb`](curso_agente_leis_local_docker.ipynb) |
| Onde roda | Google Colab (navegador) | sua máquina (Jupyter/VS Code) |
| Banco vetorial | Weaviate Cloud | contêiner Docker |
| Embeddings | Weaviate Embeddings (inclusos) | OpenAI ou Cohere (sua chave) |
| LLM | Google Gemini | OpenAI ou Cohere |
| Instalar nada? | não | Docker + venv |
| Custo | grátis | grátis com Cohere trial; centavos com OpenAI |
| Limites | 1 coleção, 3 tenants (plano Free) | os do seu disco |

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dudanogueira/teofiloAI/blob/main/curso_agente_leis_teofilo_otoni.ipynb)

**Para uma turma, use a versão nuvem**: ninguém instala nada e todo mundo começa junto.
A versão local serve para quem quer o dado na própria máquina, não pode usar Colab, ou
quer ver como se sobe a infra de verdade.

---

# ☁️ Versão nuvem (Colab + Gemini)

## Preparação (faça antes da aula)

### 1. Weaviate Cloud — um cluster por aluno

Cada participante cria o seu cluster grátis em
[console.weaviate.cloud](https://console.weaviate.cloud) e anota **URL** e **API key**.

> ⚠️ **O plano Free permite 1 coleção e 3 tenants por cluster.**
> O notebook usa exatamente 1 coleção e 2 tenants, então cabe — mas **a turma não
> consegue compartilhar um cluster**. Criar um leva ~2 min e não pede cartão.

Não é preciso chave de embeddings: o Weaviate Cloud já inclui o **Weaviate Embeddings**
(modelo multilíngue, bom em português).

### 2. Google Gemini

Pegue uma chave grátis em [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

> ⚠️ **Duas armadilhas, ambas tratadas pelo notebook:**
>
> 1. **`gemini-2.5-flash` responde `404` para chaves novas.** O notebook testa uma lista de
>    modelos e usa o primeiro que responder.
> 2. **A cota grátis varia muito por modelo.** `gemini-3.6-flash` tem apenas
>    **~20 requisições/dia** no free tier — e cada pergunta ao agente gasta 2 ou mais.
>    Por isso a lista `CANDIDATOS` **começa pelos modelos `-lite`**
>    (`gemini-3.5-flash-lite`), que têm cota muito maior e roteiam igualmente bem
>    nesta tarefa. Testado: acerto em 5/5 perguntas de roteamento.
>
> Se aparecer `RESOURCE_EXHAUSTED`, espere alguns minutos ou reordene `CANDIDATOS`.

### 3. Segredos no Colab

No ícone 🔑 da barra lateral, crie três segredos e **ative "Acesso ao notebook"** em cada:

| Nome | Valor |
|---|---|
| `WEAVIATE_URL` | endereço do cluster, sem `https://` |
| `WEAVIATE_API_KEY` | API key do cluster |
| `GEMINI_API_KEY` | chave do Google AI Studio |

Fora do Colab, o notebook lê variáveis de ambiente com os mesmos nomes, ou pergunta via `getpass`.

---

# 🐳 Versão local (Docker + OpenAI ou Cohere)

## Preparação

### 1. Subir o Weaviate

Precisa de [Docker](https://docs.docker.com/get-docker/) instalado. Na pasta do projeto:

```bash
docker compose up -d
docker compose ps        # weaviate-curso deve aparecer como "running (healthy)"
```

O [`docker-compose.yml`](docker-compose.yml) sobe o Weaviate 1.39.5 em `localhost:8080`
(REST) e `localhost:50051` (gRPC), com `ENABLE_API_BASED_MODULES=true` — é o que liga os
módulos `text2vec-openai` e `text2vec-cohere`. Os dados ficam no volume `weaviate_data`.

Comandos úteis:

| | |
|---|---|
| `docker compose stop` | para o contêiner, **mantendo** os dados |
| `docker compose up -d` | sobe de novo |
| `docker compose logs -f weaviate` | acompanha o log |
| `docker compose down -v` | apaga tudo, inclusive os dados |

### 2. Escolher o provedor e pôr a chave no `.env`

```bash
cp .env.example .env     # depois edite e cole a sua chave
```

| Provedor | Chave | Custo | Modelo de embeddings |
|---|---|---|---|
| **Cohere** (recomendado) | [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys) | **trial gratuita**, limite por minuto | `embed-multilingual-v3.0` |
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | pré-pago; esta aula custa < US$ 0,01 | `text-embedding-3-small` |

Trocar de provedor é mudar `PROVEDOR=cohere` para `PROVEDOR=openai` no `.env`. **Uma linha**:
ela define ao mesmo tempo quem vetoriza e quem responde.

> ⚠️ O vetorizador fica **congelado** no momento em que a coleção é criada. Se você trocar
> de provedor depois de importar, a célula 4.3 avisa e diz o que fazer
> (`client.collections.delete("Legislacao")` e reimportar).

A chave **não fica no `docker-compose.yml`**: o notebook a envia em cada requisição, no
header `X-Cohere-Api-Key` / `X-OpenAI-Api-Key`. O Weaviate não a armazena.

### 3. Ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install jupyterlab           # ou use a extensão de notebooks do VS Code
jupyter lab curso_agente_leis_local_docker.ipynb
```

A primeira célula do notebook instala o resto das dependências, com versões fixadas.

---

## Roteiro da aula

| Tempo | Parte | Conteúdo | Ponto alto |
|------:|:---:|---|---|
| 10 min | 0 | Setup, chaves, limites (Free na nuvem · Docker no local) | a restrição de 1 coleção motiva o multi-tenancy |
| 20 min | 1 | Python: dicts, funções, list comprehensions, `requests` | filtro por palavra falha → motiva busca vetorial |
| 20 min | 2 | PDF → texto, `ThreadPoolExecutor`, regex | parser hierárquico da Lei Orgânica |
| 15 min | 3 | Chunking com LangChain | chunk por **artigo** vs por tamanho |
| 30 min | 4 | Weaviate: schema, batch, near_text/BM25/hybrid, dedup, filtros | os dois pontos cegos, lado a lado |
| 30 min | 5 | Agente: tools, roteamento, memória | RAG fixo falha → agente escolhe a base |
| 5 min | 6 | Encerramento e próximos passos | |

---

## Dados

Tudo público, coletado ao vivo pelo notebook:

| Fonte | Como é obtida | Volume |
|---|---|---|
| Catálogo de leis | endpoint JSON `teofilootoni.mg.leg.br/legislacoes/get/4` | 7.778 leis ordinárias (1947–2026) |
| Texto das leis | PDFs no S3 da Câmara | **~200 leis** (2024–2026) → ~1.175 chunks |
| Lei Orgânica | `.../site/lei-organica-completa-com-emendas.pdf` | 112 páginas → **243 artigos** → 265 chunks |

Os PDFs têm camada de texto — não é preciso OCR.

**Para ampliar a base:** mude `ANOS` na Parte 2 (ex.: `[2020, ..., 2026]`). O download roda em
paralelo (~40 s para 200 leis) e a importação no Weaviate leva poucos segundos.

---

## Arquitetura

```
Collection "Legislacao"  (multi-tenancy ligada)
├── tenant "leis"            ~1.175 chunks · leis ordinárias 2024-2026
└── tenant "lei_organica"       265 chunks · 243 artigos com TÍTULO > CAPÍTULO > Seção
```

Vetorizados: `ementa`, `contexto`, `texto`. Os demais campos são metadados filtráveis.

O agente tem duas ferramentas, uma por tenant, e **decide sozinho** qual usar lendo as
docstrings. Buscas usam `hybrid` com `alpha=0.6`, pedindo 20 resultados e agrupando por
documento (`deduplicar`) — sem isso, os 5 "melhores" chunks costumam ser 5 pedaços da
mesma lei longa, e o agente responde conhecendo uma lei só.

Na versão local o limite de 1 coleção não existe — e mesmo assim mantemos o multi-tenancy.
Vira um bom momento da aula: a mesma decisão, antes imposta pelo plano, agora tomada por mérito.

### Os dois exemplos que fazem a Parte 4 funcionar

| Consulta | BM25 | Vetorial | Lição |
|---|:---:|:---:|---|
| `"7956"` | ✅ acerta | ❌ erra | número exato não tem significado — embedding não ajuda |
| `"trabalhador que usa moto para levar pedidos"` | ❌ erra | ✅ acerta Lei 7.981/2026 | zero palavras em comum com a ementa |

Escolhidos por teste, não por sorte: com uma consulta fácil as três estratégias devolvem
o mesmo resultado e a aula perde o ponto. **Os dois se comportam igual nas duas versões** —
com Weaviate Embeddings na nuvem e com `embed-multilingual-v3.0` no local.

---

## Perguntas que funcionam bem na demo

| Pergunta | Roteamento esperado |
|---|---|
| "Quantos vereadores tem a Câmara?" | Lei Orgânica → Art. 21 (19 vereadores) |
| "Existe lei sobre motoristas de aplicativo?" | leis → Lei nº 7.981/2026 |
| "O que diz o artigo 143 da Lei Orgânica?" | Lei Orgânica com `artigo=143` |
| "Quem propõe emenda à Lei Orgânica, e há lei sobre crianças?" | **as duas** ferramentas |
| "Qual a alíquota do IPTU em 2019?" | busca e admite que não encontrou |

O melhor momento da aula é a Parte 5.3: o `rag_simples` erra a pergunta dos vereadores
porque o **programador** fixou a base. Aí entra o agente.

---

## Problemas comuns

### Nuvem

| Sintoma | Causa | Solução |
|---|---|---|
| `USAGE_LIMIT_EXCEEDED: collections count limit of 1` | plano Free | reaproveite a coleção existente ou use outro cluster |
| `USAGE_LIMIT_EXCEEDED: tenants count limit of 3` | tenants antigos ocupando os slots | `legislacao.tenants.remove([...])` ou cluster próprio |
| `404 ... no longer available to new users` | nome de modelo Gemini antigo | já tratado pelo `escolher_modelo` |
| `429 RESOURCE_EXHAUSTED` no meio da Parte 5 | cota diária do modelo Gemini esgotada | use um modelo `-lite` (padrão) ou espere a cota renovar |
| `503 UNAVAILABLE` num modelo | modelo sobrecarregado no momento | o `escolher_modelo` pula para o próximo da lista |

### Local

| Sintoma | Causa | Solução |
|---|---|---|
| `port is already allocated` | outra coisa usa a 8080 | `docker ps`, pare o outro contêiner, ou mude a porta no compose |
| `WeaviateStartUpError` / `connection refused` | contêiner parado ou ainda subindo | `docker compose up -d`, espere ~10 s |
| `Cannot connect to the Docker daemon` | Docker Desktop fechado | abra e espere ficar verde |
| `could not read schema ...: leader not found` | nome do nó mudou entre um `up` e outro | o `CLUSTER_HOSTNAME: node1` do compose evita isso — **não remova**. Se já aconteceu: `docker compose down -v` e reimporte |
| `429 ... You have no credits remaining` | conta OpenAI sem saldo | adicione créditos, ou mude para `PROVEDOR=cohere` |
| `429` com Cohere | rate limit da trial key (por **minuto**) | espere um minuto e rode a célula de novo |
| `ModelNotFound` num `gpt-*` | nome de modelo que não existe nessa conta | já tratado pelo `escolher_modelo` |
| erro de dimensão do vetor | trocou de provedor com a coleção já criada | `client.collections.delete("Legislacao")` e reimporte |

### Nas duas

| Sintoma | Causa | Solução |
|---|---|---|
| `tenant not found` | a criação dos tenants falhou antes | rode de novo a célula 4.4 e confira a saída |
| `ModuleNotFoundError: langchain_text_splitters` | célula 0.1 não rodou | rode a primeira célula do notebook |
| PDFs com texto vazio | PDF escaneado | precisaria de OCR (`pytesseract`) |
| `Con004: connection was not closed` | faltou `client.close()` | rode a última célula |

---

## Exercícios do notebook

1. **Parte 1** — `contar_por_ano(anos)`: quantas leis por ano.
2. **Parte 4** — comparar `near_text` vs `bm25`; achar o artigo sobre veto do Prefeito.
3. **Parte 5** — quebrar o roteamento apagando a docstring de uma tool (o exercício que
   mais ensina); criar uma terceira ferramenta `listar_leis_do_ano`.

Todos têm solução em `<details>` no próprio notebook.

---

## Status de validação

**Versão nuvem** — executada de ponta a ponta contra o Weaviate Cloud e a API do Gemini:
**54/54 células de código sem erro**, incluindo a coleta real dos PDFs, a importação no
Weaviate e todas as chamadas ao agente. Roteamento verificado em 5/5 perguntas
(`gemini-3.5-flash-lite`), incluindo a que ele deve recusar.

**Versão local** — executada de ponta a ponta contra o contêiner do `docker-compose.yml`,
**nos dois provedores**, cada um a partir de uma coleção zerada:

| | `PROVEDOR=cohere` | `PROVEDOR=openai` |
|---|---|---|
| Embeddings | `embed-multilingual-v3.0` | `text-embedding-3-small` |
| LLM escolhido | `command-a-03-2025` | `gpt-5-mini` |
| Células de código | **54/54 sem erro** | **54/54 sem erro** |
| Importação | 1.175 + 265 objetos, 0 falhas (8,3 s) | 1.175 + 265 objetos, 0 falhas (11,8 s) |
| Roteamento do agente | 5/5 | 5/5 |
| Os 2 exemplos da Parte 4 | ✅ igual à nuvem | ✅ igual à nuvem |

Nos dois casos o agente acertou inclusive a pergunta que ele **deve** recusar (IPTU/2019) e
a de memória conversacional. As saídas gravadas no notebook são da execução com Cohere,
que é o padrão do `.env.example`.

> Detalhe que vale a aula: a API da OpenAI responde `400` a `temperature=0` num `gpt-5*`
> ("only the default (1) value is supported"), mas o notebook passa `temperature=0` para
> todos os modelos e funciona — o `langchain-openai` detecta o modelo de raciocínio e
> **descarta o parâmetro** antes de enviar. A célula 5.2 comenta isso.
