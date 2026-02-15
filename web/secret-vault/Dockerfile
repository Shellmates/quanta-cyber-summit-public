FROM python:3.11-slim

WORKDIR /app

RUN useradd -m ctf
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

ENV FLAG=shellmates{jwt_n0n3_4lg_1s_d4ng3r0us}
ENV PYTHONUNBUFFERED=1

USER ctf
EXPOSE 3000
CMD ["python", "app.py"]
