"""Contador por usuário — passo 04: a tabela de usuários."""
import os

# Documentação do Flask: https://flask.palletsprojects.com/en/stable/
# Guia rápido (rotas, templates, formulários): https://flask.palletsprojects.com/en/stable/quickstart/
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)

# Configuração do Flask: https://flask.palletsprojects.com/en/stable/config/
# A configuração vem de variáveis de ambiente, nunca escrita no código.
# Quem sobe pelo Compose recebe DATABASE_URL do docker-compose.yml.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

# Flask-SQLAlchemy (integração Flask + banco): https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
db = SQLAlchemy(app)


# Modelos e tabelas: https://flask-sqlalchemy.readthedocs.io/en/stable/models/
class Usuario(db.Model):
    """Uma linha da tabela `usuarios`. Cada usuário tem o seu próprio contador."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True)
    # Guardamos só o *hash* da senha, nunca a senha em si (veremos no passo 05).
    senha_hash: Mapped[str] = mapped_column(String(255))
    contador: Mapped[int] = mapped_column(default=0)


# create_all: https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/#create-the-tables
# Cria as tabelas que ainda não existem (as que já existem ficam como estão).
with app.app_context():
    db.create_all()


# Rotas: https://flask.palletsprojects.com/en/stable/quickstart/#routing
@app.route("/")
def inicio():
    return "Olá! Este é o começo do nosso projeto."


@app.route("/saude")
def saude():
    # Pergunta a versão ao Postgres: se responder, a conexão está funcionando.
    versao = db.session.execute(text("SELECT version()")).scalar()
    usuarios = db.session.execute(text("SELECT count(*) FROM usuarios")).scalar()
    return {"banco": "ok", "versao": versao, "usuarios": usuarios}


# Servidor de desenvolvimento do Flask: https://flask.palletsprojects.com/en/stable/server/
if __name__ == "__main__":
    # 0.0.0.0 = aceitar conexões de fora da máquina (vai importar no Docker).
    # Porta 8000, e não a 5000 padrão: no Mac a 5000 é do AirPlay Receiver.
    app.run(host="0.0.0.0", port=8000)
