# Commandes PowerShell pour Fixer les Problèmes Git

# 1. Retirer le fichier vidéo du commit (trop gros pour GitHub)
cd C:\Users\treso\Downloads\egoejo

# Retirer le fichier du staging
git reset HEAD backend/media/projets/Umwami.mp4

# Ajouter à .gitignore pour ne pas le commiter
Add-Content .gitignore "`nbackend/media/projets/*.mp4"
Add-Content .gitignore "`nbackend/media/projets/*.mov"
Add-Content .gitignore "`nbackend/media/projets/*.avi"

# 2. Pour le frontend (submodule), il faut commit dans le submodule
cd frontend\frontend

# Ajouter la dépendance Rollup dans package.json manuellement
# OU laisser Vercel l'installer automatiquement (vercel.json utilise npm install)

# Commit dans le submodule
git add package.json package-lock.json vercel.json
git commit -m "fix: corriger erreur Rollup sur Vercel"
git push origin main

# Revenir au repo principal
cd ..\..

# Commit le changement de vercel.json (déjà fait)
git add frontend/frontend/vercel.json
git commit -m "fix: utiliser npm install au lieu de npm ci pour Vercel"
git push origin main

