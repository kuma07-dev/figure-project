FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 先安裝套件，程式碼改動時可以沿用這一層的快取
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 不用 root 執行
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
