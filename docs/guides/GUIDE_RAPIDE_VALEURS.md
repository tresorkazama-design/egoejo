# ⚡ Guide Rapide - Trouver les Valeurs

**Version rapide** pour trouver les vraies valeurs des secrets.

---

## 🔗 Liens Directs

### Vercel
- **Token** : https://vercel.com/account/tokens → "Create Token"
- **Org ID** : https://vercel.com/[votre-org]/settings
- **Project ID** : https://vercel.com/[votre-org]/[votre-projet]/settings

### Railway
- **Token** : https://railway.app/account/tokens → "New Token"
- **Service ID** : https://railway.app/dashboard → Projet → Service → Settings

---

## 📋 Format des Valeurs

### Vercel
- **Token** : `vercel_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Org ID** : `team_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Project ID** : `prj_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Railway
- **Token** : `railway_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Service ID** : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (UUID)

---

## ✅ Django Secret Key

**Déjà configuré** : `XDPKsBrCrXD24_sGIli9_BeCG0HSXhiBVx6F8vbAERcFpd-qYGEWsXGk-BrOLAge8JM`

---

## 🚀 Configurer

```powershell
cd C:\Users\treso\Downloads\egoejo

gh secret set VERCEL_TOKEN --body "VOTRE-TOKEN"
gh secret set VERCEL_ORG_ID --body "VOTRE-ORG-ID"
gh secret set VERCEL_PROJECT_ID --body "VOTRE-PROJECT-ID"
gh secret set RAILWAY_TOKEN --body "VOTRE-TOKEN"
gh secret set RAILWAY_SERVICE_ID --body "VOTRE-SERVICE-ID"
```

---

**Guide détaillé** : `OU_TROUVER_LES_VRAIES_VALEURS.md`

