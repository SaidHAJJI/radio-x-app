#!/bin/bash

# Nom du répertoire principal du projet
PROJECT_NAME="radio-x-app"

# Créer le répertoire principal
mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Créer les répertoires principaux
mkdir backend
mkdir frontend
mkdir docs
mkdir scripts
mkdir tests

# Créer les fichiers de base à la racine
touch README.md
touch .gitignore
touch docker-compose.yml

# Créer la structure et fichiers de base pour le backend (Flask)
mkdir backend/app
mkdir backend/tests
touch backend/app/__init__.py
touch backend/app/main.py
touch backend/requirements.txt
touch backend/Dockerfile
touch backend/.env.example

# Créer la structure et fichiers de base pour le frontend (React)
# (Note: La structure React est généralement créée avec create-react-app ou Vite,
# mais nous créons ici les répertoires de base pour Docker)
mkdir frontend/public
mkdir frontend/src
touch frontend/Dockerfile
touch frontend/.env.example
# On ajoutera un .dockerignore plus tard si besoin

# Ajouter du contenu initial simple aux fichiers
echo "# Application Web pour Lecture d'Images Radio X" > README.md

echo "# Fichiers et répertoires à ignorer par Git" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "node_modules/" >> .gitignore
echo "build/" >> .gitignore
echo "dist/" >> .gitignore
echo "*.log" >> .gitignore
echo ".DS_Store" >> .gitignore

echo "version: '3.8'" > docker-compose.yml
echo "" >> docker-compose.yml
echo "services:" >> docker-compose.yml
echo "  backend:" >> docker-compose.yml
echo "    build: ./backend" >> docker-compose.yml
echo "    ports:" >> docker-compose.yml
echo "      - \"5000:5000\" # Port exposé pour l'API Flask" >> docker-compose.yml
echo "    volumes:" >> docker-compose.yml
echo "      - ./backend:/app" >> docker-compose.yml
echo "    env_file:" >> docker-compose.yml
echo "      - ./backend/.env" >> docker-compose.yml
echo "" >> docker-compose.yml
echo "  frontend:" >> docker-compose.yml
echo "    build: ./frontend" >> docker-compose.yml
echo "    ports:" >> docker-compose.yml
echo "      - \"3000:3000\" # Port exposé pour l'app React (développement)" >> docker-compose.yml
echo "    volumes:" >> docker-compose.yml
echo "      - ./frontend:/app" >> docker-compose.yml
echo "      - /app/node_modules # Éviter l'écrasement de node_modules par le volume" >> docker-compose.yml
echo "    env_file:" >> docker-compose.yml
echo "      - ./frontend/.env" >> docker-compose.yml
echo "    stdin_open: true # Nécessaire pour create-react-app en mode interactif" >> docker-compose.yml
echo "    tty: true" >> docker-compose.yml

echo "# Backend Dockerfile (Exemple simple pour Flask)" > backend/Dockerfile
echo "FROM python:3.11-slim" >> backend/Dockerfile
echo "" >> backend/Dockerfile
echo "WORKDIR /app" >> backend/Dockerfile
echo "" >> backend/Dockerfile
echo "COPY requirements.txt requirements.txt" >> backend/Dockerfile
echo "RUN pip install --no-cache-dir -r requirements.txt" >> backend/Dockerfile
echo "" >> backend/Dockerfile
echo "COPY . ." >> backend/Dockerfile
echo "" >> backend/Dockerfile
echo "# Port par défaut pour Flask" >> backend/Dockerfile
echo "EXPOSE 5000" >> backend/Dockerfile
echo "" >> backend/Dockerfile
echo "# Commande pour lancer l'application (à adapter)" >> backend/Dockerfile
echo "CMD [\"flask\", \"run\", \"--host=0.0.0.0\"]" >> backend/Dockerfile

echo "# Frontend Dockerfile (Exemple simple pour React avec Vite)" > frontend/Dockerfile
echo "FROM node:20-alpine" >> frontend/Dockerfile
echo "" >> frontend/Dockerfile
echo "WORKDIR /app" >> frontend/Dockerfile
echo "" >> frontend/Dockerfile
echo "# Copier package.json et package-lock.json (ou yarn.lock)" >> frontend/Dockerfile
echo "COPY package*.json ./" >> frontend/Dockerfile
echo "" >> frontend/Dockerfile
echo "# Installer les dépendances" >> frontend/Dockerfile
echo "RUN npm install" >> frontend/Dockerfile
echo "" >> frontend/Dockerfile
echo "# Copier le reste du code de l'application" >> frontend/Dockerfile
echo "COPY . ." >> frontend/Dockerfile
echo "" >> frontend/Dockerfile
echo "# Port exposé par Vite" >> frontend/Dockerfile
echo "EXPOSE 3000" >> frontend/Dockerfile
echo "" >> frontend/Dockerfile
echo "# Commande pour lancer le serveur de développement" >> frontend/Dockerfile
echo "CMD [\"npm\", \"run\", \"dev\", \"--\", \"--host\"]" >> frontend/Dockerfile


echo "# Variables d'environnement pour le backend" > backend/.env.example
echo "FLASK_APP=app/main.py" >> backend/.env.example
echo "FLASK_ENV=development" >> backend/.env.example
echo "# SECRET_KEY=votre_cle_secrete_ici" >> backend/.env.example
echo "# DATABASE_URL=postgresql://user:password@host:port/database" >> backend/.env.example
echo "# IA_SERVICE_API_KEY=votre_cle_api_ia" >> backend/.env.example

echo "# Variables d'environnement pour le frontend" > frontend/.env.example
echo "# REACT_APP_BACKEND_URL=http://localhost:5000/api" >> frontend/.env.example
echo "# Ou pour Vite:" >> frontend/.env.example
echo "VITE_BACKEND_URL=http://localhost:5000/api" >> frontend/.env.example


echo "Structure du projet créée dans le répertoire '$PROJECT_NAME'"
