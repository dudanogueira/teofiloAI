"""Contador por usuário — passo 03: o app conversa com o Postgres."""
import os

# Documentação do Flask: https://flask.palletsprojects.com/en/stable/
# Guia rápido (rotas, templates, formulários): https://flask.palletsprojects.com/en/stable/quickstart/
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Configuração do Flask: https://flask.palletsprojects.com/en/stable/config/
# A configuração vem de variáveis de ambiente, nunca escrita no código.
# Quem sobe pelo Compose recebe DATABASE_URL do docker-compose.yml.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

# Flask-SQLAlchemy (integração Flask + banco): https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
db = SQLAlchemy(app)


# Rotas: https://flask.palletsprojects.com/en/stable/quickstart/#routing
@app.route("/")
def inicio():
    return "Olá! Este é o começo do nosso projeto."


@app.route("/saude")
def saude():
    # Pergunta a versão ao Postgres: se responder, a conexão está funcionando.
    versao = db.session.execute(text("SELECT version()")).scalar()
    return {"banco": "ok", "versao": versao}


# Servidor de desenvolvimento do Flask: https://flask.palletsprojects.com/en/stable/server/
if __name__ == "__main__":
    # 0.0.0.0 = aceitar conexões de fora da máquina (vai importar no Docker).
    # Porta 8000, e não a 5000 padrão: no Mac a 5000 é do AirPlay Receiver.
    app.run(host="0.0.0.0", port=8000)
