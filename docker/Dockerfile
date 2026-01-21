FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Jeśli repo ma requirements.txt, możesz później odkomentować:
# RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "cloud/uruchom_jedna_symulacje.py"]
