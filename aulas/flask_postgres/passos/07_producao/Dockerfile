# Referência do Dockerfile: https://docs.docker.com/reference/dockerfile/
# 1. Imagem base: Linux enxuto com Python já instalado.
FROM python:3.13-slim

# 2. Python sem buffer na saída (os logs aparecem na hora no `docker compose logs`)
#    e sem gravar arquivos .pyc dentro do contêiner.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Pasta de trabalho dentro da imagem (é criada se não existir).
WORKDIR /app

# 4. Primeiro só o requirements.txt, depois o pip install.
#    Enquanto as dependências não mudarem, o Docker reaproveita esta camada
#    do cache e o próximo build leva segundos.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Um usuário comum para rodar o app. Por padrão o contêiner roda como root:
#    se alguém invadir o app, ganha menos poder assim.
RUN useradd --create-home app

# 6. Agora o código, que muda o tempo todo.
COPY . .

USER app

# 7. Documenta a porta em que o app escuta (não publica nada sozinho).
EXPOSE 8000

# Flask com gunicorn: https://flask.palletsprojects.com/en/stable/deploying/gunicorn/
# Outras formas de colocar Flask em produção: https://flask.palletsprojects.com/en/stable/deploying/
# 8. Gunicorn: servidor de produção, com 2 processos (workers) atendendo em paralelo.
#    O servidor do `app.run()` é só para desenvolvimento.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--preload", "--access-logfile", "-", "app:app"]
