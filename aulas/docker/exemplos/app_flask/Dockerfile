# 1. Imagem base: Linux enxuto com Python já instalado.
FROM python:3.13-slim

# 2. Pasta de trabalho dentro da imagem (é criada se não existir).
WORKDIR /app

# 3. Primeiro só o requirements.txt, depois o pip install.
#    Enquanto as dependências não mudarem, o Docker reaproveita esta camada
#    do cache e o build seguinte leva segundos.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Agora o código, que muda o tempo todo.
COPY . .

# 5. Documenta a porta em que o app escuta (não publica nada sozinho).
EXPOSE 5000

# 6. Valor padrão de configuração; o `docker run -e NOME=...` sobrescreve.
ENV NOME=Docker

# 7. Comando executado quando o contêiner sobe.
CMD ["python", "app.py"]
