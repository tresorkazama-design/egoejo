# Commandes PowerShell pour Configurer Vercel - EGOEJO

# Se placer dans le dossier frontend
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# 1. Nettoyer .env.local (garder seulement VITE_API_URL avec https://)
@"
# Created by Vercel CLI
VERCEL_OIDC_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im1yay00MzAyZWMxYjY3MGY0OGE5OGFkNjFkYWRlNGEyM2JlNyJ9.eyJpc3MiOiJodHRwczovL29pZGMudmVyY2VsLmNvbS9rYXphbWFzLXByb2plY3RzLTY3ZDczN2I5Iiwic3ViIjoib3duZXI6a2F6YW1hcy1wcm9qZWN0cy02N2Q3MzdiOTpwcm9qZWN0OmZyb250ZW5kOmVudmlyb25tZW50OmRldmVsb3BtZW50Iiwic2NvcGUiOiJvd25lcjprYXphbWFzLXByb2plY3RzLTY3ZDczN2I5OnByb2plY3Q6ZnJvbnRlbmQ6ZW52aXJvbm1lbnQ6ZGV2ZWxvcG1lbnQiLCJhdWQiOiJodHRwczovL3ZlcmNlbC5jb20va2F6YW1hcy1wcm9qZWN0cy02N2Q3MzdiOSIsIm93bmVyIjoia2F6YW1hcy1wcm9qZWN0cy02N2Q3MzdiOSIsIm93bmVyX2lkIjoidGVhbV8waVdrSHFvRWxCOUxyeTFkUmNpM3NHMVMiLCJwcm9qZWN0IjoiZnJvbnRlbmQiLCJwcm9qZWN0X2lkIjoicHJqX2JhbFlrMlVTMVlaS3ZaRU1VODRBS0JTdE5TRkIiLCJlbnZpcm9ubWVudCI6ImRldmVsb3BtZW50IiwicGxhbiI6ImhvYmJ5IiwidXNlcl9pZCI6IkNqSVJSazRLcFdudkV3QUo2eVpBamppSCIsIm5iZiI6MTc2NDc5NzU3MCwiaWF0IjoxNzY0Nzk3NTcwLCJleHAiOjE3NjQ4NDA3NzB9.dWouuAfy0c26Hz3j2Y5ThUiL3zz25MqU9R-rQK8quCCPAqZ2M1iaFonkjN80r6zCUVL-JHIJIr47tN6wkobZMPwoSLbofwNys91KAYhRMLSJSp1vWYrYZswCIvcasR7fDWJyg8KGU6lN_kxyepcAeNJS62EvDfjweDfcSZ7YXV4hEeAN1eGhjnAIugcYPQaYA88EOFmb9UM6u1cx6rbnwaTP2CUJKkm-a0ZwhkVpV0PZK4w-Fv5TcKMtKvLwz-oLzoQv45pHIuoul9NkoneyD8x3bFzgabbd3dpuCXNvp8EykZrTQnkjLBofjioifol9TZq8uStgJ1QKZQKhQk-XvQ"

# API Backend (URL de votre backend Railway)
VITE_API_URL=https://egoejo-production.up.railway.app
"@ | Set-Content .env.local -Encoding UTF8

# 2. Supprimer l'ancienne variable en production
vercel env rm VITE_API_URL production

# 3. Ajouter VITE_API_URL pour la production
# (Répondre "no" à "Mark as sensitive?")
vercel env add VITE_API_URL production

# 4. Ajouter VITE_API_URL pour preview
# (Répondre "no" à "Mark as sensitive?")
vercel env add VITE_API_URL preview

# 5. Ajouter VITE_API_URL pour development (optionnel)
# (Répondre "no" à "Mark as sensitive?")
vercel env add VITE_API_URL development

# 6. Vérifier les variables configurées
vercel env ls

# 7. Déployer en production
vercel --prod

# OU déploiement preview (test)
# vercel

