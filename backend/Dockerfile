FROM python:3.11-slim
# Installer netcat pour le script wait_for_db.sh
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
# Empêche Python de créer des fichiers .pyc et garde les logs visibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crée le répertoire de travail
WORKDIR /app

# Installe les dépendances système
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Copie et installe les dépendances Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie tout le code de l’application
COPY . /app/

# Copie le script qui attend la base de données
COPY wait_for_db.sh /wait_for_db.sh
RUN chmod +x /wait_for_db.sh

# Commande de démarrage : attendre la DB puis lancer Gunicorn
CMD ["/wait_for_db.sh", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
