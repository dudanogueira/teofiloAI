# 🧱 Do zero ao Docker: Flask + Postgres + Git

Aula de **2 horas** para iniciantes: criar um projeto do zero, versionar com **git**, publicar no
**GitHub** e empacotar um app **Flask** numa **imagem Docker** que conversa com um **Postgres**,
tudo ligado pelo **Docker Compose**.

O app é um **contador por usuário**: cada pessoa cria uma conta, faz login e tem o seu próprio
número para aumentar (+1) ou diminuir (−1). É pequeno, mas tem o que um app de verdade tem: banco
de dados, senhas guardadas do jeito certo, sessão de login e proteção contra CSRF.

> A aula [🐳 Docker do zero](../docker/) é uma boa preparação, mas não é obrigatória.

## Como a aula funciona

O projeto cresce em **7 passos**. Cada pasta em [`passos/`](passos/) é uma **foto completa** do
projeto ao fim daquele passo, e [`projeto_completo/`](projeto_completo/) é o resultado final.

```
flask_postgres/
├── README.md                ← este roteiro
├── projeto_completo/        ← o projeto pronto (igual ao passo 07)
└── passos/
    ├── 01_projeto/          ← Flask "Olá" + git + GitHub
    ├── 02_dockerfile/       ← a primeira imagem Docker
    ├── 03_compose_postgres/ ← Docker Compose com app + Postgres
    ├── 04_modelo_usuario/   ← a tabela de usuários
    ├── 05_login/            ← cadastro, login e logout
    ├── 06_contador/         ← o contador de cada usuário
    └── 07_producao/         ← gunicorn, usuário não-root, healthcheck
```

Você **não trabalha dentro desta pasta**: cria o seu próprio projeto (e o seu próprio repositório
no GitHub) numa pasta `contador` e, a cada passo, escreve as mudanças e faz **um commit**. No fim,
o `git log` do seu repositório conta a história da aula.

Para ver só o que mudou de um passo para o outro:

```bash
cd aulas/flask_postgres/passos
git diff --no-index 04_modelo_usuario 05_login        # funciona no Windows e no Mac
```

> 💡 Ficou para trás? Copie a pasta do passo por cima da sua (os comandos estão em
> [Problemas comuns](#problemas-comuns)) e continue dali.

O código tem **links para a documentação** (Flask, Flask-Login, Flask-WTF, Flask-SQLAlchemy,
Docker) nos comentários, ao lado de cada coisa nova. Abra os links durante a aula.

## Preparação (faça antes da aula)

| O que | Como testar | Onde baixar |
|---|---|---|
| **Git** | `git --version` | 🪟 [git-scm.com/download/win](https://git-scm.com/download/win) (já traz o *Git Credential Manager*) · 🍎 já vem com as *Command Line Tools* (`xcode-select --install`) |
| **Conta no GitHub** | entrar em [github.com](https://github.com) | [github.com/signup](https://github.com/signup) |
| **Docker Desktop** | `docker run hello-world` | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **Python 3.11+** | `python --version` | [python.org/downloads](https://www.python.org/downloads/) (🪟 marque *Add python.exe to PATH*) |
| GitHub CLI (opcional) | `gh --version` | [cli.github.com](https://cli.github.com/) |

Configure o seu nome e e-mail no git (aparecem em todo commit):

```bash
git config --global user.name "Seu Nome"
git config --global user.email "voce@exemplo.com"
git config --global init.defaultBranch main
```

Baixe as imagens antes (com a turma toda baixando ao mesmo tempo, a rede sofre):

```bash
docker pull python:3.13-slim
docker pull postgres:17-alpine
```

## Roteiro

| Passo | Assunto | Tempo |
|---|---|---|
| 01 | Projeto Flask, venv, `.gitignore`, primeiro commit, GitHub e `push` | 25 min |
| 02 | `Dockerfile`, `.dockerignore`, `docker build` e `docker run` | 15 min |
| 03 | Docker Compose: app + Postgres, `.env`, rede entre serviços | 20 min |
| 04 | Modelo `Usuario` com Flask-SQLAlchemy; dados no volume | 10 min |
| 05 | Cadastro, login e logout: Flask-Login, Flask-WTF, hash de senha, CSRF | 25 min |
| 06 | O contador de cada usuário; `UPDATE` atômico; tag de versão | 15 min |
| 07 | Produção: gunicorn, usuário não-root, healthcheck, `restart` | 10 min |

Cada passo segue o mesmo ritmo: **escrever → rodar → olhar → `git commit` → `git push`**.

---

## Passo 01 — O projeto e o git (25 min)

📁 [`passos/01_projeto/`](passos/01_projeto/) · 📖 [Flask: instalação](https://flask.palletsprojects.com/en/stable/installation/) e [guia rápido](https://flask.palletsprojects.com/en/stable/quickstart/)

**1. Crie a pasta e o ambiente virtual**

```bash
mkdir contador
cd contador
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell ou cmd)
source .venv/bin/activate       # Mac
```

**2. Escreva os arquivos** `app.py`, `requirements.txt`, `.gitignore` e `README.md` (veja a pasta do
passo). Repare no `.gitignore`: o `.venv/` e o `.env` **nunca** vão para o git.

**3. Rode**

```bash
pip install -r requirements.txt
python app.py
```

Abra http://localhost:8000. Pare com `Ctrl+C`.

> 🍎 Usamos a porta **8000** e não a 5000 (a padrão do Flask): no Mac a 5000 é do *AirPlay
> Receiver*.

**4. Primeiro commit**

```bash
git init
git status                       # .venv não aparece: é o .gitignore funcionando
git add .
git commit -m "Passo 01: app Flask mínimo"
git log --oneline
```

**5. Publique no GitHub**

Crie um repositório **vazio** chamado `contador`: no site, em
[github.com/new](https://github.com/new) (**sem** README, `.gitignore` nem licença, porque já temos
os nossos), e depois:

```bash
git remote add origin https://github.com/SEU-USUARIO/contador.git
git branch -M main
git push -u origin main
```

Ou, com o GitHub CLI, tudo de uma vez:

```bash
gh auth login
gh repo create contador --public --source . --push
```

> 🔑 **O push pede senha?** O GitHub não aceita mais a senha da conta no `git push`.
> 🪟 No Windows o *Git Credential Manager* abre o navegador para você entrar. 🍎 No Mac use o
> `gh auth login` (ele configura o git) ou crie um
> [token de acesso pessoal](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
> e cole-o no lugar da senha.

Recarregue a página do repositório no GitHub: os arquivos estão lá.

🎯 **Exercício:** crie a rota `/sobre` que responde com o seu nome. Faça `git status`, `git diff`,
o commit e o push. Veja o commit aparecer no GitHub.

---

## Passo 02 — A primeira imagem (15 min)

📁 [`passos/02_dockerfile/`](passos/02_dockerfile/) · 📖 [Referência do Dockerfile](https://docs.docker.com/reference/dockerfile/)

Novos: `Dockerfile` (a receita da imagem, comentada linha a linha) e `.dockerignore` (o que **não**
entra na imagem: `.venv`, `.git`, `.env`...).

```bash
docker build -t contador:0.1 .
docker images contador
docker run --rm -p 8000:8000 contador:0.1
```

Abra http://localhost:8000: é o mesmo app, agora rodando num Linux dentro do contêiner. Pare com
`Ctrl+C`.

**O que observar**

- No `-p 8000:8000`, o número da **esquerda** é a porta do seu computador e o da **direita** a do
  contêiner. Teste `-p 9000:8000` e abra http://localhost:9000.
- Rode o `docker build` de novo: ele termina em segundos, porque usou o **cache de camadas**. Mude
  só o `app.py` e rode outra vez: o `pip install` continua no cache (por isso o `requirements.txt`
  é copiado antes do resto).
- O `app.run(host="0.0.0.0")` importa: com `127.0.0.1` o app só escutaria a si mesmo, dentro do
  contêiner, e a porta publicada não funcionaria.

```bash
git add .
git commit -m "Passo 02: Dockerfile"
git push
```

🎯 **Exercício:** construa a imagem com a tag `contador:0.2` e confira as duas com
`docker images contador`. Qual o tamanho delas?

---

## Passo 03 — Docker Compose: app + Postgres (20 min)

📁 [`passos/03_compose_postgres/`](passos/03_compose_postgres/) · 📖 [Configuração do Flask](https://flask.palletsprojects.com/en/stable/config/) · [Flask-SQLAlchemy](https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/) · [Compose](https://docs.docker.com/reference/compose-file/services/) · [imagem do Postgres](https://hub.docker.com/_/postgres)

Novos: `docker-compose.yml` (dois serviços, `app` e `db`), `.env.example` e a rota `/saude`, que
pergunta a versão ao Postgres. O `requirements.txt` ganha `flask-sqlalchemy` e `psycopg`.

**Segredos ficam fora do git.** O `.env.example` (sem segredos de verdade) vai para o git; o `.env`
(com as senhas) fica só na sua máquina:

```bash
cp .env.example .env             # Mac
copy .env.example .env           # Windows
git status                       # .env não aparece; .env.example aparece
```

```bash
docker compose up -d --build
docker compose ps                # db fica "healthy" antes de o app subir
docker compose logs app
```

Abra http://localhost:8000/saude.

**O que observar**

- No `DATABASE_URL`, o endereço do banco é **`db`**, o nome do serviço. O Compose cria uma rede
  em que cada serviço se acha pelo nome.
- O Postgres **não** publica porta nenhuma: só o app fala com ele, pela rede interna.
- O `depends_on` com `condition: service_healthy` faz o app esperar o `pg_isready` do banco.
- Entre no banco: `docker compose exec db psql -U contador` (saia com `\q`).

```bash
git add .
git commit -m "Passo 03: Compose com Postgres"
git push
```

Confira no GitHub: o `.env` **não** está lá.

🎯 **Exercício:** troque a `POSTGRES_PASSWORD` no `.env` e rode `docker compose up -d`. O app
consegue conectar? (Dica: o Postgres só usa essas variáveis na **primeira** vez, quando o volume
está vazio. Rode `docker compose down -v` e suba de novo.)

---

## Passo 04 — A tabela de usuários (10 min)

📁 [`passos/04_modelo_usuario/`](passos/04_modelo_usuario/) · 📖 [Modelos no Flask-SQLAlchemy](https://flask-sqlalchemy.readthedocs.io/en/stable/models/)

A classe `Usuario` vira a tabela `usuarios`: `id`, `nome` (único), `senha_hash` e `contador`. O
`db.create_all()` cria a tabela quando o app sobe.

```bash
docker compose up -d --build
docker compose exec db psql -U contador -c "\d usuarios"
```

**Os dados vivem no volume.** `docker compose down` remove os contêineres, mas o volume
`dados_postgres` fica; `docker compose down -v` apaga o volume junto.

```bash
git add .
git commit -m "Passo 04: modelo Usuario"
git push
```

🎯 **Exercício:** insira um usuário "na mão" com
`docker compose exec db psql -U contador -c "insert into usuarios (nome, senha_hash, contador) values ('teste', 'x', 5)"`
e veja o número em `/saude`. Depois rode `down` e `up`: ele continua lá? E com `down -v`?

---

## Passo 05 — Cadastro, login e logout (25 min)

📁 [`passos/05_login/`](passos/05_login/) · 📖 [Flask-Login](https://flask-login.readthedocs.io/en/latest/) · [Flask-WTF: formulários](https://flask-wtf.readthedocs.io/en/latest/form/) e [CSRF](https://flask-wtf.readthedocs.io/en/latest/csrf/) · [Templates](https://flask.palletsprojects.com/en/stable/tutorial/templates/) · [Segurança no Flask](https://flask.palletsprojects.com/en/stable/web-security/)

É o maior passo. Novos: a pasta `templates/` (páginas HTML), os formulários e as rotas
`/cadastro`, `/login` e `/logout`. O `.env.example` ganha a `SECRET_KEY`.

| Peça | Para que serve |
|---|---|
| `generate_password_hash` / `check_password_hash` (Werkzeug) | o banco guarda só o **hash** da senha, nunca a senha |
| `SECRET_KEY` | assina o cookie de sessão; quem a conhece se passa por qualquer usuário |
| Flask-Login (`login_user`, `@login_required`, `current_user`) | lembra quem está logado e protege as rotas |
| Flask-WTF (`FlaskForm`, `CSRFProtect`) | valida os formulários e exige um token **CSRF** em todo POST |
| `unique=True` + `IntegrityError` | o próprio banco recusa dois usuários com o mesmo nome |

Gere uma `SECRET_KEY` de verdade e coloque no seu `.env`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

```bash
docker compose up -d --build
```

Abra http://localhost:8000: você é mandado para o login. Crie uma conta e entre.

**O que observar**

- Olhe a senha no banco: `docker compose exec db psql -U contador -c "select nome, senha_hash from usuarios"`.
  É um hash `scrypt:...`, não a senha.
- Erre a senha e depois tente um usuário que não existe: a mensagem é **a mesma**, de propósito
  (não contamos a um atacante quais usuários existem).
- Veja o código-fonte da página de login (`Ctrl+U`): o `csrf_token` escondido está lá.
- O "Sair" é um **POST** com token, e não um link, para que outro site não consiga deslogar você.

```bash
git status                       # o .env continua de fora
git add .
git commit -m "Passo 05: cadastro e login"
git push
```

🎯 **Exercício:** exija senhas com pelo menos **10** caracteres (dica: o `Length` do
`FormCadastro`). Teste, faça commit e push.

---

## Passo 06 — O contador de cada usuário (15 min)

📁 [`passos/06_contador/`](passos/06_contador/) · 📖 [Métodos HTTP no Flask](https://flask.palletsprojects.com/en/stable/quickstart/#http-methods) · [UPDATE no SQLAlchemy](https://docs.sqlalchemy.org/en/20/tutorial/data_update.html)

Novas rotas `POST /incrementar` e `POST /decrementar`, só para quem está logado, e a página
inicial mostra o número.

**O que observar**

- A conta é feita **no banco** (`UPDATE usuarios SET contador = contador + 1 WHERE id = ...`). Ler
  o número no Python, somar e gravar pode perder um clique quando duas abas clicam ao mesmo tempo.
- As rotas são só **POST**: um GET (um link, um robô) nunca deve mudar dados.
- Abra uma **janela anônima**, crie outro usuário e clique: cada um tem o seu número.

```bash
docker compose up -d --build
docker compose exec db psql -U contador -c "select nome, contador from usuarios"
```

Primeira versão pronta: marque com uma **tag**.

```bash
git add .
git commit -m "Passo 06: contador por usuário"
git push
git tag v1.0
git push --tags
```

No GitHub, a tag aparece em **Releases/Tags**.

🎯 **Exercício:** crie um botão **Zerar**, que volta o contador do usuário para 0.

---

## Passo 07 — Pronto para produção (10 min)

📁 [`passos/07_producao/`](passos/07_producao/) · 📖 [Flask com gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/) · [Servidor de desenvolvimento](https://flask.palletsprojects.com/en/stable/server/)

O `app.run()` avisa no log: *"This is a development server. Do not use it in a production
deployment."* Neste passo:

- o contêiner roda o **gunicorn** com 2 workers (processos) em vez do `app.run()`;
- o app roda com um **usuário comum** (`USER app`), e não como root;
- o Compose ganha um **healthcheck** do app (que chama `/saude`) e `restart: unless-stopped`.

```bash
docker compose up -d --build
docker compose ps                # app fica "healthy" depois de alguns segundos
docker compose exec app whoami   # app, e não root
docker compose logs app          # "Booting worker with pid: ..." duas vezes
```

```bash
git add .
git commit -m "Passo 07: gunicorn e ajustes de produção"
git push
git log --oneline                # a história da aula, um commit por passo
```

🎯 **Exercício:** mude o número de workers para 4 e veja nos logs. Por que o app precisa do
`db.engine.dispose()` depois do `create_all()` (leia o comentário no `app.py`)?

---

## Limpeza

```bash
docker compose down -v           # contêineres, rede e dados
docker rmi contador:0.1          # a imagem do passo 02 (e a :0.2, se criou)
```

## Portas usadas

| Porta | Quem |
|---|---|
| 8000 | o app (no seu computador e no contêiner) |
| 5432 | o Postgres, **só** dentro da rede do Compose (não é publicada) |

## Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `Cannot connect to the Docker daemon` / `error during connect` | O Docker Desktop não está aberto. Abra e espere ficar pronto. |
| `port is already allocated` / `address already in use` | Outro programa usa a 8000 (ex.: o `python app.py` do passo 01 ainda rodando, ou o contêiner do passo 02). Pare-o ou troque o número da **esquerda** em `ports:`. |
| `KeyError: 'DATABASE_URL'` ao rodar `python app.py` | A partir do passo 03 o app precisa do banco: rode pelo `docker compose up`. |
| `required variable SECRET_KEY is missing a value: Defina SECRET_KEY no .env` | Falta a linha `SECRET_KEY=` no seu `.env` (ela entrou no passo 05). |
| `env file .env not found` | Você não criou o `.env`: `cp .env.example .env` (Mac) ou `copy .env.example .env` (Windows). |
| `password authentication failed` | Você mudou a senha no `.env` depois que o volume foi criado. `docker compose down -v` e suba de novo (apaga os dados). |
| `Bad Request: The CSRF token is missing` | O formulário não enviou o `csrf_token`. Confira o `{{ form.hidden_tag() }}` ou o `<input type="hidden" name="csrf_token" ...>`. |
| `git push` recusa a senha | Use o Git Credential Manager (Windows), o `gh auth login` ou um token de acesso pessoal (veja o passo 01). |
| `! [rejected] main -> main (fetch first)` | O repositório no GitHub tem um commit que você não tem (criou com README?). `git pull --rebase origin main` e depois `git push`. |
| Ficou para trás num passo | Copie a pasta do passo por cima do seu projeto: 🍎 `cp -R aulas/flask_postgres/passos/05_login/. ~/contador/` · 🪟 `Copy-Item -Recurse -Force aulas\flask_postgres\passos\05_login\* $HOME\contador\` |

## Status de validação

Executado no **macOS (Apple Silicon)** com Docker Engine 29: os passos 02 a 07 foram construídos e
testados com um script que cadastra dois usuários, testa login errado, rotas protegidas, CSRF
ausente (400) e contadores independentes. Os comandos são os mesmos no Windows, mas a aula **ainda
não foi executada numa máquina Windows**.
