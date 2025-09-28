FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/

# Criar diretório para banco de dados
RUN mkdir -p src/database

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "src/main.py"]
