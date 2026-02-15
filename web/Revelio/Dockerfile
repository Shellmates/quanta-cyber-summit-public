FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static

ENV PYTHONUNBUFFERED=1
ENV BOT_BASE_URL=http://127.0.0.1:5000

EXPOSE 5000

CMD ["python", "/app/app.py"]


