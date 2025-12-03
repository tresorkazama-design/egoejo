# Commandes PowerShell pour Fixer les Problèmes Git - FINAL

cd C:\Users\treso\Downloads\egoejo

# 1. Retirer le fichier vidéo du dernier commit
git reset --soft HEAD~1

# 2. Retirer le fichier vidéo du staging
git reset HEAD backend/media/projets/Umwami.mp4

# 3. Le .gitignore a déjà été mis à jour pour exclure les fichiers vidéo

# 4. Commit sans le fichier vidéo
git add .
git commit -m "fix: corriger erreur Rollup sur Vercel (sans fichier vidéo)"

# 5. Push
git push origin main

# Note: La dépendance Rollup sera installée automatiquement sur Vercel
# car vercel.json utilise maintenant "npm install" au lieu de "npm ci"

