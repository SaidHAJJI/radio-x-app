# Backend Dockerfile (Exemple simple pour Flask)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port par défaut pour Flask
EXPOSE 5000

# Commande pour lancer l'application (à adapter)
CMD ["flask", "run", "--host=0.0.0.0"]
