# Étape 1 : Construction
# Utilise une image Node.js récente pour installer les dépendances et construire le projet.
FROM node:20-alpine as builder

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie package.json et package-lock.json pour installer les dépendances
COPY package.json .
COPY package-lock.json .

# Installe les dépendances Node.js
RUN npm install

# Copie le reste du code source
COPY . .

# Exécute la construction de l'application (les fichiers statiques prêts pour la production)
RUN npm run build

# Étape 2 : Service (Production)
# Utilise Nginx pour servir l'application de manière légère et rapide
FROM nginx:alpine

# Copie les fichiers construits à l'étape 1 dans le dossier de service de Nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Expose le port par défaut de Nginx
EXPOSE 80

# Commande pour démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]
