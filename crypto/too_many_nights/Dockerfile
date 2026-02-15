FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y socat && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pycryptodome

WORKDIR /app

COPY chall.py .
COPY secret.py .

RUN useradd -m -u 1000 ctf && \
    chown -R ctf:ctf /app

USER ctf

CMD ["python", "-u", "chall.py"]
