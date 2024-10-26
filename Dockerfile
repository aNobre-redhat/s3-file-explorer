FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Use Gunicorn para rodar a aplicação em produção
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
