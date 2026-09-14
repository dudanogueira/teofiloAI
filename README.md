# Mini curso: Agente de IA para a legislação de Teófilo Otoni

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dudanogueira/teofiloAI/blob/main/curso_agente_leis_teofilo_otoni.ipynb)

Notebook de 2 horas que ensina **Python + LangChain + Weaviate** construindo um agente
que responde perguntas sobre as leis do município de Teófilo Otoni/MG, citando a fonte.

Clique no botão acima para abrir direto no Google Colab — ou baixe
[`curso_agente_leis_teofilo_otoni.ipynb`](curso_agente_leis_teofilo_otoni.ipynb) e suba em *File → Upload notebook*.

---

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
>    nesta tarefa. Testado: acerto em 4/4 perguntas de roteamento.
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

## Roteiro da aula

| Tempo | Parte | Conteúdo | Ponto alto |
|------:|:---:|---|---|
| 10 min | 0 | Setup, chaves, limites do plano Free | a restrição de 1 coleção motiva o multi-tenancy |
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
| Texto das leis | PDFs no S3 da Câmara | **194 leis** (2024–2026) → ~1.160 chunks |
| Lei Orgânica | `.../site/lei-organica-completa-com-emendas.pdf` | 112 páginas → **243 artigos** → 265 chunks |

Os PDFs têm camada de texto — não é preciso OCR.

**Para ampliar a base:** mude `ANOS` na Parte 2 (ex.: `[2020, ..., 2026]`). O download roda em
paralelo (~40 s para 194 leis) e a importação no Weaviate leva poucos segundos.

---

## Arquitetura

```
Collection "Legislacao"  (multi-tenancy ligada)
├── tenant "leis"            1.160 chunks · leis ordinárias 2024-2026
└── tenant "lei_organica"      265 chunks · 243 artigos com TÍTULO > CAPÍTULO > Seção
```

Vetorizados: `ementa`, `contexto`, `texto`. Os demais campos são metadados filtráveis.

O agente tem duas ferramentas, uma por tenant, e **decide sozinho** qual usar lendo as
docstrings. Buscas usam `hybrid` com `alpha=0.6`, pedindo 20 resultados e agrupando por
documento (`deduplicar`) — sem isso, os 5 "melhores" chunks costumam ser 5 pedaços da
mesma lei longa, e o agente responde conhecendo uma lei só.

### Os dois exemplos que fazem a Parte 4 funcionar

| Consulta | BM25 | Vetorial | Lição |
|---|:---:|:---:|---|
| `"7956"` | ✅ acerta | ❌ erra | número exato não tem significado — embedding não ajuda |
| `"trabalhador que usa moto para levar pedidos"` | ❌ erra | ✅ acerta Lei 7.981/2026 | zero palavras em comum com a ementa |

Escolhidos por teste, não por sorte: com uma consulta fácil as três estratégias devolvem
o mesmo resultado e a aula perde o ponto.

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

| Sintoma | Causa | Solução |
|---|---|---|
| `USAGE_LIMIT_EXCEEDED: collections count limit of 1` | plano Free | reaproveite a coleção existente ou use outro cluster |
| `USAGE_LIMIT_EXCEEDED: tenants count limit of 3` | tenants antigos ocupando os slots | `legislacao.tenants.remove([...])` ou cluster próprio |
| `tenant not found` | a criação dos tenants falhou antes | rode de novo a célula 4.4 e confira a saída |
| `404 ... no longer available to new users` | nome de modelo Gemini antigo | já tratado pelo `escolher_modelo` |
| `429 RESOURCE_EXHAUSTED` no meio da Parte 5 | cota diária do modelo Gemini esgotada | use um modelo `-lite` (padrão) ou espere a cota renovar |
| `503 UNAVAILABLE` num modelo | modelo sobrecarregado no momento | o `escolher_modelo` pula para o próximo da lista |
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

O notebook foi executado de ponta a ponta contra o Weaviate Cloud e a API do Gemini:
**54/54 células de código sem erro**, incluindo a coleta real dos PDFs, a importação no
Weaviate e todas as chamadas ao agente.

Roteamento do agente verificado em 5/5 perguntas (`gemini-3.5-flash-lite`), incluindo a
que ele deve recusar.
