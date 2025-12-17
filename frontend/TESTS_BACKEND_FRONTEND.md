# 🔌 Tests de Connexion Backend-Frontend

## 📋 Vue d'ensemble

Ce document décrit les tests créés pour vérifier la connexion entre le backend Django et le frontend React.

---

## 🧪 Types de tests

### 1. **Tests unitaires avec mocks** (`backend-connection.test.js`)

**Fichier** : `src/utils/__tests__/backend-connection.test.js`

**Objectif** : Tester la logique de connexion sans nécessiter le backend réel.

**Tests inclus** :
- ✅ Configuration de l'URL API
- ✅ Health check (avec mock)
- ✅ Appels aux endpoints principaux
- ✅ Gestion des erreurs réseau
- ✅ Format des requêtes (headers, JSON)
- ✅ Authentification (token)

**Commande** :
```bash
npm run test:backend
```

**Avantages** :
- ✅ Rapides à exécuter
- ✅ Ne nécessitent pas le backend
- ✅ Testent la logique de connexion

---

### 2. **Tests d'intégration réels** (`integration-backend.test.js`)

**Fichier** : `src/utils/__tests__/integration-backend.test.js`

**Objectif** : Tester la connexion réelle avec le backend Django.

**Prérequis** :
- Backend Django démarré sur `http://127.0.0.1:8000`
- Base de données initialisée

**Tests inclus** :
- ✅ Health check réel
- ✅ Récupération des projets
- ✅ Soumission d'intentions
- ✅ Gestion des erreurs HTTP

**Commande** :
```bash
# Démarrer le backend d'abord
cd ../../backend
python manage.py runserver

# Dans un autre terminal, lancer les tests
cd frontend/frontend
npm run test:integration
```

**Note** : Ces tests sont automatiquement ignorés si le backend n'est pas disponible (`BACKEND_AVAILABLE=false`).

---

### 3. **Tests E2E avec Playwright** (`backend-connection.spec.js`)

**Fichier** : `e2e/backend-connection.spec.js`

**Objectif** : Tester la connexion backend-frontend dans un environnement de navigateur réel.

**Tests inclus** :
- ✅ Chargement de la page Projets avec connexion API
- ✅ Soumission du formulaire Rejoindre
- ✅ Gestion des erreurs de connexion
- ✅ Vérification des headers CORS
- ✅ Authentification dans Admin

**Commande** :
```bash
# Avec backend démarré
npm run test:e2e:backend

# Ou tous les tests E2E
npm run test:e2e
```

**Avantages** :
- ✅ Testent le comportement réel dans le navigateur
- ✅ Vérifient les interactions utilisateur
- ✅ Détectent les problèmes CORS

---

## 🚀 Guide d'utilisation

### Scénario 1 : Tests rapides (sans backend)

Pour tester rapidement la logique de connexion :

```bash
npm run test:backend
```

Ces tests utilisent des mocks et ne nécessitent pas le backend.

---

### Scénario 2 : Tests complets (avec backend)

Pour tester la connexion réelle :

1. **Démarrer le backend** :
```bash
cd ../../backend
python manage.py runserver
```

2. **Lancer les tests d'intégration** :
```bash
cd frontend/frontend
npm run test:integration
```

3. **Lancer les tests E2E** :
```bash
npm run test:e2e:backend
```

---

### Scénario 3 : CI/CD

Dans un environnement CI/CD, vous pouvez :

1. **Démarrer le backend en arrière-plan**
2. **Attendre qu'il soit prêt**
3. **Lancer les tests d'intégration**

Exemple de script CI :
```bash
# Démarrer le backend
cd backend && python manage.py runserver &
BACKEND_PID=$!

# Attendre que le backend soit prêt
sleep 5

# Lancer les tests
cd frontend/frontend
npm run test:integration
npm run test:e2e:backend

# Arrêter le backend
kill $BACKEND_PID
```

---

## 🔍 Vérifications effectuées

### Configuration
- ✅ URL de base de l'API correcte
- ✅ Format des endpoints
- ✅ Headers par défaut

### Connexion
- ✅ Health check fonctionnel
- ✅ Réponses JSON valides
- ✅ Gestion des erreurs réseau

### Endpoints
- ✅ GET `/api/projets/` - Liste des projets
- ✅ POST `/api/intents/rejoindre/` - Soumission d'intentions
- ✅ Authentification avec token

### Erreurs
- ✅ Erreurs réseau (timeout, CORS)
- ✅ Erreurs HTTP (404, 500)
- ✅ Gestion gracieuse des erreurs

---

## 🐛 Dépannage

### Problème : "Backend non disponible"

**Solution** : Vérifier que le backend est démarré :
```bash
cd backend
python manage.py runserver
```

Vérifier que l'URL est correcte dans `src/utils/api.js` :
```javascript
export const API_BASE = 'http://127.0.0.1:8000/api';
```

---

### Problème : "CORS policy error"

**Solution** : Configurer CORS dans Django :

```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

---

### Problème : "Network error: Failed to fetch"

**Solution** : 
1. Vérifier que le backend écoute sur le bon port
2. Vérifier les règles de firewall
3. Vérifier que l'URL dans `api.js` correspond

---

## 📊 Résultats attendus

### Tests unitaires (mocks)
- ✅ Tous les tests doivent passer
- ✅ Temps d'exécution : < 1 seconde

### Tests d'intégration (backend réel)
- ✅ Health check : 200 OK
- ✅ Endpoints : Réponses valides
- ✅ Temps d'exécution : < 10 secondes

### Tests E2E
- ✅ Pages chargées correctement
- ✅ Requêtes API interceptées
- ✅ Gestion des erreurs fonctionnelle

---

## ✅ Checklist de vérification

Avant de déployer, vérifier :

- [ ] Tests unitaires passent (`npm run test:backend`)
- [ ] Tests d'intégration passent avec backend (`npm run test:integration`)
- [ ] Tests E2E passent (`npm run test:e2e:backend`)
- [ ] URL API correcte en production
- [ ] CORS configuré correctement
- [ ] Authentification fonctionnelle
- [ ] Gestion des erreurs testée

---

## 📝 Notes importantes

1. **Les tests unitaires ne nécessitent pas le backend** - Ils utilisent des mocks
2. **Les tests d'intégration nécessitent le backend** - Ils font des appels réels
3. **Les tests E2E nécessitent le backend** - Ils testent dans le navigateur
4. **Tous les tests préservent le visuel** - Aucun composant de production modifié

---

**Rappel** : Ces tests vérifient la connexion backend-frontend sans casser le visuel du projet EGOEJO ! 🎨

