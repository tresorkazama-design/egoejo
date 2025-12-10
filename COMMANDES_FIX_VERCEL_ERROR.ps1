# Commandes PowerShell pour Corriger les Erreurs Vercel

cd C:\Users\treso\Downloads\egoejo

# 1. Modifier vercel.json pour forcer npm install avant build
# (Déjà fait automatiquement)

# 2. Commit et push
git add frontend/frontend/vercel.json
git commit -m "fix: forcer npm install avant build sur Vercel"
git push origin main

# Vercel redéploiera automatiquement

