# 🧪 Guide - Tests E2E en Production

**Date** : 17 Décembre 2025  
**Objectif** : Exécuter les tests E2E contre l'environnement de production

---

## ⚠️ Précautions

### Avant d'exécuter les tests en production

1. **Ne pas surcharger le serveur** : Utiliser un seul worker
2. **Ne pas modifier les données** : Les tests doivent être en lecture seule
3. **Utiliser des mocks** : Mocker les API pour éviter les appels réels
4. **Timeouts plus longs** : La production peut être plus lente

---

## 🚀 Configuration

### Fichier : `playwright.production.config.js`

La configuration production est déjà créée avec :
- Timeout plus long (60s)
- Un seul worker (évite la surcharge)
- Base URL de production
- Vidéos et screenshots en cas d'échec

### Variables d'environnement

```bash
# Définir l'URL de production
export PLAYWRIGHT_BASE_URL=https://egoejo.org
# OU
export VITE_APP_URL=https://egoejo.org
```

---

## 📋 Exécution des Tests

### Exécuter tous les tests E2E en production

```bash
cd frontend/frontend
npx playwright test --config=playwright.production.config.js
```

### Exécuter un test spécifique

```bash
npx playwright test e2e/saka-cycle-visibility.spec.js --config=playwright.production.config.js
```

### Exécuter avec rapport HTML

```bash
npx playwright test --config=playwright.production.config.js --reporter=html
```

---

## 🔍 Vérifications

### 1. Vérifier que les mocks fonctionnent

Les tests doivent mocker toutes les API pour éviter :
- Les appels réels au backend
- La modification des données
- La dépendance à l'état du serveur

### 2. Vérifier les timeouts

Si les tests échouent avec des timeouts :
- Augmenter les timeouts dans `playwright.production.config.js`
- Vérifier la latence réseau
- Vérifier que le serveur répond correctement

### 3. Vérifier les sélecteurs

Si les tests échouent avec "element not found" :
- Vérifier que l'interface de production correspond à celle de développement
- Vérifier que les sélecteurs sont robustes
- Utiliser `page.screenshot()` pour voir l'état de la page

---

## 🐛 Dépannage

### Problème : Tests échouent avec "timeout"

**Solution** :
1. Augmenter les timeouts dans la config
2. Vérifier la latence réseau
3. Vérifier que le serveur répond

### Problème : Tests échouent avec "element not found"

**Solution** :
1. Vérifier que l'interface correspond
2. Utiliser des sélecteurs plus robustes
3. Ajouter des `waitForSelector` explicites

### Problème : Tests modifient les données

**Solution** :
1. Vérifier que tous les appels API sont mockés
2. Utiliser des comptes de test isolés
3. Nettoyer les données après les tests

---

## 📊 Résultats Attendus

### Tests SAKA Cycle Visibility

- ✅ **12/12 tests** doivent passer
- ✅ Tous les mocks doivent fonctionner
- ✅ Aucune modification de données

### Autres Tests E2E

- ✅ Tests d'authentification
- ✅ Tests de navigation
- ✅ Tests de projets
- ✅ Tests de votes

---

## 🔄 Intégration CI/CD

### GitHub Actions (Recommandé)

```yaml
name: E2E Production Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Tous les jours à 2h UTC

jobs:
  e2e-production:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd frontend/frontend && npm install
      - run: npx playwright install
      - run: npx playwright test --config=playwright.production.config.js
```

---

## 📝 Notes

- Les tests en production sont **complémentaires** aux tests locaux
- Ils vérifient que l'interface correspond à celle de développement
- Ils ne remplacent **pas** les tests locaux (plus rapides, plus fiables)

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide de référence

