# 🔧 Fix : Root Directory Vercel

**Erreur** : `Could not read package.json: Error: ENOENT: no such file or directory, open '/vercel/path0/frontend/package.json'`

**Cause** : Vercel cherche `package.json` dans `frontend/` mais il est dans `frontend/frontend/`

---

## ✅ Solution : Configurer le Root Directory

### Option 1 : Via l'Interface Vercel (Recommandé)

1. **Aller sur** : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/general
2. **Scroller jusqu'à** "Root Directory"
3. **Cliquer sur** "Edit"
4. **Entrer** : `frontend/frontend`
5. **Cliquer sur** "Save"
6. **Redeploy** manuellement ou attendre le prochain push

### Option 2 : Via `vercel.json`

Le Root Directory peut aussi être configuré dans `vercel.json` à la racine du projet.

Créer `vercel.json` à la racine :

```json
{
  "buildCommand": "cd frontend/frontend && npm install && npm run build",
  "outputDirectory": "frontend/frontend/dist",
  "installCommand": "cd frontend/frontend && npm install"
}
```

**OU** utiliser la configuration dans `frontend/frontend/vercel.json` et configurer le Root Directory dans l'interface.

---

## 🚀 Solution Rapide

### Via l'Interface Vercel

1. **Aller sur** : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/general
2. **Root Directory** : `frontend/frontend`
3. **Save**
4. **Redeploy**

---

## 📋 Configuration Complète Vercel

Dans **Settings** → **General** :

- **Root Directory** : `frontend/frontend` ✅
- **Build Command** : `npm run build` (ou `npm install && npm run build`)
- **Output Directory** : `dist`
- **Install Command** : `npm install`
- **Framework Preset** : `Vite`

---

## ⚠️ Note sur les Submodules

Le warning "Failed to fetch one or more git submodules" peut être ignoré si le frontend n'est pas un vrai submodule Git, ou il faut configurer les submodules dans Vercel.

---

**Une fois le Root Directory configuré, le build devrait fonctionner !** ✅

