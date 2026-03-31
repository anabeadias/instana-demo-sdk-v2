FROM python:3.11-slim

WORKDIR /app

# copiar requirements primeiro (melhor cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copiar o resto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]