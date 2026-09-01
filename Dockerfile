FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libsm6 \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.docker.txt .

RUN pip install --no-cache-dir -r requirements.docker.txt

COPY app ./app
COPY scripts ./scripts

EXPOSE 8001

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]