# Contador

App Flask em que cada usuário faz login e controla o seu próprio contador.

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac
pip install -r requirements.txt
python app.py
```

Abra http://localhost:8000

## Rodando com Docker

```bash
docker build -t contador:0.1 .
docker run --rm -p 8000:8000 contador:0.1
```
