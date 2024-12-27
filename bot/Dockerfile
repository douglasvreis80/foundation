# Use a imagem base personalizada que já contém os componentes do whatsapp-web.js
FROM douglasvreis80/alert-messenger:1.1

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos da aplicação para o contêiner
COPY . /app

# Instala as dependências necessárias
RUN npm install

# Define a variável de ambiente para a URL da API (pode ser sobrescrita no runtime)
ENV API_URL=http://localhost:5000

# Expõe a porta usada pelo whatsapp-web.js (se necessário para debugging)
EXPOSE 3000

# Comando para iniciar a aplicação
CMD ["node", "app.js"]
