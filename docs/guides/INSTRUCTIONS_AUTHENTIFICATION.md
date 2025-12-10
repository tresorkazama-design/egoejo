# 🔐 Instructions d'Authentification GitHub CLI

**Problème** : Vous voyez `To get started with GitHub CLI, please run: gh auth login`

---

## ✅ Solution Rapide

### Étape 1 : Se connecter à GitHub CLI

```powershell
cd C:\Users\treso\Downloads\egoejo
gh auth login
```

**Suivre les instructions** :
1. Choisir `GitHub.com`
2. Choisir `HTTPS`
3. Choisir `Login with a web browser`
4. Appuyer sur `Enter`
5. Autoriser dans le navigateur
6. Revenir au terminal

### Étape 2 : Vérifier la connexion

```powershell
gh auth status
```

**Résultat attendu** :
```
✓ Logged in to github.com as [votre-username]
```

### Étape 3 : Configurer les secrets

```powershell
# Utiliser le script automatisé (recommandé)
.\config-secrets.ps1

# OU configurer manuellement
gh secret set VERCEL_TOKEN --body "votre-token-vercel"
gh secret set VERCEL_ORG_ID --body "votre-org-id"
gh secret set VERCEL_PROJECT_ID --body "votre-project-id"
gh secret set RAILWAY_TOKEN --body "votre-token-railway"
gh secret set RAILWAY_SERVICE_ID --body "votre-service-id"
gh secret set DJANGO_SECRET_KEY --body "XDPKsBrCrXD24_sGIli9_BeCG0HSXhiBVx6F8vbAERcFpd-qYGEWsXGk-BrOLAge8JM"
```

---

## 📋 Checklist

- [ ] Exécuter `gh auth login`
- [ ] Vérifier avec `gh auth status`
- [ ] Configurer les secrets avec `.\config-secrets.ps1`
- [ ] Vérifier avec `gh secret list`

---

**Une fois authentifié, tout fonctionnera !** ✅

