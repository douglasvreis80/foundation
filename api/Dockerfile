# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto para o contêiner
COPY . .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Configurar o Flask para ouvir em todas as interfaces
ENV FLASK_RUN_HOST=0.0.0.0

# Expôr a porta 5000 para o Flask
EXPOSE 5000

# Comando para executar o aplicativo
CMD ["flask", "run"]