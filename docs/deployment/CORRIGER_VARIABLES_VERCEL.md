# 🔧 Corriger les Variables Vercel - EGOEJO

**Problèmes rencontrés** :
1. `VITE_API_URL` existe déjà en production
2. Variable "sensitive" ne peut pas être utilisée en development
3. Doublons dans `.env.local`

---

## ✅ Solution

### 1. Nettoyer `.env.local`

Le fichier `.env.local` contient probablement plusieurs entrées `VITE_API_URL`. Il faut le nettoyer :

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Créer un nouveau .env.local propre
@"
# Created by Vercel CLI
VERCEL_OIDC_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im1yay00MzAyZWMxYjY3MGY0OGE5OGFkNjFkYWRlNGEyM2JlNyJ9.eyJpc3MiOiJodHRwczovL29pZGMudmVyY2VsLmNvbS9rYXphbWFzLXByb2plY3RzLTY3ZDczN2I5Iiwic3ViIjoib3duZXI6a2F6YW1hcy1wcm9qZWN0cy02N2Q3MzdiOTpwcm9qZWN0OmZyb250ZW5kOmVudmlyb25tZW50OmRldmVsb3BtZW50Iiwic2NvcGUiOiJvd25lcjprYXphbWFzLXByb2plY3RzLTY3ZDczN2I5OnByb2plY3Q6ZnJvbnRlbmQ6ZW52aXJvbm1lbnQ6ZGV2ZWxvcG1lbnQiLCJhdWQiOiJodHRwczovL3ZlcmNlbC5jb20va2F6YW1hcy1wcm9qZWN0cy02N2Q3MzdiOSIsIm93bmVyIjoia2F6YW1hcy1wcm9qZWN0cy02N2Q3MzdiOSIsIm93bmVyX2lkIjoidGVhbV8waVdrSHFvRWxCOUxyeTFkUmNpM3NHMVMiLCJwcm9qZWN0IjoiZnJvbnRlbmQiLCJwcm9qZWN0X2lkIjoicHJqX2JhbFlrMlVTMVlaS3ZaRU1VODRBS0JTdE5TRkIiLCJlbnZpcm9ubWVudCI6ImRldmVsb3BtZW50IiwicGxhbiI6ImhvYmJ5IiwidXNlcl9pZCI6IkNqSVJSazRLcFdudkV3QUo2eVpBamppSCIsIm5iZiI6MTc2NDc5NzU3MCwiaWF0IjoxNzY0Nzk3NTcwLCJleHAiOjE3NjQ4NDA3NzB9.dWouuAfy0c26Hz3j2Y5ThUiL3zz25MqU9R-rQK8quCCPAqZ2M1iaFonkjN80r6zCUVL-JHIJIr47tN6wkobZMPwoSLbofwNys91KAYhRMLSJSp1vWYrYZswCIvcasR7fDWJyg8KGU6lN_kxyepcAeNJS62EvDfjweDfcSZ7YXV4hEeAN1eGhjnAIugcYPQaYA88EOFmb9UM6u1cx6rbnwaTP2CUJKkm-a0ZwhkVpV0PZK4w-Fv5TcKMtKvLwz-oLzoQv45pHIuoul9NkoneyD8x3bFzgabbd3dpuCXNvp8EykZrTQnkjLBofjioifol9TZq8uStgJ1QKZQKhQk-XvQ"

# API Backend (URL de votre backend Railway)
VITE_API_URL=https://egoejo-production.up.railway.app
"@ | Set-Content .env.local -Encoding UTF8
```

**OU** éditer manuellement `.env.local` et garder seulement :
```bash
VERCEL_OIDC_TOKEN=...
VITE_API_URL=https://egoejo-production.up.railway.app
```

**⚠️ Important** : Utiliser `https://` (pas juste le domaine).

---

### 2. Mettre à Jour la Variable en Production

La variable existe déjà, il faut la **mettre à jour** :

```powershell
# Mettre à jour pour la production
vercel env rm VITE_API_URL production
vercel env add VITE_API_URL production
# Entrer : https://egoejo-production.up.railway.app
# Répondre "no" à "Mark as sensitive?" (pas besoin pour une URL)
```

**OU** via l'interface web :
1. Aller sur : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/environment-variables
2. Trouver `VITE_API_URL` pour "Production"
3. Cliquer sur **"Edit"** ou **"Remove"** puis **"Add New"**
4. **Key** : `VITE_API_URL`
5. **Value** : `https://egoejo-production.up.railway.app`
6. **Environments** : ✅ Production
7. **Ne pas cocher** "Sensitive" (pas nécessaire pour une URL)

---

### 3. Ajouter pour Preview

```powershell
# Ajouter pour preview (sans marquer comme sensitive)
vercel env add VITE_API_URL preview
# Entrer : https://egoejo-production.up.railway.app
# Répondre "no" à "Mark as sensitive?"
```

---

### 4. Ajouter pour Development

**⚠️ Important** : Les variables "sensitive" ne peuvent pas être utilisées en development.

**Solution** : Ne pas marquer comme sensitive :

```powershell
# Ajouter pour development (sans marquer comme sensitive)
vercel env add VITE_API_URL development
# Entrer : http://localhost:8000/api
# Répondre "no" à "Mark as sensitive?"
```

**OU** utiliser directement `.env.local` pour le développement local (déjà fait).

---

## ✅ Vérification

### Vérifier les Variables dans Vercel

```powershell
# Lister toutes les variables
vercel env ls
```

**Devrait afficher** :
```
VITE_API_URL (Production)
VITE_API_URL (Preview)
VITE_API_URL (Development)
```

### Vérifier `.env.local`

```powershell
Get-Content .env.local
```

**Devrait contenir** :
```bash
VERCEL_OIDC_TOKEN=...
VITE_API_URL=https://egoejo-production.up.railway.app
```

---

## 🚀 Déployer

Une fois les variables configurées :

```powershell
# Déploiement en production
vercel --prod

# OU déploiement preview (test)
vercel
```

---

## 📋 Checklist

- [ ] `.env.local` nettoyé (une seule entrée `VITE_API_URL` avec `https://`)
- [ ] `VITE_API_URL` mis à jour dans Vercel (Production)
- [ ] `VITE_API_URL` ajouté dans Vercel (Preview)
- [ ] `VITE_API_URL` ajouté dans Vercel (Development) - optionnel
- [ ] Variables vérifiées avec `vercel env ls`
- [ ] Déploiement réussi

---

## 💡 Notes

### Pourquoi ne pas marquer comme "Sensitive" ?

- Les URLs d'API ne sont pas vraiment "sensibles" (pas de secrets)
- Les variables "sensitive" ne peuvent pas être utilisées en development
- Pour une URL publique, ce n'est pas nécessaire

### Si vous voulez quand même la marquer comme sensitive

C'est possible pour Production et Preview, mais **pas pour Development** :
- Production : ✅ Peut être sensitive
- Preview : ✅ Peut être sensitive
- Development : ❌ Ne peut pas être sensitive

---

## 📚 Documentation

- `CONFIGURER_VITE_API_URL.md` - Guide initial
- `SUITE_DEPLOIEMENT_FRONTEND.md` - Guide complet

---

**Une fois les variables corrigées, vous pouvez déployer !** ✅

