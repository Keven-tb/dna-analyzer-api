# Imagem base oficial, variante "slim" (enxuta)
FROM python:3.12-slim

# Diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia primeiro apenas o requirements.txt e instala as dependências.
# Isso aproveita o cache de camadas do Docker: se o código da aplicação
# mudar mas as dependências não, esta camada não precisa ser reconstruída.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Agora copia o restante do código da aplicação
COPY . .

# Variável de ambiente lida pela aplicação (app.py usa DATA_DIR)
ENV DATA_DIR=/app/data

# Porta em que o serviço escuta
EXPOSE 8000

# Declara /app/data como um volume: sinaliza que esse diretório deve ser
# gerenciado fora do sistema de arquivos "descartável" do contêiner
VOLUME /app/data

# Comando que inicia o servidor
CMD ["python", "app.py"]
