# 🦙 Opcional: LLM local com Ollama

O [Ollama](https://ollama.com) roda modelos de linguagem abertos (Llama, Qwen, Gemma…)
**na sua máquina**. Aqui ele sobe como mais um contêiner, ao lado do Weaviate e do n8n,
definido num arquivo separado: [`../docker-compose.ollama.yml`](../docker-compose.ollama.yml).

É opcional e didático: dá para ver um LLM rodando sem internet e sem chave, e comparar as
respostas com as do `gpt-5-mini`. Para a aula, o agente principal (OpenAI) é bem mais rápido
e erra menos. Veja [Desempenho](#desempenho-medido).

## Subir

Rode de dentro da pasta `n8n/`, passando **os dois** arquivos com `-f`:

```bash
cd n8n
docker compose -f docker-compose.yml -f docker-compose.ollama.yml up -d
```

O segundo arquivo **se soma** ao primeiro: o Ollama entra no mesmo projeto e na mesma rede
do n8n, e o n8n o encontra pelo nome `ollama`.

> 💡 **Para não repetir os `-f`**: todo comando `docker compose` (`exec`, `ps`, `logs`,
> `down`…) precisa receber os dois arquivos, senão ele não enxerga o serviço `ollama`.
> Defina uma vez no terminal:
>
> ```bash
> export COMPOSE_FILE=docker-compose.yml:docker-compose.ollama.yml
> ```
>
> Daí em diante, `docker compose up -d`, `docker compose exec ollama …` etc. já usam os dois.
> Os exemplos abaixo supõem que você fez isso.

| Contêiner | O que é | Porta no seu computador |
|---|---|---|
| `ollama-curso` | o servidor do Ollama | `11435` |

A porta é `11435`, e não a `11434` padrão, para não brigar com um Ollama instalado direto no
computador. O n8n **não** usa essa porta: dentro do Docker ele fala com `http://ollama:11434`.

## Baixar modelos

O contêiner sobe **vazio**. Os modelos são baixados para o volume `ollama_data` e ficam lá
(sobrevivem a `down` e a recriar o contêiner):

```bash
docker compose exec ollama ollama pull llama3.1     # 4,9 GB, o do agente
docker compose exec ollama ollama list              # o que já foi baixado
docker compose exec ollama ollama rm llama3.1       # apagar um modelo
```

Outros modelos: [ollama.com/search](https://ollama.com/search). Para usar no agente do n8n, o
modelo precisa suportar **tools** ([lista](https://ollama.com/search?c=tools)). Um pequeno
para testar rápido: `smollm2:135m` (270 MB).

## Terminal interativo

Para conversar com o modelo direto no terminal, sem o n8n:

```bash
docker compose exec ollama ollama run llama3.1
```

Ou, sem precisar do `COMPOSE_FILE` nem dos `-f`, pelo nome do contêiner:

```bash
docker exec -it ollama-curso ollama run llama3.1
```

Aparece o prompt `>>>`. Digite e aperte Enter:

```
>>> O que é uma Lei Orgânica municipal?
Uma Lei Orgânica municipal é a norma fundamental de um município...

>>> /bye
```

Comandos dentro do prompt:

| Comando | O que faz |
|---|---|
| `/?` | lista os comandos |
| `/bye` | sai (ou Ctrl+D) |
| `/clear` | esquece a conversa até aqui |
| `/set system "Responda sempre em português."` | define as instruções de sistema |
| `/set parameter num_ctx 16384` | aumenta o contexto |
| `/show info` | mostra detalhes do modelo (tamanho, contexto, se suporta tools…) |
| `"""` | começa/termina um texto de várias linhas |

Uma pergunta só, sem abrir o prompt (bom para scripts), e com estatísticas de velocidade:

```bash
docker compose exec ollama ollama run llama3.1 --verbose "Explique o que é uma Lei Orgânica"
```

O `--verbose` mostra `eval rate` (tokens gerados por segundo) no final. É o jeito mais fácil
de sentir a diferença entre CPU e GPU.

### Mais comandos úteis

```bash
docker compose exec ollama ollama ps            # modelos carregados na memória agora
docker compose exec ollama ollama stop llama3.1 # tira o modelo da memória
docker compose exec ollama sh                   # um shell dentro do contêiner (exit sai)
docker compose logs -f ollama                   # log do servidor (cada chamada do n8n aparece aqui)
```

A API também responde no seu computador:

```bash
curl http://localhost:11435/api/tags            # modelos baixados, em JSON
OLLAMA_HOST=http://localhost:11435 ollama list  # se você tiver o CLI do Ollama instalado
```

## Usar no agente do n8n

O workflow [`02_agente_ollama.json`](02_agente_ollama.json) é o mesmo agente da versão
OpenAI, mas quem **gera a resposta** é o `llama3.1` no Ollama. Só a parte generativa muda:
a **busca continua igual**, com as mesmas coleções e os mesmos embeddings da OpenAI. Por isso
ele não tem ingestão própria.

| | 02 · Agente | 02 · Agente (Ollama) |
|---|---|---|
| LLM (gera a resposta) | `gpt-5-mini`, na nuvem | `llama3.1` (8B), no seu computador |
| Embeddings (busca) | `text-embedding-3-small` | o mesmo |
| Coleções | `LeisMunicipais`, `LeiOrganica` | as mesmas |

1. Rode antes o **01 · Ingestão** (o normal, da pasta `workflows/`).
2. Baixe o modelo: `docker compose exec ollama ollama pull llama3.1`.
3. Crie a credencial **Ollama**:
   - Tipo: **Ollama**
   - **Base URL**: `http://ollama:11434` (o nome do serviço, como no Weaviate)
4. Importe [`02_agente_ollama.json`](02_agente_ollama.json) (**⋯ → Import from File…**) e
   escolha as credenciais:

| Nó | Credencial |
|---|---|
| `Ollama llama3.1` | Ollama |
| `Embeddings OpenAI` | OpenAI |
| `consultar_lei_organica`, `buscar_leis_municipais` | Weaviate |

O nó `Ollama llama3.1` vem com **Context Length** (`numCtx`) = 16384: com o padrão do Ollama
(4096), as instruções + os trechos das ferramentas não cabem, e o modelo passa a responder
sem base. Para testar outro modelo, baixe-o e troque o campo **Model** do nó.

Enquanto o agente responde, deixe `docker compose logs -f ollama` aberto noutro terminal:
dá para ver cada ida do n8n ao modelo e quanto tempo ela levou.

## Desempenho (medido)

Num Mac M2 Pro com 32 GB, com as 7 perguntas de teste do [README do n8n](../README.md):

| Onde roda o Ollama | Resposta de uma pergunta | Geração |
|---|---|---|
| **Contêiner** (este compose) | 50 s a 3,5 min | ~13 tokens/s, só CPU |
| **Nativo** no Mac | 13 s a 35 s | usa a GPU (Metal) |

> ⚠️ **No Mac, o Docker não acessa a GPU.** Dentro do contêiner o Ollama roda só na CPU, e
> cada pergunta ao agente vira 2 ou mais chamadas ao modelo, com prompts grandes. Funciona,
> mas é lento. Com contexto de 16 mil tokens, o `llama3.1` ocupa ~7 GB de RAM: confira se o
> Docker tem memória suficiente. Em Linux com GPU NVIDIA, descomente o bloco `deploy:` do
> `docker-compose.ollama.yml`.

O `llama3.1` escolheu a base certa em todas as perguntas, inclusive a que exige as duas.
Mas **errou mais que o `gpt-5-mini`**, e nem sempre do mesmo jeito: numa execução, respondeu
"quem pode propor emenda à Lei Orgânica" com um artigo sobre leis ordinárias, e atribuiu
conteúdo ambiental a uma lei que é o Plano Plurianual. Bom material para a aula: mesmas
ferramentas, mesmos trechos recuperados, só o modelo mudou. Abra o nó da ferramenta e compare
o que foi recuperado com o que o modelo escreveu.

### Mais rápido no Mac: Ollama nativo

Com o [Ollama instalado](https://ollama.com) direto no Mac (`ollama pull llama3.1`), não é
preciso este compose. Só muda a **Base URL** da credencial: `http://host.docker.internal:11434`.
Docker Desktop, Rancher Desktop e OrbStack resolvem esse nome sozinhos.

## Desligar e apagar

```bash
docker compose stop ollama     # para só o Ollama (os modelos ficam)
docker compose rm -sf ollama   # remove o contêiner (os modelos continuam no volume)
docker volume rm n8n_ollama_data   # apaga os modelos baixados
```

`docker compose down -v` **com** o `COMPOSE_FILE` definido apaga tudo, inclusive os modelos.
