FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    numpy scipy matplotlib \
    typing_extensions \
    msgpack

COPY . /app

ENV PYTHONPATH=/app

CMD ["python", "cloud/uruchom_jedna_symulacje.py"]
