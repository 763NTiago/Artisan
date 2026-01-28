# Utilizando imagem slim para reduzir o tamanho final e aumentar a segurança
FROM python:3.11-slim

# Evita arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema para PostgreSQL e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cache e instalação das dependências Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o código-fonte do projeto Artisan
COPY . /app/

# Porta padrão
EXPOSE 8000

# Comando padrão de execução (pode ser sobrescrito pelo docker-compose)
CMD ["gunicorn", "artisan.wsgi:application", "--bind", "0.0.0.0:8000"]