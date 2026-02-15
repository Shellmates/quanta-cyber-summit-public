FROM python:3.11-slim

WORKDIR /app

RUN useradd -m ctf
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

# Le flag est écrit dans /app/flag au démarrage (voir entrypoint)
ENV FLAG=shellmates{s7i_byp4ss_v1a_c0nt3xt_p0llut10n}
ENV PYTHONUNBUFFERED=1

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R ctf:ctf /app

USER ctf
EXPOSE 3000
ENTRYPOINT ["/entrypoint.sh"]
