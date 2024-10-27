# Usando uma imagem Python 3.9 como base
FROM python:3.9-slim

# Definindo o diretório de trabalho dentro do container
WORKDIR /app

# Copiando os arquivos de requisitos e instalando as dependências
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copiando o restante da aplicação para o diretório de trabalho
COPY . .

# Expondo a porta 5000
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
