# Commandes PowerShell pour Fixer l'Erreur Rollup sur Vercel

# Se placer dans le dossier frontend
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Solution 1 : Ajouter la dépendance manquante (Recommandé)
npm install --save-dev @rollup/rollup-linux-x64-gnu

# Commit et push
cd ..\..
git add frontend/frontend/package.json frontend/frontend/package-lock.json
git commit -m "fix: ajouter @rollup/rollup-linux-x64-gnu pour Vercel"
git push origin main

# Vercel redéploiera automatiquement après le push

