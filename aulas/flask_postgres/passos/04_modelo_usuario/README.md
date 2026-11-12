# Contador

App Flask em que cada usuário faz login e controla o seu próprio contador.

## Rodando com Docker Compose (app + Postgres)

```bash
cp .env.example .env            # Mac   (no Windows: copy .env.example .env)
docker compose up -d --build
```

Abra http://localhost:8000 e http://localhost:8000/saude

Para ver a tabela criada pelo app, direto no Postgres:

```bash
docker compose exec db psql -U contador -c "\d usuarios"
```

Para parar: `docker compose down` (os dados ficam) ou `docker compose down -v` (apaga os dados).
