"""App mínimo para a aula de Docker.

Lê duas variáveis de ambiente (NOME e REDIS_HOST) para mostrar como a mesma
imagem muda de comportamento conforme a configuração recebida no `docker run`.
"""
import os
import socket

from flask import Flask

app = Flask(__name__)

NOME = os.getenv("NOME", "mundo")
REDIS_HOST = os.getenv("REDIS_HOST")  # só existe quando sobe pelo Compose

redis_client = None
if REDIS_HOST:
    import redis

    redis_client = redis.Redis(host=REDIS_HOST, port=6379)


@app.route("/")
def index():
    linhas = [
        f"Olá, {NOME}!",
        # O hostname de um contêiner é o próprio ID dele: prova de que estamos "lá dentro".
        f"Contêiner: {socket.gethostname()}",
    ]
    if redis_client:
        visitas = redis_client.incr("visitas")
        linhas.append(f"Visitas: {visitas}")
    return "\n".join(linhas) + "\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    # 0.0.0.0 = aceitar conexões de fora do contêiner. Com 127.0.0.1 a porta
    # publicada não funciona: o app só escutaria a si mesmo.
    app.run(host="0.0.0.0", port=5000)
