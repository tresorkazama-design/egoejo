# 🔧 Fix : Erreur Rollup sur Vercel

**Erreur** : `Cannot find module @rollup/rollup-linux-x64-gnu`

**Cause** : Problème avec les dépendances optionnelles de Rollup sur Vercel.

---

## ✅ Solution 1 : Ajouter la dépendance explicitement (Recommandé)

### Étape 1 : Ajouter dans `package.json`

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Ajouter la dépendance manquante
npm install --save-dev @rollup/rollup-linux-x64-gnu
```

### Étape 2 : Commit et Push

```powershell
cd C:\Users\treso\Downloads\egoejo
git add frontend/frontend/package.json frontend/frontend/package-lock.json
git commit -m "fix: ajouter @rollup/rollup-linux-x64-gnu pour Vercel"
git push origin main
```

### Étape 3 : Redéployer

Vercel redéploiera automatiquement après le push.

---

## ✅ Solution 2 : Modifier le Build Command dans Vercel

### Via l'interface web

1. Aller sur : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/general
2. **Build Command** : Changer de `npm run build` à :
   ```bash
   rm -rf node_modules package-lock.json && npm install && npm run build
   ```

### Via CLI

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Modifier vercel.json
```

---

## ✅ Solution 3 : Mettre à jour les dépendances

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Mettre à jour Vite et Rollup
npm update vite rollup

# Commit et push
cd ..\..
git add frontend/frontend/package.json frontend/frontend/package-lock.json
git commit -m "fix: mettre à jour vite et rollup"
git push origin main
```

---

## ✅ Solution 4 : Modifier `vercel.json`

Modifier `frontend/frontend/vercel.json` :

```json
{
  "buildCommand": "rm -rf node_modules package-lock.json && npm install && npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## 🚀 Solution Rapide (Recommandée)

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# 1. Ajouter la dépendance manquante
npm install --save-dev @rollup/rollup-linux-x64-gnu

# 2. Commit et push
cd ..\..
git add .
git commit -m "fix: ajouter @rollup/rollup-linux-x64-gnu pour Vercel"
git push origin main
```

Vercel redéploiera automatiquement.

---

## 📋 Checklist

- [ ] Dépendance `@rollup/rollup-linux-x64-gnu` ajoutée
- [ ] `package.json` et `package-lock.json` commités
- [ ] Push sur GitHub
- [ ] Vercel redéploie automatiquement
- [ ] Build réussi

---

**La Solution 1 (ajouter la dépendance) est la plus simple et recommandée !** ✅

