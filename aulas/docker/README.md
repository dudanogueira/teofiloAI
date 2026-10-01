# 🐳 Docker do zero

Aula de **2 horas** para iniciantes: do "por que Docker existe" até subir uma aplicação com dois
serviços via Docker Compose e controlar contêineres pelo Python. Notebook:
[`aula_docker.ipynb`](aula_docker.ipynb).

## Preparação (faça antes da aula)

### 1. Docker Desktop

| | |
|---|---|
| 🪟 **Windows** | Baixe em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/). O instalador pede para ativar o **WSL2**: aceite e reinicie. Se aparecer erro de virtualização, ela precisa ser ligada na BIOS (em laboratórios, peça ao suporte). |
| 🍎 **Mac** | Baixe a versão do seu processador: **Apple Silicon** (M1, M2...) ou **Intel** ( → Sobre este Mac). |

Abra o Docker Desktop e espere o ícone da baleia indicar que está rodando. Teste num terminal:

```bash
docker run hello-world
```

> Outras opções no Mac (Colima, OrbStack, Rancher Desktop) também funcionam: o notebook só usa o
> comando `docker`.

### 2. Python e Jupyter

```bash
cd aulas/docker
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac
pip install -r requirements.txt
jupyter notebook aula_docker.ipynb
```

### 3. Baixe as imagens antes (opcional, mas recomendado em turma)

Com 20 pessoas baixando ao mesmo tempo, a rede sofre. Rode antes da aula:

```bash
docker pull hello-world
docker pull nginx:alpine
docker pull alpine
docker pull redis:8-alpine
docker pull python:3.13-slim
```

## Roteiro

| Parte | Assunto | Tempo |
|---|---|---|
| 0 | Por que Docker, VM × contêiner, vocabulário, `docker version` | 20 min |
| 1 | `run`, `ps`, `logs`, `stop`, `start`, `rm`, publicar portas (nginx) | 25 min |
| 2 | Variáveis de ambiente, `exec`, bind mounts e volumes | 20 min |
| 3 | `Dockerfile`, `build`, cache de camadas, rodar a própria imagem (Flask) | 20 min |
| 4 | Redes entre contêineres e Docker Compose (Flask + Redis) | 20 min |
| 5 | SDK `docker` para Python; o `docker-compose.yml` do Weaviate do curso, linha a linha | 10 min |
| 6 | Limpeza e colinha de comandos | 5 min |

Cada parte termina com um 🎯 exercício, com solução escondida.

## Arquivos

```
docker/
├── aula_docker.ipynb
├── requirements.txt
├── diagramas/              ← SVGs usados no notebook
└── exemplos/
    ├── site/index.html     ← servido pelo nginx via bind mount (Parte 2)
    ├── app_flask/          ← app + Dockerfile da Parte 3
    └── compose/            ← Flask + Redis da Parte 4
```

O exemplo do Compose também roda sozinho, fora do notebook:

```bash
cd exemplos/compose
docker compose up -d --build
# abra http://localhost:8000 e recarregue: o contador de visitas sobe
docker compose down -v
```

## Portas usadas

| Porta | Quem | Parte |
|---|---|---|
| 8088 | nginx | 1 e 2 |
| 8000 | app Flask (por dentro: 5000) | 3 e 4 |

> 🍎 A porta **5000 é evitada de propósito**: no Mac ela é ocupada pelo *AirPlay Receiver*. O
> notebook explica isso — é um bom exemplo de por que a porta de fora é escolha sua.

## Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `Cannot connect to the Docker daemon` / `error during connect` | O Docker Desktop não está aberto. Abra e espere ficar pronto. |
| `port is already allocated` | Outro contêiner (ou programa) usa a porta. `docker ps` mostra quem; troque o número da esquerda do `-p`. |
| Windows: `WSL 2 installation is incomplete` | Rode `wsl --update` num PowerShell como administrador e reinicie. |
| Bind mount vazio no Windows | Confira se a pasta está num disco local (não em rede) e se o caminho tem `/`. O notebook usa `.as_posix()` para isso. |
| `docker.errors.DockerException` na Parte 5 | A função `conectar_docker()` do notebook já pergunta o endereço ao comando `docker`; confira se o `docker ps` funciona no terminal. |

## Status de validação

Executado de ponta a ponta no **macOS (Apple Silicon)** com Docker Engine 29: **todas as células
de código sem erro**, e a limpeza final não deixa contêiner, rede, volume nem imagem da aula para
trás. Nenhum comando depende do shell (tudo passa pela função `rodar()`, com `subprocess`), então o
mesmo notebook vale para o Windows — mas ele **ainda não foi executado numa máquina Windows**.
