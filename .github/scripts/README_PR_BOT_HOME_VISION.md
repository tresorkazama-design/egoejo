# PR Bot - EGOEJO Compliant (Home/Vision)

## 📋 Description

Bot GitHub Actions qui vérifie automatiquement la conformité des pages Accueil et Vision lors de chaque Pull Request.

## 🚀 Fonctionnement

1. **Déclenchement** : Sur chaque événement `pull_request` (opened, synchronize, reopened)
2. **Audit** : Exécute `npm ci` puis `npm run audit:home-vision`
3. **Commentaire** : Poste un commentaire sur la PR avec le rapport détaillé
4. **Label** : Applique un label selon le statut :
   - 🟢 **EGOEJO Compliant** : Toutes les vérifications passent
   - 🟡 **EGOEJO Conditional** : Vérifications critiques OK, mais certaines non-critiques échouent
   - 🔴 **EGOEJO Non Compliant** : Au moins une violation détectée

## 🔧 Permissions Minimales

Le workflow utilise `GITHUB_TOKEN` avec les permissions suivantes :

```yaml
permissions:
  contents: read          # Lire le code
  pull-requests: write    # Commenter et gérer les labels des PR
  issues: write           # Créer/gérer les labels
```

**Note** : `GITHUB_TOKEN` est automatiquement fourni par GitHub Actions, aucune configuration supplémentaire n'est nécessaire.

## 📝 Gestion Idempotente

Le bot est **idempotent** : il met à jour le commentaire existant au lieu d'en créer plusieurs.

- **Identification** : Le bot identifie ses commentaires via le titre "Statut EGOEJO Compliant - Pages Accueil/Vision"
- **Mise à jour** : Si un commentaire existe déjà, il est mis à jour avec le nouveau statut
- **Création** : Si aucun commentaire n'existe, un nouveau est créé

## 📊 Format du Commentaire

Le commentaire inclut :

- **Statut** : Compliant / Conditional / Non Compliant
- **Résumé** : Nombre de violations détectées
- **Détails** : Liste des violations avec fichier, ligne, clé i18n, extrait, description
- **Timestamp** : Date et heure de l'audit

## 🏷️ Labels

Les labels sont automatiquement créés s'ils n'existent pas :

- **EGOEJO Compliant** (vert `#28a745`)
- **EGOEJO Conditional** (orange `#fbca04`)
- **EGOEJO Non Compliant** (rouge `#d73a4a`)

Les anciens labels de conformité sont automatiquement retirés avant d'ajouter le nouveau.

## 🔍 Tests Locaux

Pour tester le script localement :

```bash
cd frontend/frontend

# Exécuter l'audit
npm run audit:home-vision -- --json > audit-result.json

# Tester le PR bot
GITHUB_TOKEN=your_token \
PR_NUMBER=123 \
GITHUB_REPOSITORY=owner/repo \
node ../../.github/scripts/pr_bot_home_vision.js
```

## 📚 Fichiers

- **Workflow** : `.github/workflows/pr-bot-home-vision.yml`
- **Script** : `.github/scripts/pr_bot_home_vision.js`
- **Audit** : `frontend/frontend/scripts/audit-home-vision.mjs`

## ⚠️ Notes

- Le script d'audit doit être exécuté avec `--json` pour générer un format JSON lisible
- Le fichier `audit-result.json` est généré dans `frontend/frontend/` par le workflow
- Le script PR bot lit ce fichier pour générer le commentaire

