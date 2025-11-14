# Changelog - EGOEJO

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.2.0] - 2025-02-XX

### Ajouté

- Découpage des bundles frontend (chunks séparés pour React, GSAP, Three) via `manualChunks`
- Chargement paresseux des vues (Layout, Home, Univers, etc.) dans `router.jsx`
- Fichier `backend/env.template` pour configurer rapidement les variables d’environnement
- `Makefile` avec cibles `backend-test`, `frontend-test`, `frontend-build`, `predeploy`

### Modifié

- `README.md` : documentation enrichie (fallback SQLite, throttle tests, scripts Makefile)
- `App.jsx`/`router.jsx` : simplification du chargement du routeur
- `settings.py` : désactivation conditionnelle du rate limiting via `DISABLE_THROTTLE_FOR_TESTS`

### Notes

- Les tests backend peuvent désormais être lancés sans PostgreSQL (fallback SQLite)
- Pour les tests locaux, définir `DEBUG=1` et `DISABLE_THROTTLE_FOR_TESTS=1` supprime les redirections HTTPS et le throttling.

## [1.1.0] - 2025-01-27

### Ajouté

- **Nettoyage des fichiers de backup** : Suppression de tous les fichiers de backup dans le frontend
- **Admin Panel finalisé** : 
  - Correction des endpoints pour utiliser l'API Django
  - Support des filtres (date, profil, recherche)
  - Pagination fonctionnelle
  - Export CSV avec filtres
  - Suppression d'intentions
- **Formulaire Rejoindre implémenté** :
  - Formulaire complet avec validation
  - Protection anti-spam (honeypot)
  - Gestion des erreurs
  - Messages de succès
- **Tests backend** :
  - Tests unitaires pour le modèle Intent
  - Tests pour les endpoints API
  - Tests de validation
  - Tests d'authentification admin
  - Tests de filtres et recherche
- **Tests frontend** :
  - Tests pour le formulaire Rejoindre
  - Configuration Vitest
  - Setup des tests avec Testing Library
- **CI/CD** :
  - Workflow GitHub Actions
  - Tests automatiques backend et frontend
  - Lint automatique
  - Couverture de code
  - Build automatique

### Modifié

- **Backend** :
  - Amélioration de l'endpoint `admin_data` avec support des filtres
  - Amélioration de l'endpoint `export_intents` avec support des filtres
  - Ajout de l'endpoint `delete_intent` pour la suppression
  - Amélioration de la gestion des erreurs
- **Frontend** :
  - Mise à jour de `api.js` avec les bons endpoints
  - Correction de `Admin.jsx` pour utiliser les nouveaux endpoints
  - Implémentation complète de `Rejoindre.jsx`
  - Correction des problèmes d'encodage (caractères spéciaux)

### Technique

- Ajout de `pytest`, `pytest-django`, `pytest-cov` pour les tests backend
- Ajout de `vitest`, `@testing-library/react`, `@testing-library/jest-dom` pour les tests frontend
- Configuration de GitHub Actions pour CI/CD
- Documentation des tests dans `TESTS.md`

## [1.0.0] - 2025-01-XX

### Version initiale

- Backend Django avec REST API
- Frontend React avec Vite
- Admin Panel React
- Docker Compose pour le développement
- Modèles de données (Projet, Cagnotte, Contribution, Intent, Media)
- Endpoints API de base
- Authentification JWT
- Sécurité (Argon2, rate limiting, CORS)

