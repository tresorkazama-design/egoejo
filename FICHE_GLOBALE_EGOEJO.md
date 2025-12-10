# 📋 Fiche Globale - Projet EGOEJO

**Version**: 2.0 (Hybride V1.6 + V2.0) - Post-Audit Sécurisé  
**Date**: 2025-01-27  
**Statut**: Production Ready ✅ Scale Ready ✅ Async Ready ✅ Intelligence Ready ✅ Connected Ready ✅ Visual Ready ✅ Financial Ready ✅ Investment Ready (Dormant) 💤 Security Hardened 🔒  
**Dernière mise à jour majeure** : Architecture "The Sleeping Giant" (V1.6 Dons Actif + V2.0 Investissement Dormant) + Corrections Critiques Sécurité

---

## 🎯 Vue d'Ensemble

**EGOEJO** est une plateforme web full-stack moderne pour un collectif dédié au vivant. L'application permet de gérer des projets, des cagnottes, des contenus éducatifs, une messagerie en temps réel, des sondages, et de collecter des intentions de rejoindre l'organisation.

### Mission
Relier des citoyens à des projets sociaux à fort impact pour le vivant.

### Objectifs
- Faciliter la découverte et la participation à des projets
- Collecter des intentions de rejoindre le collectif
- Gérer des cagnottes et contributions
- Partager des contenus éducatifs
- Favoriser la communication via chat en temps réel
- Organiser des votes et sondages

---

## 🏗️ Architecture Technique

### Structure du Projet

```
egoejo/
├── backend/              # API Django REST Framework
│   ├── config/          # Configuration Django
│   ├── core/            # Application principale
│   │   ├── api/         # Vues API
│   │   ├── models/      # Modèles de données
│   │   ├── serializers/ # Sérialiseurs DRF
│   │   ├── security/    # Modules de sécurité
│   │   └── migrations/  # Migrations DB
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/            # Application React (sous-module Git)
│   └── frontend/        # Code source React
│       ├── src/
│       │   ├── app/     # Pages et router
│       │   ├── components/  # Composants React
│       │   ├── contexts/    # Contextes React
│       │   ├── hooks/       # Hooks personnalisés
│       │   ├── utils/       # Utilitaires
│       │   └── locales/     # Traductions i18n
│       ├── e2e/         # Tests E2E Playwright
│       └── public/      # Assets statiques
│
├── admin-panel-legacy-*.zip  # Archive legacy (admin-panel supprimé le 2025-01-27)
├── finance/             # Système financier unifié ⭐ NOUVEAU v2.0
├── investment/          # Investissement (V2.0 dormant) ⭐ NOUVEAU v2.0
├── scripts/             # Scripts utilitaires
├── docker-compose.yml   # Orchestration Docker
└── README.md
```

### Architecture de Déploiement

```
┌─────────────────┐
│   Vercel        │  → Frontend React (Production)
│   (Frontend)    │
└─────────────────┘
        │
        │ HTTPS
        │
┌─────────────────┐
│   Railway       │  → Backend Django (Production)
│   (Backend)     │
└─────────────────┘
        │
        │
┌─────────────────┐
│   PostgreSQL    │  → Base de données
│   (Railway)     │
└─────────────────┘
```

---

## 🛠️ Stack Technologique

### Backend

| Technologie | Version | Usage |
|------------|---------|-------|
| **Python** | 3.11+ | Langage principal |
| **Django** | 5.0+ | Framework web |
| **Django REST Framework** | 3.15+ | API REST |
| **PostgreSQL** | 15+ | Base de données |
| **Redis** | 6+ | Cache & WebSockets |
| **Django Channels** | 4.0+ | WebSockets temps réel |
| **Gunicorn** | 21.2+ | Serveur WSGI production |
| **Daphne** | 4.0+ | Serveur ASGI pour WebSockets |
| **Argon2** | 23.1+ | Hachage mots de passe |
| **Cryptography** | 41.0+ | Chiffrement données |
| **Django CSP** | 3.8+ | Content Security Policy |
| **WhiteNoise** | 6.6+ | Fichiers statiques |
| **django-storages** | 1.14+ | Stockage objet (R2/S3) |
| **boto3** | 1.34+ | Client AWS S3/R2 |
| **Resend** | 0.6+ | Envoi d'emails |
| **Celery** | 5.4+ | Tâches asynchrones ⭐ NOUVEAU |
| **Flower** | 2.0+ | Monitoring Celery (optionnel) ⭐ NOUVEAU |
| **OpenAI** | 1.0+ | Embeddings pour recherche sémantique ⭐ NOUVEAU v1.4.0 |
| **sentence-transformers** | 2.2+ | Embeddings locaux (alternative OpenAI) ⭐ NOUVEAU v1.4.0 |
| **pyclamd** | 0.4+ | Scan antivirus ClamAV ⭐ NOUVEAU v1.4.0 |
| **python-magic** | 0.4+ | Validation type MIME ⭐ NOUVEAU v1.4.0 |
| **umap-learn** | 0.5+ | Réduction dimensionnalité UMAP (optionnel) ⭐ NOUVEAU v1.5.0 |
| **scikit-learn** | 1.0+ | Réduction dimensionnalité t-SNE ⭐ NOUVEAU v1.5.0 |
| **DRF Spectacular** | 0.27+ | Documentation OpenAPI |

### Frontend

| Technologie | Version | Usage |
|------------|---------|-------|
| **React** | 19.2.0 | Framework UI |
| **Vite** | 7.1.11 | Build tool & dev server |
| **React Router** | 7.9.4 | Routing |
| **Three.js** | 0.180.0 | Graphiques 3D |
| **@react-three/fiber** | 9.4.0 | React renderer Three.js |
| **@react-three/drei** | 10.7.6 | Helpers Three.js |
| **GSAP** | 3.13.0 | Animations |
| **Vitest** | 2.1.9 | Tests unitaires |
| **Playwright** | 1.48.0 | Tests E2E |
| **MSW** | 2.12.3 | Mock Service Worker |
| **Sentry** | (optionnel) | Monitoring erreurs |
| **TypeScript** | (configuré) | TypeScript Strict Mode ⭐ NOUVEAU v1.4.0 |
| **ESLint** | (configuré) | Linter avec règles TypeScript ⭐ NOUVEAU v1.4.0 |

### Infrastructure & DevOps

- **Docker** & **Docker Compose** : Containerisation
- **Vercel** : Déploiement frontend
- **Railway** : Déploiement backend
- **GitHub Actions** : CI/CD (si configuré)
- **Git** : Version control (sous-module frontend)

---

## 🗄️ Modèles de Données

### Backend (Django Models)

#### 1. **Projet**
Gestion des projets du collectif
- `titre`, `description`, `categorie`
- `impact_score`, `image`
- Relations : Media, Cagnotte

#### 2. **Cagnotte**
Gestion des collectes de fonds
- `titre`, `description`
- `montant_cible`, `montant_collecte`
- Relation : Projet (optionnel)

#### 3. **Contribution**
Contributions aux cagnottes
- `cagnotte`, `user`, `montant`
- Timestamps automatiques

#### 4. **Intent**
Intentions de rejoindre le collectif
- `nom`, `email`, `profil`
- `message`, `document_url`
- `ip`, `user_agent` (tracking)
- Protection anti-spam (honeypot)

#### 5. **ChatThread** & **ChatMessage**
Messagerie en temps réel
- Threads de conversation
- Messages avec WebSockets
- Membres et permissions

#### 6. **Poll** & **PollBallot** ⭐ AMÉLIORÉ v1.4.0
Système de votes/sondages avec méthodes avancées
- Options multiples
- Votes anonymes ou authentifiés
- Ouverture/fermeture dynamique
- **Méthodes de vote** : `voting_method` (binary, quadratic, majority) ⭐ NOUVEAU
- **Vote Quadratique** : Distribution de points (`max_points`, `PollBallot.points`) ⭐ NOUVEAU
- **Jugement Majoritaire** : Classement des options (`PollBallot.ranking`) ⭐ NOUVEAU

#### 7. **EducationalContent**
Contenus éducatifs
- Titre, description, format
- Likes et commentaires
- **Catégorisation** : `category` (ressources, guides, videos, racines-philosophie, autres)
- **Tags** : `tags` (JSON) pour tags comme "Steiner", "Biodynamie"

#### 8. **HelpRequest** & **Engagement**
Demandes d'aide et engagements
- Types de besoins
- Statuts et suivi

#### 9. **PerformanceMetric** & **MonitoringAlert**
Monitoring et métriques
- Métriques de performance (LCP, FID, CLS)
- Alertes système
- Tracking utilisateurs

#### 10. **ModerationReport** & **AuditLog**
Modération et audit
- Signalements de contenu
- Logs d'actions admin

#### 11. **ImpactDashboard** ⭐ NOUVEAU
Tableau de bord d'impact utilisateur
- `total_contributions` : Total des contributions en euros
- `projects_supported` : Nombre de projets soutenus
- `cagnottes_contributed` : Nombre de cagnottes
- `intentions_submitted` : Nombre d'intentions
- Métriques agrégées pour performance

#### 12. **ProjetQuerySet**
QuerySet personnalisé avec recherche full-text
- Méthode `search(query)` : Recherche floue avec pg_trgm
- Similarité trigram pour recherche intelligente
- Fallback sur recherche simple si pg_trgm non disponible
- Compatible SQLite (dev) et PostgreSQL (production)

#### 13. **Champs Embedding** ⭐ ACTIF v1.4.0
Recherche sémantique avec embeddings (RAG léger)
- `Projet.embedding` : Vecteur d'embedding (JSONField)
- `EducationalContent.embedding` : Vecteur d'embedding (JSONField)
- Format JSON avec modèle et dimension
- **Génération automatique** : Tâches Celery pour embeddings (OpenAI ou Sentence Transformers) ⭐ NOUVEAU
- **Recherche sémantique** : Endpoints `/api/projets/semantic-search/` et `/api/projets/semantic-suggestions/` ⭐ NOUVEAU
- **Coordonnées 3D** : `coordinates_3d` (x, y, z) stockées dans embedding pour visualisation Mycélium ⭐ NOUVEAU v1.5.0
- Prêt pour migration vers VectorField (pgvector)

#### 14. **Champ Audio File** ⭐ NOUVEAU v1.5.0
Génération automatique audio (TTS) pour accessibilité terrain
- `EducationalContent.audio_file` : Fichier MP3 généré automatiquement
- **Génération automatique** : Lors de la publication d'un contenu
- **Providers supportés** : OpenAI TTS ou ElevenLabs TTS
- **Stockage** : R2/S3 ou local

#### 15. **Système Financier Unifié (Finance)** ⭐ NOUVEAU v2.0 🔒 SÉCURISÉ
Wallet universel pour V1.6 (Dons) et V2.0 (Investissement dormant)
- `UserWallet` : Portefeuille utilisateur avec solde
- `WalletTransaction` : Transactions (DEPOSIT, PLEDGE_DONATION, PLEDGE_EQUITY, REFUND, RELEASE, COMMISSION)
  - **Idempotence** : `idempotency_key` (UUID) pour éviter double dépense 🔒 NOUVEAU
- `EscrowContract` : Contrats d'escrow (cantonnement) pour sécuriser les fonds
- **Service unifié** : `pledge_funds()` gère Dons ET Investissement selon feature flag
  - **Race condition corrigée** : `select_for_update()` verrouille wallet pendant transaction 🔒 NOUVEAU
  - **Arrondis précis** : `quantize()` avec arrondi bancaire (ROUND_HALF_UP) 🔒 NOUVEAU
- **Commission automatique** : 5% EGOEJO + 3% Stripe (calculs précis)
- **Closing asynchrone** : Notifications déléguées à Celery (évite timeout) 🔒 NOUVEAU

#### 16. **Investissement (Investment - V2.0 Dormant)** ⭐ NOUVEAU v2.0
Registre des actionnaires (ne se remplit que si `ENABLE_INVESTMENT_FEATURES=True`)
- `ShareholderRegister` : Registre des actionnaires par projet
- **Champs** : `number_of_shares`, `amount_invested`, `subscription_bulletin`, `is_signed`
- **Génération automatique** : Lors d'un investissement (si V2.0 activé)

#### 17. **Modèle Projet Hybride** ⭐ MODIFIÉ v2.0
Support V1.6 (Dons) et V2.0 (Investissement dormant)
- `funding_type` : DONATION, EQUITY, HYBRID
- `donation_goal` / `investment_goal` : Objectifs financiers distincts
- `share_price`, `total_shares`, `valuation_pre_money` : Configuration V2.0 (dormant)
- `is_investment_open` : Propriété intelligente (vérifie feature flag + configuration)
- `donation_current` / `investment_current` : Montants collectés calculés automatiquement

#### 18. **Vote Pondéré Actionnaires (Poll)** ⭐ MODIFIÉ v2.0
Gouvernance adaptative selon mode V1.6 ou V2.0
- `is_shareholder_vote` : Vote réservé aux actionnaires (V2.0)
- `get_vote_weight()` : 1 personne = 1 voix (V1.6) ou 1 action = 1 voix (V2.0)
- **Protection Fondateur** : Vote pondéré x100 pour groupe "Founders_V1_Protection" 🔒 NOUVEAU

---

## 🔌 API Endpoints

### Authentification

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/auth/login/` | POST | Connexion JWT | Public |
| `/api/auth/refresh/` | POST | Rafraîchir token | Public |
| `/api/auth/register/` | POST | Inscription | Public |
| `/api/auth/me/` | GET | Profil utilisateur | JWT |

### Projets & Cagnottes

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/projets/` | GET | Liste projets (cache 5min) | Public |
| `/api/projets/` | POST | Créer projet | JWT |
| `/api/projets/search/` ⭐ NOUVEAU | GET | Recherche full-text (pg_trgm) | Public |
| `/api/cagnottes/` | GET | Liste cagnottes | Public |
| `/api/cagnottes/<id>/contribute/` | POST | Contribuer | JWT |

### Intentions

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/intents/rejoindre/` | POST | Soumettre intention | Public |
| `/api/intents/admin/` | GET | Liste intentions | Admin Token |
| `/api/intents/export/` | GET | Export CSV | Admin Token |
| `/api/intents/<id>/delete/` | DELETE | Supprimer | Admin Token |

### Chat (Temps Réel)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/chat/threads/` | GET | Liste threads | JWT |
| `/api/chat/threads/` | POST | Créer thread | JWT |
| `/api/chat/messages/` | GET | Messages thread | JWT |
| `/api/chat/messages/` | POST | Envoyer message | JWT |
| `/ws/chat/<thread_id>/` | WebSocket | Chat temps réel | JWT |

### Sondages

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/polls/` | GET | Liste sondages | Public |
| `/api/polls/` | POST | Créer sondage | JWT |
| `/api/polls/<id>/vote/` | POST | Voter (binaire, quadratique, majoritaire) ⭐ AMÉLIORÉ | JWT |
| `/api/polls/<id>/open/` | POST | Ouvrir | JWT |
| `/api/polls/<id>/close/` | POST | Fermer | JWT |
| `/ws/polls/<poll_id>/` | WebSocket | Résultats temps réel | JWT |

### Contenus Éducatifs

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/contents/` | GET | Liste contenus (cache 10min si published) | Public |
| `/api/contents/` | POST | Créer contenu | JWT |
| `/api/contents/<id>/like/` | POST | Liker | JWT |
| `/api/contents/<id>/comment/` | POST | Commenter | JWT |
| `/api/contents/?category=racines-philosophie` | GET | Contenus Racines & Philosophie | Public |

### Monitoring & Analytics

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/analytics/metrics/` | POST | Envoyer métrique | Public |
| `/api/monitoring/alerts/` | POST | Envoyer alerte | Public |
| `/api/monitoring/metrics/stats/` | GET | Statistiques | Admin |
| `/api/monitoring/alerts/list/` | GET | Liste alertes | Admin |

### Impact & Gamification ⭐ NOUVEAU

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/impact/dashboard/` | GET | Tableau de bord d'impact | JWT |

### Recherche Full-Text & Sémantique ⭐ NOUVEAU v1.4.0

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/projets/search/` | GET | Recherche full-text projets (pg_trgm) | Public |
| `/api/projets/semantic-search/` ⭐ NOUVEAU | GET | Recherche sémantique (embeddings) | Public |
| `/api/projets/semantic-suggestions/` ⭐ NOUVEAU | GET | Suggestions sémantiques liées | Public |

### Mycélium Numérique (3D) ⭐ NOUVEAU v1.5.0

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/mycelium/data/` | GET | Coordonnées 3D pour visualisation | Public |
| `/api/mycelium/reduce/` | POST | Lancer réduction dimensionnalité | Admin |

### Configuration Features (V1.6/V2.0) ⭐ NOUVEAU v2.0

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/config/features/` | GET | Configuration feature flags (investment_enabled, etc.) | Public |

### Finance & Investment ⭐ NOUVEAU v2.0

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/finance/wallet/` | GET | Solde wallet utilisateur | JWT |
| `/api/finance/wallet/deposit/` | POST | Dépôt depuis Stripe | JWT |
| `/api/finance/pledge/` | POST | Engagement (Don ou Investissement) | JWT |
| `/api/finance/escrow/` | GET | Contrats d'escrow utilisateur | JWT |
| `/api/investment/shareholders/` | GET | Registre actionnaires (si V2.0 activé) | JWT |

### Sécurité & GDPR

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/security/audit/` | GET | Audit sécurité | Admin |
| `/api/security/metrics/` | GET | Métriques sécurité | Admin |
| `/api/user/data-export/` | GET | Export données | JWT |
| `/api/user/data-delete/` | DELETE | Supprimer données | JWT |

---

## 🎨 Frontend - Pages & Composants

### Pages Principales

| Route | Composant | Description |
|-------|-----------|-------------|
| `/` | `Home` | Page d'accueil avec HeroSorgho 3D |
| `/univers` | `Univers` | Exploration du vivant |
| `/vision` | `Vision` | Vision du collectif |
| `/alliances` | `Alliances` | Partenariats |
| `/projets` | `Projets` | Liste des projets |
| `/contenus` | `Contenus` | Bibliothèque de contenus |
| `/communaute` | `Communaute` | Communauté |
| `/citations` | `Citations` | Citations inspirantes |
| `/votes` | `Votes` | Sondages et votes |
| `/chat` | `Chat` | Messagerie temps réel |
| `/rejoindre` | `Rejoindre` | Formulaire d'adhésion |
| `/admin` | `Admin` | Interface admin |
| `/login` | `Login` | Connexion |
| `/register` | `Register` | Inscription |
| `/impact` ⭐ NOUVEAU | `Impact` | Tableau de bord d'impact utilisateur |
| `/racines-philosophie` ⭐ NOUVEAU | `RacinesPhilosophie` | Section Racines & Philosophie (Steiner, Biodynamie) |
| `/mycelium` ⭐ NOUVEAU v1.5.0 | `Mycelium` | Visualisation 3D "Mycélium Numérique" |
| `/podcast` ⭐ NOUVEAU v1.5.0 | `Podcast` | Liste des contenus avec versions audio |

### Composants Clés

#### UI Components
- **Button** : Boutons avec variants (primary, ghost, etc.)
- **Input** : Champs de formulaire avec validation
- **CardTilt** : Cartes avec effet 3D tilt
- **Loader** : Indicateurs de chargement
- **Notification** : Système de notifications
- **ErrorBoundary** : Gestion d'erreurs React

#### Layout Components
- **Layout** : Layout principal avec navigation
- **Navbar** : Barre de navigation
- **FullscreenMenu** : Menu plein écran
- **LanguageSelector** : Sélecteur de langue

#### 3D & Animations
- **HeroSorgho** : Hero section avec Three.js
- **Logo3D** : Logo 3D interactif
- **MenuCube3D** : Menu cube 3D
- **CustomCursor** : Curseur personnalisé
- **CursorSpotlight** : Effet spotlight
- **PageTransition** : Transitions entre pages
- **ScrollProgress** : Barre de progression scroll

#### Features
- **ChatWindow** : Interface de chat
- **ChatList** : Liste des conversations
- **SEO** : Gestion SEO dynamique
- **OptimizedImage** : Images optimisées
- **PageViewTracker** : Tracking des vues
- **EcoModeToggle** ⭐ NOUVEAU : Toggle mode éco-responsable (bas à droite)
- **OfflineIndicator** ⭐ NOUVEAU : Indicateur statut hors-ligne (PWA)
- **QuadraticVote** ⭐ NOUVEAU v1.4.0 : Composant vote quadratique (distribution points)
- **SemanticSuggestions** ⭐ NOUVEAU v1.4.0 : Suggestions sémantiques liées
- **SemanticSearch** ⭐ NOUVEAU v1.4.0 : Recherche sémantique conceptuelle
- **MyceliumVisualization** ⭐ NOUVEAU v1.5.0 : Visualisation 3D constellation (Three.js)
- **AudioPlayer** ⭐ NOUVEAU v1.5.0 : Lecteur audio pour contenus TTS

### Contextes React

- **AuthContext** : Authentification utilisateur
- **LanguageContext** : Gestion i18n (FR, EN, ES, DE, AR, SW)
- **NotificationContext** : Notifications globales
- **EcoModeContext** ⭐ NOUVEAU : Mode éco-responsable (réduit empreinte carbone)

### Hooks Personnalisés

- **useWebSocket** : Connexion WebSocket
- **useFetch** : Requêtes HTTP
- **useDebounce** : Debounce pour recherche
- **useLocalStorage** : Persistance locale
- **useMediaQuery** : Media queries responsive
- **useClickOutside** : Détection clic extérieur
- **useSEO** : Gestion SEO dynamique
- **useNotification** : Notifications
- **useToggle** : Toggle state
- **useLowPowerMode** ⭐ NOUVEAU : Détection mode low-power (mobile, économie d'énergie)

### Utilitaires Backend

- **ProjetQuerySet.search()** ⭐ NOUVEAU : Recherche full-text avec pg_trgm
- **django-storages** ⭐ NOUVEAU : Gestion stockage objet (R2/S3)
- **useEcoMode** ⭐ NOUVEAU : Gestion mode éco-responsable
- **useEcoMode** ⭐ NOUVEAU : Gestion mode éco-responsable

---

## 🔐 Sécurité

### Backend

#### Authentification & Autorisation
- **JWT** : Tokens d'accès (60 min) + refresh (7 jours)
- **Rotation automatique** : Refresh tokens
- **Blacklist** : Tokens révoqués
- **Argon2** : Hachage mots de passe (plus sûr que PBKDF2)
- **Validation** : Mots de passe minimum 10 caractères

#### Protection des Données
- **Chiffrement** : Fernet pour données sensibles
- **Sanitization** : Nettoyage XSS, injections
- **Masquage** : Données sensibles dans logs
- **GDPR** : Export/suppression données utilisateur

#### Headers de Sécurité
- **CSP** : Content Security Policy
- **HSTS** : HTTP Strict Transport Security
- **X-Frame-Options** : DENY
- **X-Content-Type-Options** : nosniff
- **Referrer-Policy** : same-origin
- **Permissions-Policy** : Restrictions permissions

#### Rate Limiting
- **Anonymes** : 10 requêtes/minute
- **Utilisateurs** : 100 requêtes/minute
- **Configurable** : Via variables d'environnement

#### Protection Anti-Spam
- **Honeypot** : Champ "website" caché
- **Validation** : Email, longueur messages
- **Tracking** : IP, User-Agent

### Frontend

- **Validation** : Côté client et serveur
- **XSS Protection** : Échappement HTML
- **HTTPS** : Forcé en production
- **CSP** : Content Security Policy
- **Tokens sécurisés** : localStorage avec expiration

---

## 🧪 Tests

### Backend

- **Framework** : pytest + pytest-django
- **Coverage** : pytest-cov
- **Tests unitaires** : Modèles, serializers, vues
- **Tests d'intégration** : API endpoints
- **Tests de sécurité** : Bandit, Safety

### Frontend

#### Tests Unitaires (Vitest)
- **Composants** : Tests de rendu, interactions
- **Hooks** : Tests des hooks personnalisés
- **Utils** : Tests des utilitaires
- **Coverage** : 80% minimum requis

#### Tests d'Accessibilité
- **Jest-Axe** : Tests ARIA, contrastes
- **Navigation clavier** : Tab, Enter, Escape
- **Screen readers** : Compatibilité

#### Tests E2E (Playwright)
- **Navigation** : Toutes les pages
- **Formulaires** : Validation, soumission
- **Chat** : Messagerie temps réel
- **Admin** : Interface admin
- **Backend connection** : API calls

#### Tests de Performance
- **Lighthouse CI** : Métriques Core Web Vitals
- **Métriques** : LCP, FID, CLS, TTFB
- **Composants lents** : Détection automatique

---

## 📊 Monitoring & Analytics

### Sentry (Production)
- **Erreurs** : Capture automatique
- **Performance** : Métriques Core Web Vitals
- **Replay** : Sessions avec erreurs
- **Alertes** : Notifications email/Slack

### Métriques Backend
- **PerformanceMetric** : Stockage métriques
- **MonitoringAlert** : Alertes système
- **Endpoints** : `/api/analytics/metrics/`, `/api/monitoring/alerts/`

### Métriques Frontend
- **Core Web Vitals** : LCP, FID, CLS
- **Page Load** : Temps de chargement
- **API Duration** : Durée requêtes
- **Custom Metrics** : Métriques personnalisées

---

## 🌍 Internationalisation (i18n)

### Langues Supportées
- **Français** (FR) - Par défaut
- **Anglais** (EN)
- **Espagnol** (ES)
- **Allemand** (DE)
- **Arabe** (AR)
- **Swahili** (SW)

### Implémentation
- **Context** : LanguageContext
- **Fichiers** : `src/locales/*.json`
- **Hook** : `useLanguage()`
- **Fonction** : `t(key, lang)`

---

## 🚀 Déploiement

### Frontend (Vercel)

**Configuration** :
- **Root Directory** : `frontend/frontend`
- **Build Command** : `npm install && npm run build`
- **Output Directory** : `dist`
- **Node Version** : 18+

**Variables d'environnement** :
- `VITE_API_URL` : URL backend (production)
- `VITE_SENTRY_DSN` : DSN Sentry (optionnel)

**Domaine personnalisé** :
- Configuration DNS dans Vercel
- HTTPS automatique
- Certificats SSL gérés

### Backend (Railway)

**Configuration** :
- **Start Command** : `python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application`
- **Python Version** : 3.11+
- **Database** : PostgreSQL (Railway)

**Variables d'environnement** :
- `DJANGO_SECRET_KEY` : Clé secrète (50+ caractères)
- `DATABASE_URL` : URL PostgreSQL (ou PgBouncer si configuré) ⭐ MODIFIÉ
- `REDIS_URL` : URL Redis (optionnel)
- `USE_S3_STORAGE` : `true` pour activer R2/S3 ⭐ NOUVEAU
- `R2_ACCESS_KEY_ID` : Access Key Cloudflare R2 ⭐ NOUVEAU
- `R2_SECRET_ACCESS_KEY` : Secret Key Cloudflare R2 ⭐ NOUVEAU
- `R2_BUCKET_NAME` : Nom du bucket R2 ⭐ NOUVEAU
- `R2_ENDPOINT_URL` : Endpoint R2 ⭐ NOUVEAU
- `R2_CUSTOM_DOMAIN` : Domaine personnalisé (optionnel) ⭐ NOUVEAU
- `ALLOWED_HOSTS` : Domaines autorisés
- `CORS_ALLOWED_ORIGINS` : Origines CORS
- `ADMIN_TOKEN` : Token admin
- `RESEND_API_KEY` : Clé API Resend
- `NOTIFY_EMAIL` : Email notifications

---

## 📁 Structure des Fichiers Clés

### Backend

```
backend/
├── config/
│   ├── settings.py          # Configuration Django
│   ├── urls.py              # URLs principales
│   ├── asgi.py              # ASGI pour WebSockets
│   └── wsgi.py              # WSGI pour production
│
├── core/
│   ├── models/              # Modèles de données
│   │   ├── projects.py
│   │   ├── fundraising.py
│   │   ├── intents.py
│   │   ├── chat.py
│   │   ├── polls.py
│   │   ├── monitoring.py
│   │   ├── impact.py ⭐ NOUVEAU
│   │   ├── projects.py ⭐ MODIFIÉ (QuerySet recherche full-text)
│   │   └── ...
│   │
│   ├── api/                 # Vues API
│   │   ├── projects.py
│   │   ├── monitoring_views.py
│   │   ├── gdpr_views.py
│   │   ├── impact_views.py ⭐ NOUVEAU
│   │   ├── search_views.py ⭐ NOUVEAU (Recherche full-text)
│   │   ├── semantic_search_views.py ⭐ NOUVEAU v1.4.0 (Recherche sémantique)
│   │   ├── polls.py ⭐ MODIFIÉ v1.4.0 (Vote quadratique/majoritaire)
│   │   ├── projects.py ⭐ MODIFIÉ v1.4.0 (Scan antivirus intégré)
│   │   ├── content_views.py ⭐ MODIFIÉ v1.4.0 (Scan antivirus intégré, génération audio auto)
│   │   └── ...
│   │
│   ├── serializers/         # Sérialiseurs DRF
│   ├── security/            # Modules sécurité
│   │   ├── encryption.py
│   │   ├── sanitization.py
│   │   ├── middleware.py
│   │   └── logging.py
│   │
│   ├── tasks/              # Tâches Celery ⭐ NOUVEAU v1.4.0
│   │   ├── tasks.py        # Tâches générales (emails, impact, notifications projet) 🔒 MODIFIÉ v2.0
│   │   ├── tasks_embeddings.py ⭐ NOUVEAU : Génération embeddings
│   │   ├── tasks_security.py ⭐ NOUVEAU : Scan antivirus, validation fichiers
│   │   ├── tasks_mycelium.py ⭐ NOUVEAU v1.5.0 : Réduction dimensionnalité (UMAP/t-SNE)
│   │   └── tasks_audio.py ⭐ NOUVEAU v1.5.0 : Génération audio TTS
│   │
│   ├── scripts/            # Scripts utilitaires ⭐ NOUVEAU v1.5.0
│   │   ├── launch_mycelium_reduction.py ⭐ NOUVEAU : Script réduction dimensionnalité
│   │   └── test_audio_generation.py ⭐ NOUVEAU : Script test TTS
│   │
│   └── consumers.py         # WebSocket consumers
│
├── finance/                # Système financier unifié ⭐ NOUVEAU v2.0 🔒 SÉCURISÉ
│   ├── models.py           # UserWallet, WalletTransaction (idempotency_key), EscrowContract
│   ├── services.py         # Services financiers sécurisés (race condition, arrondis, idempotence)
│   ├── admin.py            # Admin Django
│   └── apps.py
│
├── investment/             # Investissement (V2.0 dormant) ⭐ NOUVEAU v2.0
│   ├── models.py           # ShareholderRegister
│   ├── admin.py            # Admin Django
│   └── apps.py
│
└── requirements.txt
```

### Frontend

```
frontend/frontend/
├── src/
│   ├── app/
│   │   ├── pages/           # Pages de l'application
│   │   │   ├── Mycelium.jsx ⭐ NOUVEAU v1.5.0
│   │   │   └── Podcast.jsx ⭐ NOUVEAU v1.5.0
│   │   └── router.jsx       # Configuration routing
│   │
│   ├── components/          # Composants React
│   │   ├── QuadraticVote.jsx ⭐ NOUVEAU v1.4.0
│   │   ├── SemanticSuggestions.jsx ⭐ NOUVEAU v1.4.0
│   │   ├── SemanticSearch.jsx ⭐ NOUVEAU v1.4.0
│   │   ├── MyceliumVisualization.jsx ⭐ NOUVEAU v1.5.0
│   │   └── AudioPlayer.jsx ⭐ NOUVEAU v1.5.0
│   ├── contexts/            # Contextes React
│   │   └── EcoModeContext.jsx ⭐ NOUVEAU
│   ├── hooks/               # Hooks personnalisés
│   │   └── useLowPowerMode.js ⭐ NOUVEAU
│   ├── utils/               # Utilitaires
│   │   ├── api.js           # Client API
│   │   ├── monitoring.js    # Monitoring
│   │   ├── sentry.js        # Sentry
│   │   └── ...
│   │
│   ├── locales/             # Traductions i18n
│   └── styles/              # Styles CSS
│       └── eco-mode.css ⭐ NOUVEAU
│
├── e2e/                     # Tests E2E Playwright
├── public/                   # Assets statiques
├── vite.config.js            # Configuration Vite
├── vitest.config.js          # Configuration Vitest
├── playwright.config.js      # Configuration Playwright
├── tsconfig.json ⭐ NOUVEAU v1.4.0 : Configuration TypeScript Strict
├── tsconfig.node.json ⭐ NOUVEAU v1.4.0 : Config TypeScript Node
└── .eslintrc.cjs ⭐ NOUVEAU v1.4.0 : ESLint (interdit nouveaux .jsx)
```

---

## 🔧 Configuration & Variables d'Environnement

### Backend (.env)

```env
# Django
DJANGO_SECRET_KEY=...
DEBUG=0
ALLOWED_HOSTS=egoejo.org,www.egoejo.org

# Database
DATABASE_URL=postgresql://...
# Note: En production avec PgBouncer, DATABASE_URL pointe vers PgBouncer

# Redis (optionnel)
REDIS_URL=redis://...

# Storage (R2/S3) ⭐ NOUVEAU
USE_S3_STORAGE=true
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=egoejo-media
R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
R2_CUSTOM_DOMAIN=media.egoejo.org  # Optionnel

# Security
ADMIN_TOKEN=...
ENCRYPTION_KEY=...

# Email
RESEND_API_KEY=...
NOTIFY_EMAIL=...

# Intelligence Sémantique (Embeddings) ⭐ NOUVEAU v1.4.0
OPENAI_API_KEY=...  # Optionnel (pour embeddings OpenAI)
# Si non configuré, utilise Sentence Transformers (local, gratuit)

# Sécurité (Scan Anti-Virus) ⭐ NOUVEAU v1.4.0
CLAMAV_HOST=localhost  # Optionnel
CLAMAV_PORT=3310       # Optionnel
# Si non configuré, fichiers considérés comme sûrs (pas de blocage)

# Text-to-Speech (TTS) - Audio-First ⭐ NOUVEAU v1.5.0
TTS_PROVIDER=openai    # 'openai' ou 'elevenlabs'
TTS_VOICE=alloy        # Voix OpenAI : 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'
# OU pour ElevenLabs :
# ELEVENLABS_API_KEY=...
# TTS_PROVIDER=elevenlabs
# TTS_VOICE=default

# Feature Flags - Architecture "The Sleeping Giant" ⭐ NOUVEAU v2.0
ENABLE_INVESTMENT_FEATURES=False  # False = V1.6 (Dons), True = V2.0 (Investissement)
EGOEJO_COMMISSION_RATE=0.05       # 5% commission EGOEJO
STRIPE_FEE_ESTIMATE=0.03          # 3% frais Stripe estimés
FOUNDER_GROUP_NAME=Founders       # Groupe pour protection fondateur (vote x100)

# Celery (Déjà requis pour Channels)
REDIS_URL=redis://...  # Déjà requis

# CORS
CORS_ALLOWED_ORIGINS=https://egoejo.org
CSRF_TRUSTED_ORIGINS=https://egoejo.org
```

### Frontend (.env)

```env
# API
VITE_API_URL=https://egoejo-production.up.railway.app

# Monitoring (optionnel)
VITE_SENTRY_DSN=https://...
```

---

## 📚 Documentation Disponible

### Guides Principaux
- `README.md` : Documentation principale
- `GUIDE_ACHAT_NOM_DOMAINE.md` : Acheter un domaine
- `CONFIGURATION_SENTRY_VERCEL.md` : Configurer Sentry
- `GUIDE_GIT_SOUS_MODULE.md` : Gestion Git sous-module
- `backend/ENDPOINTS_MONITORING.md` : Endpoints monitoring
- `frontend/frontend/TESTS_E2E_ET_MONITORING.md` : Tests E2E
- `SUGGESTIONS_AMELIORATIONS_OPTIMISATIONS.md` : Suggestions d'amélioration
- `IMPLEMENTATION_AMELIORATIONS_COMPLETE.md` : Guide d'implémentation
- `RESUME_IMPLEMENTATION_AMELIORATIONS.md` : Résumé des améliorations
- `ANALYSE_SCALABILITE_AMELIORATIONS.md` : Analyse scalabilité complète
- `GUIDE_CONFIGURATION_R2_PGBOUNCER.md` : Guide configuration R2 & PgBouncer
- `RESUME_AMELIORATIONS_SCALABILITE.md` : Résumé améliorations scalabilité
- `ANALYSE_ARCHITECTURE_V1.2.0.md` ⭐ NOUVEAU : Analyse architecture complète + plan d'action
- `GUIDE_IMPLEMENTATION_CELERY.md` ⭐ NOUVEAU : Guide installation et utilisation Celery
- `GUIDE_RECHERCHE_SEMANTIQUE.md` ⭐ NOUVEAU : Roadmap recherche vectorielle (pgvector)
- `GUIDE_LAZY_LOADING_THREEJS.md` ⭐ NOUVEAU : Guide lazy loading Three.js
- `GUIDE_ROADMAP_V1.4.0.md` ⭐ NOUVEAU v1.4.0 : Guide implémentation roadmap v1.4.0
- `GUIDE_VARIABLES_ENVIRONNEMENT_V1.4.0.md` ⭐ NOUVEAU v1.4.0 : Configuration variables v1.4.0
- `ANALYSE_VIGILANCE_V1.3.0.md` ⭐ NOUVEAU v1.4.0 : Analyse points de vigilance
- `RESUME_IMPLEMENTATION_V1.4.0.md` ⭐ NOUVEAU v1.4.0 : Résumé implémentation v1.4.0
- `ROADMAP_V1.5.0_CONNECTE_VISUEL.md` ⭐ NOUVEAU v1.5.0 : Roadmap v1.5.0 Connecté & Visuel
- `GUIDE_VARIABLES_ENVIRONNEMENT_V1.5.0.md` ⭐ NOUVEAU v1.5.0 : Configuration variables TTS
- `GUIDE_LANCEMENT_MYCELIUM.md` ⭐ NOUVEAU v1.5.0 : Guide réduction dimensionnalité
- `GUIDE_TEST_AUDIO.md` ⭐ NOUVEAU v1.5.0 : Guide test génération audio
- `RESUME_CONFIGURATION_V1.5.0.md` ⭐ NOUVEAU v1.5.0 : Résumé configuration v1.5.0
- `NOTES_INSTALLATION_UMAP.md` ⭐ NOUVEAU v1.5.0 : Notes installation UMAP (Python 3.14)

### Guides Techniques
- `LANCEMENT.md` : Lancer le projet localement
- `QUICK_START.md` : Démarrage rapide
- `GUIDE_DEPLOIEMENT.md` : Guide de déploiement
- `GUIDE_PRODUCTION.md` : Configuration production

---

## 🎯 Fonctionnalités Principales

### ✅ Implémentées

1. **Gestion de Projets**
   - Liste, création, édition
   - Catégorisation
   - Images et médias

2. **Cagnottes & Contributions**
   - Création de cagnottes
   - Suivi des contributions
   - Objectifs et progression

3. **Formulaire Rejoindre**
   - Validation complète
   - Protection anti-spam
   - Export CSV admin

4. **Chat Temps Réel**
   - WebSockets Django Channels
   - Threads de conversation
   - Messages en temps réel

5. **Sondages & Votes**
   - Création de sondages
   - Votes multiples
   - Résultats temps réel

6. **Contenus Éducatifs**
   - Bibliothèque de contenus
   - Likes et commentaires
   - Catégorisation

7. **Interface Admin**
   - Gestion des intentions
   - Filtres et recherche
   - Export CSV

8. **Monitoring**
   - Métriques de performance
   - Alertes automatiques
   - Intégration Sentry

9. **Sécurité Renforcée**
   - Chiffrement données
   - Sanitization
   - Headers sécurité
   - GDPR compliance

10. **Tests Complets**
    - Tests unitaires (80%+ coverage)
    - Tests E2E Playwright
    - Tests accessibilité
    - Tests performance

11. **Gamification Impact** ⭐ NOUVEAU
    - Tableau de bord d'impact utilisateur
    - Métriques de contribution
    - Message d'impact personnalisé
    - Endpoint `/api/impact/dashboard/`

12. **Racines & Philosophie** ⭐ NOUVEAU
    - Section dédiée aux fondements historiques
    - Catégorie "racines-philosophie" pour contenus
    - Tags pour références (Steiner, Biodynamie, etc.)
    - Page `/racines-philosophie`

13. **Optimisations Performance** ⭐ NOUVEAU
    - Low Power Mode (détection automatique mobile)
    - Cache Redis sur endpoints publics
    - PWA offline amélioré (cache contenus et chat)
    - Eco-Mode pour réduire empreinte carbone

14. **Scalabilité Infrastructure** ⭐ NOUVEAU
    - Stockage objet R2/S3 pour médias (persistance sur Cloudflare R2 ou AWS S3)
    - Recherche full-text avec pg_trgm (PostgreSQL)
    - Connection pooling PgBouncer (documenté)
    - Migration pg_trgm compatible SQLite (dev) et PostgreSQL (prod)

15. **Intelligence Sémantique (RAG Léger)** ⭐ NOUVEAU v1.4.0
    - Génération embeddings automatique (OpenAI ou Sentence Transformers)
    - Recherche sémantique conceptuelle (pas juste mots-clés)
    - Suggestions automatiques basées sur similarité
    - Endpoints `/api/projets/semantic-search/` et `/api/projets/semantic-suggestions/`
    - Tâches Celery asynchrones pour génération embeddings

16. **Gouvernance Décentralisée** ⭐ NOUVEAU v1.4.0
    - Vote Quadratique : Distribution de points entre options
    - Jugement Majoritaire : Classement des options par préférence
    - Support méthodes avancées dans modèle Poll
    - Composant UI `QuadraticVote` pour interface vote avancé

17. **Sécurité & Qualité Code Renforcées** ⭐ NOUVEAU v1.4.0
    - Scan antivirus ClamAV sur uploads (tâches Celery asynchrones)
    - Validation type MIME des fichiers uploadés
    - TypeScript Strict Mode configuré
    - ESLint interdit nouveaux fichiers `.jsx` (force `.tsx`)
    - Migration progressive vers TypeScript documentée

18. **Mycélium Numérique (Visualisation 3D)** ⭐ NOUVEAU v1.5.0
    - Réduction dimensionnalité (UMAP/t-SNE) pour transformer embeddings en coordonnées 3D
    - Visualisation Three.js interactive des projets et contenus
    - Page `/mycelium` pour exploration visuelle
    - Endpoints `/api/mycelium/data/` et `/api/mycelium/reduce/`
    - Script `launch_mycelium_reduction.py` pour lancer la réduction

19. **Accessibilité Audio-First (TTS)** ⭐ NOUVEAU v1.5.0
    - Génération automatique audio (MP3) lors de la publication
    - Support OpenAI TTS et ElevenLabs TTS
    - Composant `AudioPlayer` pour lecture
    - Page `/podcast` pour liste des contenus audio
    - Script `test_audio_generation.py` pour tester
    - Idéal pour utilisation terrain (mains dans la terre)

20. **Fédération ActivityPub** ⭐ DOCUMENTÉ v1.5.0
    - Roadmap complète pour intégration Fediverse
    - Documentation détaillée dans `ROADMAP_V1.5.0_CONNECTE_VISUEL.md`
    - Prêt pour implémentation Phase 3

21. **Architecture "The Sleeping Giant" (V1.6 + V2.0)** ⭐ NOUVEAU v2.0
    - **Feature Flags** : `ENABLE_INVESTMENT_FEATURES` (Kill Switch V1.6/V2.0)
    - **Système Financier Unifié** : Wallet universel, Escrow, Transactions
    - **Investissement Dormant** : Registre actionnaires (V2.0 activable)
    - **Modèle Projet Hybride** : Support Dons ET Investissement selon feature flag
    - **Vote Pondéré** : 1 voix V1.6, 1 action = 1 voix V2.0 (x100 fondateurs)
    - **Service Unifié** : `pledge_funds()` gère Dons ET Investissement
    - **Commission Automatique** : 5% EGOEJO + 3% Stripe
    - **Activation Instantanée** : Changer variable d'env = transformation sans réécriture

### 🚧 En Développement / Amélioration

- **Fédération ActivityPub** 📋 Documenté (Phase 3 de v1.5.0)
  - Intégration Fediverse (Mastodon, Lemmy, PeerTube)
  - Endpoints ActivityPub (Actor, Outbox, Inbox)
  - WebFinger discovery
  - Signature HTTP
  
- **Améliorations Mycélium** 📋 En cours
  - Connexions interactives entre nœuds
  - Filtres par catégorie/tags
  - Animation transitions
  
- **Améliorations Audio** 📋 En cours
  - Extraction texte depuis PDF pour TTS
  - Support plusieurs langues
  - Playlist automatique
  
- Migration progressive vers TypeScript 📋 En cours (ESLint configuré, nouveaux fichiers en .tsx)
- Automated Moderation (AI Lite) pour chat 📋 Documenté
- Notifications push
- Analytics avancés
- Optimisations SEO supplémentaires
- Migration pgvector (VectorField) 📋 Préparé (migration conditionnelle créée)

---

## 📈 Métriques & Performance

### Core Web Vitals (Objectifs)

- **LCP** (Largest Contentful Paint) : < 2.5s
- **FID** (First Input Delay) : < 100ms
- **CLS** (Cumulative Layout Shift) : < 0.1
- **TTFB** (Time to First Byte) : < 600ms

### Optimisations

- **Code Splitting** : Chunks séparés (vendor, react, gsap, three)
- **Lazy Loading** : Routes et composants
- **Image Optimization** : Images optimisées
- **PWA** : Service Worker, cache amélioré (contenus 24h, chat 5min)
- **Compression** : Gzip, Brotli
- **Low Power Mode** ⭐ NOUVEAU : Détection automatique mobile/économies d'énergie, désactivation Three.js
- **Cache Redis** ⭐ NOUVEAU : Cache sur `/api/projets/` (5min) et `/api/contents/` (10min)
- **Eco-Mode** ⭐ NOUVEAU : Réduction empreinte carbone (animations désactivées, images optimisées)
- **Stockage Objet (R2/S3)** ⭐ NOUVEAU : Persistance médias sur Cloudflare R2 ou AWS S3
- **Recherche Full-Text** ⭐ NOUVEAU : Recherche intelligente avec pg_trgm (PostgreSQL)
- **Connection Pooling** ⭐ NOUVEAU : PgBouncer pour scalabilité DB (documenté)
- **Stockage Objet (R2/S3)** ⭐ NOUVEAU : Persistance des médias sur Cloudflare R2 ou AWS S3
- **Recherche Full-Text** ⭐ NOUVEAU : Recherche intelligente avec pg_trgm (PostgreSQL)
- **Connection Pooling** ⭐ NOUVEAU : PgBouncer documenté pour scalabilité des connexions DB
- **Recherche Sémantique** ⭐ NOUVEAU v1.4.0 : Recherche conceptuelle avec embeddings (OpenAI/Sentence Transformers)
- **Scan Anti-Virus** ⭐ NOUVEAU v1.4.0 : Scan ClamAV asynchrone sur uploads (tâches Celery)
- **TypeScript Strict** ⭐ NOUVEAU v1.4.0 : Configuration TypeScript Strict Mode pour nouveaux fichiers
- **Visualisation 3D Mycélium** ⭐ NOUVEAU v1.5.0 : Réduction dimensionnalité (UMAP/t-SNE) + Three.js
- **Génération Audio TTS** ⭐ NOUVEAU v1.5.0 : Génération automatique MP3 (OpenAI/ElevenLabs) pour accessibilité terrain

---

## 🔄 Workflow de Développement

### Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend/frontend
npm install
npm run dev
```

### Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend/frontend
npm run test          # Tests unitaires
npm run test:e2e      # Tests E2E
npm run test:a11y     # Tests accessibilité
```

### Déploiement

```bash
# Backend (Railway)
git push origin main  # Déploiement automatique

# Frontend (Vercel)
git push origin main  # Déploiement automatique
```

---

## 🎨 Design & UX

### Thème
- **Couleurs** : Vert (#00ffa3), Fond sombre (#050607)
- **Typographie** : Moderne, lisible
- **Animations** : GSAP, transitions fluides
- **3D** : Three.js pour éléments interactifs

### Responsive
- **Mobile First** : Design adaptatif
- **Breakpoints** : Mobile, tablette, desktop
- **Touch** : Gestes tactiles supportés

### Accessibilité
- **ARIA** : Attributs ARIA complets
- **Navigation clavier** : Tab, Enter, Escape
- **Contrastes** : WCAG AA minimum
- **Screen readers** : Compatible

---

## 🔗 Liens & Accès

### Production
- **Frontend** : https://egoejo.org (ou URL Vercel)
- **Backend** : https://egoejo-production.up.railway.app
- **API Docs** : https://egoejo-production.up.railway.app/api/schema/swagger-ui/

### Développement
- **Frontend Local** : http://localhost:5173
- **Backend Local** : http://localhost:8000
- **API Local** : http://localhost:8000/api/

---

## 📝 Notes Importantes

### Git
- **Frontend** : Sous-module Git séparé
- **Backend** : Repo principal
- **Branches** : `main` (production), `frontend_ui_refonte` (frontend)

### Secrets
- **Ne jamais committer** : `.env`, secrets
- **GitHub Secrets** : Configuration CI/CD
- **Vercel/Railway** : Variables d'environnement

### Maintenance
- **Mises à jour** : Dépendances régulières
- **Sécurité** : Audits npm/pip
- **Monitoring** : Vérification Sentry
- **Backups** : Base de données réguliers
- **Stockage Médias** : R2/S3 configuré (pas de perte de données) ⭐ NOUVEAU
- **Connection Pooling** : PgBouncer recommandé pour production ⭐ NOUVEAU

---

## 🎓 Ressources & Support

### Documentation Externe
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)

### Outils
- **Sentry** : Monitoring erreurs
- **Vercel Analytics** : Analytics frontend
- **Railway** : Déploiement backend
- **GitHub** : Version control

---

## ✅ Checklist Production

- [x] Tests passent (100%)
- [x] Sécurité renforcée
- [x] Monitoring configuré
- [x] Documentation complète
- [x] Déploiement automatique
- [x] HTTPS activé
- [x] Variables d'environnement configurées
- [x] Base de données migrée
- [x] Fichiers statiques servis
- [x] CORS configuré
- [x] Rate limiting activé
- [x] Logs configurés
- [x] Backups planifiés
- [x] Stockage objet R2/S3 configuré ⭐ NOUVEAU
- [x] Recherche full-text implémentée ⭐ NOUVEAU
- [x] Connection pooling documenté ⭐ NOUVEAU
- [x] Intelligence sémantique implémentée ⭐ NOUVEAU v1.4.0
- [x] Vote quadratique implémenté ⭐ NOUVEAU v1.4.0
- [x] Scan antivirus intégré ⭐ NOUVEAU v1.4.0
- [x] TypeScript Strict configuré ⭐ NOUVEAU v1.4.0
- [x] Mycélium Numérique implémenté ⭐ NOUVEAU v1.5.0
- [x] TTS Audio-First implémenté ⭐ NOUVEAU v1.5.0
- [x] ActivityPub documenté ⭐ NOUVEAU v1.5.0
- [x] Architecture "The Sleeping Giant" implémentée ⭐ NOUVEAU v2.0
- [x] Système financier unifié (Wallet, Escrow) ⭐ NOUVEAU v2.0
- [x] Investissement dormant (V2.0 activable) ⭐ NOUVEAU v2.0
- [x] Feature flags (ENABLE_INVESTMENT_FEATURES) ⭐ NOUVEAU v2.0

---

**Dernière mise à jour** : 2025-01-27  
**Version** : 2.0 (Hybride V1.6 + V2.0)  
**Statut** : ✅ Production Ready ✅ Scale Ready ✅ Async Ready ✅ Intelligence Ready ✅ Connected Ready ✅ Visual Ready ✅ Financial Ready ✅ Investment Ready (Dormant) 💤

---

## 🆕 Améliorations Récentes (2025-01-27)

### Phase 1 : Critiques ✅
- ✅ **Nettoyage admin-panel/** : Dossier legacy archivé et supprimé
- ✅ **React 19 Compatibilité** : Vérifiée et confirmée

### Phase 2 : Performance ✅
- ✅ **Low Power Mode** : Détection automatique mobile/économies d'énergie, désactivation Three.js
- ✅ **Cache Redis Avancé** : Cache sur `/api/projets/` (5min) et `/api/contents/` (10min)

### Phase 3 : UX ✅
- ✅ **Eco-Mode** : Toggle éco-responsable, réduction empreinte carbone
- ✅ **PWA Offline** : Cache amélioré pour contenus (24h) et chat (5min), indicateur hors-ligne

### Phase 4 : Enrichissement ✅
- ✅ **Gamification Impact** : Modèle `ImpactDashboard`, endpoint `/api/impact/dashboard/`, page `/impact`
- ✅ **Racines & Philosophie** : Catégorie et tags dans `EducationalContent`, page `/racines-philosophie`

### Phase 5 : Scalabilité ✅ ⭐ NOUVEAU
- ✅ **Stockage Objet (R2/S3)** : Configuration django-storages pour Cloudflare R2 ou AWS S3
- ✅ **Recherche Full-Text** : Endpoint `/api/projets/search/` avec pg_trgm (PostgreSQL)
- ✅ **Connection Pooling** : Documentation PgBouncer pour scalabilité DB
- ✅ **Migration pg_trgm** : Compatible SQLite (dev) et PostgreSQL (prod)

**Migrations appliquées** : 
- ✅ `0009_educationalcontent_category_educationalcontent_tags_and_more`
- ✅ `0010_enable_pg_trgm` (compatible SQLite/PostgreSQL)
- ✅ `0011_add_embedding_fields` (champs embedding Projet et EducationalContent)
- ✅ `0012_add_voting_method_to_poll` (vote quadratique/majoritaire)
- ✅ `0013_migrate_to_pgvector` (préparation pgvector, conditionnelle)

### Phase 6 : Intelligence Sémantique ✅ ⭐ NOUVEAU v1.4.0
- ✅ **Recherche Sémantique (RAG Léger)** : Endpoints `/api/projets/semantic-search/` et `/api/projets/semantic-suggestions/`
- ✅ **Génération Embeddings** : Tâches Celery pour OpenAI ou Sentence Transformers
- ✅ **Composants UI** : `SemanticSearch` et `SemanticSuggestions` créés
- ✅ **Champs Embedding** : Prêts pour migration pgvector future

### Phase 7 : Gouvernance Décentralisée ✅ ⭐ NOUVEAU v1.4.0
- ✅ **Vote Quadratique** : Distribution de points entre options
- ✅ **Jugement Majoritaire** : Classement des options
- ✅ **Modèle Poll Étendu** : Champs `voting_method`, `max_points`, `points`, `ranking`
- ✅ **API Adaptée** : Support méthodes avancées dans endpoint `/api/polls/<id>/vote/`
- ✅ **Composant UI** : `QuadraticVote` créé

### Phase 8 : Sécurité & Qualité Code ✅ ⭐ NOUVEAU v1.4.0
- ✅ **Scan Anti-Virus** : Tâches Celery ClamAV sur uploads (Projet, EducationalContent)
- ✅ **Validation Type MIME** : Validation fichiers uploadés
- ✅ **TypeScript Strict Mode** : Configuration complète (`tsconfig.json`, `tsconfig.node.json`)
- ✅ **ESLint Strict** : Interdit nouveaux fichiers `.jsx`, force `.tsx`
- ✅ **Migration Progressive** : Documentation et configuration pour migration TypeScript

### Phase 9 : Connecté & Visuel ✅ ⭐ NOUVEAU v1.5.0
- ✅ **Mycélium Numérique (3D)** : Réduction dimensionnalité (UMAP/t-SNE), visualisation Three.js, page `/mycelium`
- ✅ **TTS Audio-First** : Génération automatique audio (OpenAI/ElevenLabs), composant `AudioPlayer`, page `/podcast`
- ✅ **Scripts Utilitaires** : `launch_mycelium_reduction.py`, `test_audio_generation.py`
- ✅ **Documentation Complète** : Guides configuration, lancement, tests
- ✅ **ActivityPub Documenté** : Roadmap complète pour Phase 3 (Fédération Fediverse)

**Migrations appliquées** : 
- ✅ `0015_add_audio_file_and_coordinates_3d` (audio_file, coordinates_3d dans embedding)

### Phase 10 : Architecture "The Sleeping Giant" ✅ ⭐ NOUVEAU v2.0
- ✅ **Feature Flags** : Système `ENABLE_INVESTMENT_FEATURES` (Kill Switch V1.6/V2.0)
- ✅ **Application Finance** : Wallet universel, Escrow, Transactions (V1.6 + V2.0)
- ✅ **Application Investment** : Registre actionnaires (V2.0 dormant)
- ✅ **Modèle Projet Hybride** : Support `funding_type` (DONATION, EQUITY, HYBRID)
- ✅ **Services Financiers Unifiés** : `pledge_funds()`, `release_escrow()`
- ✅ **Vote Pondéré Actionnaires** : `Poll.get_vote_weight()` adaptatif V1.6/V2.0
- ✅ **API Config Features** : Endpoint `/api/config/features/` pour frontend
- ✅ **Documentation Complète** : `ARCHITECTURE_SLEEPING_GIANT_V1.6_V2.0.md`

**Migrations à créer** :
- ⏳ `0016_add_finance_models` (UserWallet, WalletTransaction, EscrowContract)
- ⏳ `0017_add_investment_models` (ShareholderRegister)
- ⏳ `0018_add_project_funding_fields` (funding_type, donation_goal, investment_goal, etc.)
- ⏳ `0019_add_poll_shareholder_vote` (is_shareholder_vote)
- ⏳ `0020_add_idempotency_key` (idempotency_key UUIDField dans WalletTransaction) 🔒 NOUVEAU

### Phase 11 : Corrections Critiques Sécurité ✅ ⭐ NOUVEAU v2.0 🔒
- ✅ **Race Condition Wallet** : `select_for_update()` pour verrouiller wallet pendant transaction
- ✅ **Arrondis Mathématiques** : `quantize()` avec arrondi bancaire (ROUND_HALF_UP) sur tous calculs
- ✅ **Magic Strings Groupes** : `FOUNDER_GROUP_NAME` centralisé dans settings (évite perte protection)
- ✅ **Closing Asynchrone** : Notifications déléguées à Celery (`notify_project_success_task`)
- ✅ **Idempotence** : `idempotency_key` (UUIDField unique) dans `WalletTransaction`
- ✅ **Documentation** : `AUDIT_CORRECTIONS_CRITIQUES_V2.0.md` créée

**Impact** :
- ✅ Pas de double dépense (race condition corrigée)
- ✅ Calculs précis (pas d'erreur d'un centime)
- ✅ Pas de timeout (notifications asynchrones)
- ✅ Pas de double paiement (idempotence)

