# Contador

App Flask em que cada usuário cria uma conta, faz login e controla o **seu próprio** contador
(+1 / −1). Roda em Docker: uma imagem com o app (Flask + gunicorn) e um Postgres, ligados pelo
Docker Compose.

## Rodando

```bash
cp .env.example .env            # Mac   (no Windows: copy .env.example .env)
# edite o .env: troque a senha do banco e a SECRET_KEY
docker compose up -d --build
```

Abra http://localhost:8000, crie uma conta em **Cadastre-se** e entre.
A rota http://localhost:8000/saude mostra se o banco está respondendo.

| Comando | O que faz |
|---|---|
| `docker compose ps` | mostra os serviços e se estão saudáveis |
| `docker compose logs -f app` | acompanha os logs do app |
| `docker compose exec db psql -U contador -c "select nome, contador from usuarios"` | olha a tabela direto no Postgres |
| `docker compose down` | para tudo (os dados ficam no volume) |
| `docker compose down -v` | para tudo e **apaga** os dados |

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `app.py` | o app: modelo `Usuario`, cadastro, login, logout e o contador |
| `templates/` | as páginas HTML (Jinja) |
| `requirements.txt` | dependências do Python |
| `Dockerfile` | receita da imagem do app |
| `docker-compose.yml` | app + Postgres, rede e volume |
| `.env.example` | modelo das variáveis secretas (o `.env` de verdade não vai para o git) |

## Documentação

- Flask: https://flask.palletsprojects.com/en/stable/
- Flask-SQLAlchemy: https://flask-sqlalchemy.readthedocs.io/en/stable/
- Flask-Login: https://flask-login.readthedocs.io/en/latest/
- Flask-WTF: https://flask-wtf.readthedocs.io/en/latest/
- Flask + gunicorn: https://flask.palletsprojects.com/en/stable/deploying/gunicorn/
- Docker Compose: https://docs.docker.com/reference/compose-file/services/
