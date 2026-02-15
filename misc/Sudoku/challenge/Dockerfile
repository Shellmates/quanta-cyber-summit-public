
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY model.py .
COPY checker.py .
COPY templates/ ./templates/

COPY model_correct.h5 .
COPY model_poisoned.h5 .

COPY train_models.py .

RUN echo '#!/bin/bash\n\
if [ ! -f "model_correct.h5" ] || [ ! -f "model_poisoned.h5" ]; then\n\
    echo "Models not found. Training models..."\n\
    python train_models.py\n\
fi\n\
echo "Starting Flask application..."\n\
python app.py' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["/app/start.sh"]
