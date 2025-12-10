# 🔍 Diagnostic Erreurs Vercel - EGOEJO

**Problème** : Tous les déploiements échouent avec erreur

---

## 🔍 Étape 1 : Vérifier les Logs de Build

### Dans Vercel Dashboard

1. Aller sur : https://vercel.com/kazamas-projects-67d737b9/frontend
2. Cliquer sur un déploiement en erreur (ex: "GgqyT8sv4")
3. Aller dans l'onglet **"Build Logs"**
4. Chercher l'erreur à la fin des logs

### Erreurs Possibles

#### Erreur 1 : Rollup (encore)
```
Error: Cannot find module @rollup/rollup-linux-x64-gnu
```
**Solution** : Voir Solution 1 ci-dessous

#### Erreur 2 : Variables d'environnement
```
VITE_API_URL is not defined
```
**Solution** : Vérifier que `VITE_API_URL` est configuré dans Vercel

#### Erreur 3 : Build Command
```
Error: Command "npm run build" exited with 1
```
**Solution** : Vérifier la configuration du build

#### Erreur 4 : Root Directory
```
Error: Could not find a production build
```
**Solution** : Vérifier que `Root Directory` est `frontend/frontend`

---

## ✅ Solutions

### Solution 1 : Forcer l'Installation de Rollup

Modifier `package.json` pour forcer l'installation de toutes les dépendances optionnelles :

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Ajouter dans package.json (dans devDependencies)
# "@rollup/rollup-linux-x64-gnu": "^4.53.3"
```

**OU** modifier `vercel.json` pour forcer l'installation :

```json
{
  "installCommand": "npm install --include=optional",
  "buildCommand": "npm run build"
}
```

### Solution 2 : Vérifier la Configuration Vercel

**Dans Vercel Dashboard** → **Settings** → **General** :

- **Root Directory** : `frontend/frontend`
- **Build Command** : `npm run build`
- **Output Directory** : `dist`
- **Install Command** : `npm install` (pas `npm ci`)

### Solution 3 : Vérifier les Variables d'Environnement

**Dans Vercel Dashboard** → **Settings** → **Environment Variables** :

- ✅ `VITE_API_URL` doit être configuré pour **Production**
- ✅ Valeur : `https://egoejo-production.up.railway.app`

### Solution 4 : Modifier le Build Command

**Dans Vercel Dashboard** → **Settings** → **General** :

Changer **Build Command** de :
```bash
npm run build
```

À :
```bash
npm install && npm run build
```

---

## 🚀 Solution Rapide (Recommandée)

### Option A : Modifier `vercel.json`

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
```

Modifier `vercel.json` :

```json
{
  "buildCommand": "npm install && npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Puis commit et push :
```powershell
cd ..\..
git add frontend/frontend/vercel.json
git commit -m "fix: forcer npm install avant build sur Vercel"
git push origin main
```

### Option B : Via l'Interface Vercel

1. Aller sur : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/general
2. **Build Command** : Changer en `npm install && npm run build`
3. **Save**
4. **Redeploy** manuellement

---

## 📋 Checklist de Diagnostic

- [ ] Logs de build vérifiés dans Vercel
- [ ] Erreur identifiée
- [ ] Solution appliquée
- [ ] Redéploiement effectué
- [ ] Build réussi

---

**Vérifiez d'abord les logs pour identifier l'erreur exacte !** 🔍

