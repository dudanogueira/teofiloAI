# 🔀 Versão n8n (sem código)

O mesmo agente do notebook, montado com **nós visuais no [n8n](https://n8n.io)** em vez de
Python. Mesmo acervo (202 leis ordinárias de 2024–2026 + os 243 artigos da Lei Orgânica),
mesmas duas bases de conhecimento, mesmas instruções do agente.

| | Notebook local | n8n |
|---|---|---|
| Onde se programa | células Python | nós arrastados na tela |
| Separação das bases | 1 coleção, 2 **tenants** | **2 coleções**: `LeisMunicipais` e `LeiOrganica` |
| Quem gera o vetor | o Weaviate (módulo `text2vec-*`) | o n8n (nó *Embeddings OpenAI*) |
| Provedor | OpenAI ou Cohere | OpenAI (`gpt-5-mini` + `text-embedding-3-small`) |
| Busca | híbrida, alpha 0.6 | híbrida, alpha 0.6 |

## Preparação

Você precisa de **Docker** e de uma **API key da OpenAI** com créditos
([platform.openai.com/api-keys](https://platform.openai.com/api-keys)).
A ingestão inteira custa poucos centavos (≈1,6 mil trechos em `text-embedding-3-small`).

```bash
cd n8n
docker compose up -d
```

Isso sobe dois contêineres:

| Contêiner | O que é | Porta no seu computador |
|---|---|---|
| `weaviate-n8n` | o banco vetorial | `8080` (REST) e `50051` (gRPC) |
| `n8n-curso` | o n8n | [`5678`](http://localhost:5678) |

> ⚠️ São as mesmas portas do Weaviate do notebook local. Se ele estiver rodando, pare antes:
> `docker compose stop` na raiz do repositório.

Abra **http://localhost:5678** e crie a sua conta de dono: e-mail e senha à sua escolha,
que ficam só na sua máquina.

## Importar os workflows

Os dois workflows estão na pasta [`workflows/`](workflows/). Para cada arquivo:

1. No n8n, clique em **Create workflow** (ou **+** → *Workflow*).
2. No menu **⋯** (canto superior direito), escolha **Import from File…**.
3. Selecione o arquivo e clique em **Save**.

| Arquivo | Workflow |
|---|---|
| `01_ingestao.json` | 01 · Ingestão das leis de Teófilo Otoni |
| `02_agente.json` | 02 · Agente da legislação de Teófilo Otoni |

> Também funciona abrir o arquivo `.json`, copiar tudo (Ctrl/Cmd+C) e colar
> (Ctrl/Cmd+V) em um workflow vazio.

## Criar as duas credenciais

Os workflows vêm **sem credenciais**: cada aluno cadastra as suas. No n8n, vá em
**Overview → Credentials → Create credential** (ou clique em qualquer nó OpenAI/Weaviate
e escolha *Create new credential*).

### 1. OpenAI

- Tipo: **OpenAI**
- **API Key**: a sua chave `sk-...`
- O resto fica como está.

### 2. Weaviate

- Tipo: **Weaviate Credentials**
- **Connection Type**: `Custom Connection`
- **Weaviate Api Key**: deixe em branco (o Weaviate local não tem senha)

| Campo | Valor |
|---|---|
| Custom Connection HTTP Host | `weaviate` |
| Custom Connection HTTP Port | `8080` |
| Custom Connection HTTP Secure | desligado |
| Custom Connection gRPC Host | `weaviate` |
| Custom Connection gRPC Port | `50051` |
| Custom Connection gRPC Secure | desligado |

> ⚠️ **É `weaviate`, não `localhost`.** O n8n roda dentro do Docker; para ele, `localhost`
> é o próprio contêiner do n8n. Os contêineres se enxergam pelo **nome do serviço** no
> `docker-compose.yml`. A porta `8080` é a de dentro do contêiner (coincide com a publicada
> para o seu computador, mas são coisas diferentes).

Clique em **Save**: o n8n testa a conexão na hora.

### Onde escolher as credenciais

Abra cada workflow e, nos nós abaixo, selecione a credencial criada. Os nós sem credencial
aparecem com um ⚠️.

| Workflow | Credencial OpenAI | Credencial Weaviate |
|---|---|---|
| 01 · Ingestão | `Embeddings OpenAI (leis)`, `Embeddings OpenAI (artigos)` | `Gravar em LeisMunicipais`, `Gravar em LeiOrganica` |
| 02 · Agente | `OpenAI gpt-5-mini`, `Embeddings OpenAI` | `consultar_lei_organica`, `buscar_leis_municipais` |

## Workflow 1 — Ingestão

Abra **01 · Ingestão das leis de Teófilo Otoni** e clique em **Execute workflow**.
Leva alguns minutos (baixa ~200 PDFs). Pode rodar de novo quando quiser: ele apaga as
coleções e recria do zero.

```
Iniciar ─ Coleções a recriar ─ Apagar coleções ─┬─ Anos ─ Listar leis do ano ─ Separar leis ─ Preparar leis
                                                │    ─ Baixar PDF ─ Extrair texto do PDF ─ Limpar texto ─ Gravar em LeisMunicipais
                                                │
                                                └─ Baixar Lei Orgânica ─ Extrair páginas ─ Extrair artigos ─ Gravar em LeiOrganica
```

| Nó | No notebook |
|---|---|
| `Listar leis do ano` (HTTP Request) | `listar_leis()` |
| `Preparar leis` (Code) | `url_do_pdf()` + filtro das leis com PDF |
| `Baixar PDF` + `Extrair texto do PDF` | `baixar_pdf()` + `pdf_para_texto()` |
| `Limpar texto` (Code) | `limpar()` e o descarte de PDFs com menos de 200 caracteres |
| `Extrair artigos` (Code) | `parse_lei_organica()`, traduzida para JavaScript, com as mesmas regex |
| `Dividir em trechos` | `RecursiveCharacterTextSplitter` (1200/150 nas leis, 1800/200 na LO) |
| `Gravar em …` + `Embeddings OpenAI` | a criação da coleção + `batch.add_object()` |

Os nós *Code* são o único lugar com código, e são as mesmas funções do notebook — vale
abri-los lado a lado com a Parte 3.

Ao final, as coleções ficam com cerca de **1.335 trechos** (`LeisMunicipais`) e **277**
(`LeiOrganica`). O notebook dá 1.175 e 265: aqui a ementa e o caminho TÍTULO > CAPÍTULO
entram no texto antes de dividir, então alguns documentos rendem um trecho a mais.

## Workflow 2 — Agente

Abra **02 · Agente da legislação de Teófilo Otoni** e clique em **Open chat**, no rodapé.

- **Agente** — o *System Message* é o mesmo texto `INSTRUCOES` do notebook.
- **OpenAI gpt-5-mini** — o LLM, o mesmo do notebook.
- **Memória da conversa** — as últimas 10 mensagens; faz o papel do `InMemorySaver`.
- **`consultar_lei_organica`** e **`buscar_leis_municipais`** — dois nós Weaviate no modo
  *Retrieve Documents (As Tool for AI Agent)*, cada um em uma coleção. O campo
  **Description** faz o papel da docstring do `@tool`: é o que o modelo lê para
  decidir qual base consultar.
- **Embeddings OpenAI** — transforma a consulta em vetor. Tem que ser o **mesmo modelo** da
  ingestão (`text-embedding-3-small`): vetores de modelos diferentes não se comparam.

Perguntas para testar (as mesmas da Parte 7):

1. Quantos vereadores tem a Câmara Municipal de Teófilo Otoni?
2. Existe alguma lei sobre motoristas de aplicativo e entregadores na cidade?
3. Quem pode propor emenda à Lei Orgânica, e existe alguma lei recente sobre proteção
   de crianças e adolescentes no município?
4. O que diz o artigo 143 da Lei Orgânica?
5. Qual é a alíquota do IPTU em Teófilo Otoni para imóveis residenciais em 2019?
6. O que a Lei Orgânica diz sobre o meio ambiente? → *E existe alguma lei municipal recente sobre esse mesmo tema?*

Clique em cada nó depois de uma pergunta para ver **o que ele recebeu e devolveu** — é o
equivalente visual aos `🔧 ferramenta(...)` que o notebook imprimia.

## O que o n8n faz diferente (bom assunto para a aula)

- **Duas coleções em vez de tenants.** No Docker não há o limite de 1 coleção do Weaviate
  Cloud Free, e o nó Weaviate do n8n cria uma coleção por nome sozinho. Compare: tenants
  isolam dados *com o mesmo schema*; coleções podem ter schemas diferentes.
- **Schema automático.** O n8n usa o formato do LangChain: o trecho vai na propriedade
  `text` e cada metadado vira uma propriedade. No notebook nós desenhamos o schema à mão
  (tipos, tokenização, o que entra ou não no vetor).
- **Quem vetoriza é o n8n.** O modelo é o mesmo do notebook (`text-embedding-3-small`), mas
  a chamada sai do n8n, não do Weaviate. Por isso a ementa (leis) e o caminho
  TÍTULO > CAPÍTULO (LO) são colados no começo do texto antes de dividir: é assim que
  entram no vetor.
- **Ferramentas mais simples.** As tools do notebook tinham parâmetros opcionais (`ano`,
  `artigo`) e deduplicavam os trechos por lei. Aqui a ferramenta recebe só a consulta, e
  o mesmo documento pode aparecer em mais de um trecho.
- **"Clear Data" não serve.** O nó Weaviate tem uma opção para limpar a coleção antes de
  gravar, mas no n8n 2.40 ela apaga a coleção **a cada lote de 200 trechos**, e só o último
  lote sobreviveria. Por isso a ingestão apaga as coleções pela API REST do Weaviate antes.

## Comandos úteis

```bash
docker compose stop            # para tudo (dados e workflows ficam)
docker compose up -d           # sobe de novo
docker compose down -v         # apaga TUDO: coleções, conta, credenciais e workflows
```

Conferir quantos objetos há em cada coleção:

```bash
curl -s localhost:8080/v1/graphql -H 'content-type: application/json' \
  -d '{"query":"{ Aggregate { LeisMunicipais { meta { count } } LeiOrganica { meta { count } } } }"}'
```
