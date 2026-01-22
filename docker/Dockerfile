FROM python:3.11-slim

WORKDIR /app

# --- pakiety systemowe potrzebne matplotlib ---
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# --- python libs ---
RUN pip install --no-cache-dir \
    numpy \
    matplotlib

COPY . /app

CMD ["python", "cloud/uruchom_jedna_symulacje.py"]
