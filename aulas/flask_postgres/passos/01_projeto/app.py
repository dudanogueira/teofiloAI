"""Contador por usuário — passo 01: o menor app Flask possível."""
from flask import Flask

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Olá! Este é o começo do nosso projeto."


if __name__ == "__main__":
    # 0.0.0.0 = aceitar conexões de fora da máquina (vai importar no Docker).
    # Porta 8000, e não a 5000 padrão: no Mac a 5000 é do AirPlay Receiver.
    app.run(host="0.0.0.0", port=8000)
