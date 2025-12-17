# 🏗️ Architecture EGOEJO V2 - Scalable & Maintainable

**Date** : 2025-12-16  
**Version** : 2.0.0  
**Statut** : Architecture cible pour la phase "Scale" - Cycles SAKA & Tests de concurrence implémentés

---

## 1. Objectif du document

Ce document sert de **boussole technique** pour la phase "Scale" d'EGOEJO. Il décrit comment l'architecture passe de "Production Ready" à "Scalable & Maintainable", en alignant le design technique avec le système SAKA, les cycles (compost, Silo), la logique 4P (double métrique euros / engagement), et les besoins de monitoring et de résilience.

**Approche progressive** : Ce document décrit l'état cible et les améliorations en cours, pas un big bang. On reste sur un **monolithe Django bien structuré** (pas de microservices pour l'instant), mais avec une organisation du code claire, des services réutilisables, et une infrastructure prête à évoluer.

---

## 2. Vue d'ensemble de l'architecture

### Vue logique

#### Frontend
- **Stack** : Vite + React 19, PWA (Service Workers), Tailwind CSS, Three.js
- **Tests** : Vitest (unitaires), Playwright (E2E)
- **Déploiement** : Vercel (CDN global, edge functions)
- **Build** : Vite production build optimisé (code splitting, tree shaking)

#### Backend
- **Framework** : Django 5 + Django REST Framework (DRF)
- **Tâches asynchrones** : Celery + Redis (broker & backend)
- **WebSockets** : Django Channels + Redis (Channel Layers)
- **Déploiement** : Railway (PostgreSQL, Redis, workers Celery)
- **API** : REST + WebSockets pour temps réel (chat, polls)

#### Base de données
- **Principal** : PostgreSQL (production) / SQLite (dev/test)
- **Extensions** : pgvector (recherche sémantique), pg_trgm (recherche full-text)
- **Migrations** : Django migrations versionnées (0019-0023 pour SAKA)

#### Stockage
- **Statique** : WhiteNoise (compression, cache headers) + CDN Vercel
- **Médias** : S3/R2 (production) / FileSystemStorage (dev) - voir section 3

### Flux critiques

#### Authentification
1. **JWT** : Access token (60 min) + Refresh token (7 jours) avec rotation
2. **Session** : Django sessions pour WebSockets (Channels)
3. **Permissions** : DRF permissions + groupes Django (Founders, etc.)

#### SAKA (Protocole d'engagement)
1. **Récolte** : `harvest_saka()` → `SakaTransaction` (EARN) → `SakaWallet.balance++`
2. **Plantation** : `spend_saka()` → `SakaTransaction` (SPEND) → `SakaWallet.balance--`
3. **Boost projet** : Transaction atomique → verrouillage wallet + projet → `Projet.saka_score++`
4. **Compost** : Tâche Celery périodique → `SakaCompostLog` (lié à `SakaCycle`) → `SakaSilo.total_balance++`
5. **Cycles** : `SakaCycle` agrège les stats par période → `get_cycle_stats()` calcule récolté/planté/composté

#### Cagnottes / Projets
1. **Création** : `Projet` → `Cagnotte` (optionnel) → `Contribution`
2. **Financement** : `WalletTransaction` (PLEDGE_DONATION) → `Cagnotte.montant_collecte++`
3. **Boost SAKA** : `POST /api/projets/<pk>/boost/` → `Projet.saka_score++`

---

## 3. Stockage & Fichiers (S3 / R2)

### Pourquoi Object Storage en production

Le disque Railway est **éphémère** : lors d'un redéploiement ou d'un restart, les fichiers uploadés sur le système de fichiers local sont perdus. Les médias (images de projets, avatars, documents) doivent donc être stockés dans un **Object Storage** persistant (S3, R2, ou équivalent).

### Configuration conditionnelle

Le code utilise `DEFAULT_FILE_STORAGE` conditionné par la variable d'environnement `USE_S3_STORAGE` :

```python
# backend/config/settings.py
USE_S3_STORAGE = os.environ.get('USE_S3_STORAGE', 'False').lower() == 'true'

if USE_S3_STORAGE:
    # Configuration S3/R2 (Cloudflare R2 ou AWS S3)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # Variables requises : R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_ENDPOINT_URL
else:
    # Stockage local (développement uniquement)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
```

### Stratégie de déploiement

- **En local/dev** : On reste sur `FileSystemStorage` (simple, rapide pour les tests)
- **En production** : On bascule sur S3-like (R2 Cloudflare recommandé pour la compatibilité S3 + CDN intégré)

### Variables d'environnement requises (production)

```env
USE_S3_STORAGE=True
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET_NAME=egoejo-media
R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
R2_CUSTOM_DOMAIN=media.egoejo.org  # Optionnel (CDN)
```

---

## 4. Service Layer & Organisation du code

### Principe de séparation des responsabilités

L'architecture suit une séparation claire des responsabilités :

- **`models.py`** → Uniquement les données et la logique très bas niveau (méthodes de modèle, propriétés calculées)
- **`api/*.py`** → Orchestration HTTP (validation des requêtes, formatage des réponses, permissions)
- **`services/*.py`** → Logique métier réutilisable (SAKA, boosting, calcul 4P, stats)

### Exemples concrets

#### SAKA : Services de transaction

**Fichier** : `backend/core/services/saka.py`

```python
@transaction.atomic
def harvest_saka(user, reason: SakaReason, amount: Optional[int] = None) -> Optional[SakaTransaction]:
    """Récolter des grains SAKA (Proof of Care)"""
    # Logique : vérification limites quotidiennes, création transaction, mise à jour wallet
    ...

@transaction.atomic
def spend_saka(user, amount: int, reason: str, metadata: Optional[dict] = None) -> bool:
    """Dépenser des grains SAKA (vote, boost) - SÉCURISÉ avec select_for_update()"""
    # Logique : vérification solde, verrouillage wallet, création transaction
    # Protection contre les race conditions via verrous pessimistes
    ...
```

**Utilisation dans les vues** : `backend/core/api/projects.py`

```python
@api_view(['POST'])
def boost_project(request, pk):
    # Validation HTTP
    cost = int(request.data.get("amount", 10))
    
    # Transaction atomique globale avec verrouillage
    with transaction.atomic():
        project = Projet.objects.select_for_update().get(pk=pk)
        
        # Appel service (logique métier avec verrous)
        if not spend_saka(request.user, cost, reason="project_boost"):
            return Response({"detail": "Solde insuffisant"}, status=400)
        
        # Mise à jour projet (atomique)
        Projet.objects.filter(id=project.id).update(saka_score=F('saka_score') + cost)
```

#### Stats SAKA : Services de calcul

**Fichier** : `backend/core/services/saka_stats.py`

```python
def get_saka_global_stats() -> Dict:
    """Statistiques globales SAKA (utilisateurs, balances, compost)"""
    # Agrégations ORM optimisées
    ...

def get_saka_daily_stats(days: int = 30) -> List[Dict]:
    """Série temporelle des transactions SAKA par jour"""
    # Groupement par date, agrégations
    ...

def get_top_saka_users(limit: int = 10) -> List[Dict]:
    """Top utilisateurs par balance SAKA"""
    # Tri, limite, sérialisation
    ...

def get_cycle_stats(cycle: SakaCycle) -> Dict:
    """Statistiques SAKA pour un cycle donné (récolté, planté, composté par période)"""
    # Agrégation des transactions dans la période du cycle
    # Somme des compost logs liés au cycle
    ...
```

**Utilisation dans les vues** : `backend/core/api/saka_views.py`

```python
@api_view(["GET"])
def saka_stats_view(request):
    # Appel services (logique métier)
    global_stats = get_saka_global_stats()
    daily_stats = get_saka_daily_stats(days=30)
    top_users = get_top_saka_users(limit=10)
    
    # Formatage réponse HTTP
    return Response({"enabled": True, "global": global_stats, ...})

@api_view(["GET"])
def saka_cycles_view(request):
    """Liste des cycles SAKA avec leurs statistiques"""
    cycles = SakaCycle.objects.all().order_by('-start_date')
    
    data = []
    for cycle in cycles:
        stats = get_cycle_stats(cycle)  # Service de calcul
        data.append({
            "id": cycle.id,
            "name": cycle.name,
            "start_date": cycle.start_date.isoformat(),
            "end_date": cycle.end_date.isoformat(),
            "is_active": cycle.is_active,
            "stats": stats,  # Récolté, planté, composté pour cette période
        })
    
    return Response(data)
```

### Avantages de cette organisation

1. **Tests unitaires facilités** : Les services sont testables indépendamment des vues HTTP
2. **Réutilisabilité** : Un service peut être appelé depuis une vue, une tâche Celery, ou un management command
3. **Préparation à l'évolution** : Si besoin de microservices plus tard, les services sont déjà isolés et peuvent être extraits
4. **Maintenabilité** : La logique métier est centralisée, pas dispersée dans les vues

---

## 5. Performance & Cache

### Stratégie de cache avec Redis

Redis est utilisé en priorité pour les données **publiques et agrégées**, jamais pour les données **sensibles ou personnelles**.

#### Données cachées (TTL 60-300s)

- **Stats globales SAKA** : `cache.get('saka_global_stats')` → TTL 300s
- **Listes de projets publiques** : `cache.get('projets_list')` → TTL 60s
- **SakaSilo global** : `cache.get('saka_silo_state')` → TTL 180s
- **Top utilisateurs SAKA** : `cache.get('saka_top_users')` → TTL 300s

#### Données jamais cachées

- **Solde SAKA utilisateur** : Toujours lu depuis la DB (données sensibles, changent fréquemment)
- **Opérations financières** : Wallets, transactions, contributions (données critiques)
- **Données d'authentification** : Tokens, sessions (sécurité)

### Invalidation du cache

Le cache est invalidé lors des **écritures critiques** :

```python
# Exemple : Boost projet
@api_view(['POST'])
def boost_project(request, pk):
    # ... transaction atomique ...
    
    # Invalidation cache après écriture
    cache.delete('projets_list')
    cache.delete('saka_global_stats')
    cache.delete('saka_top_projects')
```

**Après compost** : Le cache des stats globales SAKA est invalidé pour refléter le nouveau solde du Silo.

### Configuration Redis

```python
# backend/config/settings.py
REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL.replace('/0', '/1'),  # DB 1 pour cache
            'KEY_PREFIX': 'egoejo',
            'TIMEOUT': 300,  # 5 minutes par défaut
        }
    }
else:
    # Fallback : cache en mémoire (dev uniquement)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
```

**Note** : Redis DB 0 = Channels, DB 1 = Cache, DB 2 = Celery (séparation logique).

---

## 6. Monitoring & Observabilité

### Sentry : Erreurs & Performance

Sentry est configuré pour capturer les erreurs backend et tracer les performances des endpoints critiques.

#### Erreurs backend

Toutes les exceptions non gérées sont envoyées à Sentry avec contexte :
- User ID, IP, User-Agent
- Variables d'environnement (masquées)
- Stack trace complète

#### Performance Monitoring (Sentry Performance)

Les endpoints suivants sont tracés pour mesurer les temps de réponse :

- **`/api/saka/*`** : Récolte, dépense, stats
- **`/api/projets/<pk>/boost/`** : Boost projet (transaction atomique critique)
- **`/api/polls/<pk>/vote/`** : Vote quadratique avec SAKA
- **Tâches Celery de compost** : `saka_run_compost_cycle` (exécution périodique)

### Métriques importantes à surveiller

#### SAKA : Santé du système nerveux

- **Temps moyen d'un boost** : Objectif < 200ms (transaction atomique)
- **Taux d'erreur sur transactions SAKA** : Objectif < 0.1% (erreurs de solde insuffisant exclues)
- **Nombre de composts par cycle** : Suivi via `SakaCompostLog`
- **Taille du SakaSilo** : `SakaSilo.total_balance` (croissance attendue)

#### Infrastructure

- **Temps de réponse API** : P95 < 500ms (hors endpoints lourds)
- **Taux d'erreur global** : < 1%
- **Utilisation Redis** : Mémoire, connexions
- **Tâches Celery** : Queue length, temps d'exécution

### Dashboard recommandé

Un dashboard (Grafana, Sentry Dashboard, ou équivalent) devrait afficher :
- Temps de réponse par endpoint SAKA
- Volume de transactions SAKA (récolte, dépense, compost)
- État du Silo (balance, cycles, dernière exécution)
- Erreurs critiques (double dépense, solde négatif, etc.)

**Objectif** : Garder un œil permanent sur la santé du "système nerveux" SAKA.

---

## 7. Concurrence & Intégrité des données SAKA

### Approche : Verrous pessimistes + Transactions atomiques

Le protocole SAKA garantit l'intégrité des données même en cas de **concurrence élevée** (plusieurs utilisateurs boostant le même projet simultanément, votes simultanés, etc.).

#### Verrous pessimistes (`select_for_update()`)

Lors des opérations critiques, les wallets et projets sont **verrouillés** pour éviter les race conditions :

```python
# Exemple : Boost projet
with transaction.atomic():
    # Verrouiller le projet (bloque les autres requêtes jusqu'à commit)
    project = Projet.objects.select_for_update().get(pk=pk)
    
    # Verrouiller le wallet (dans spend_saka)
    wallet = SakaWallet.objects.select_for_update().get(user=user)
    
    # Vérifier solde et dépenser
    if wallet.balance < cost:
        return Response({"detail": "Solde insuffisant"}, status=400)
    
    wallet.balance -= cost
    wallet.save()
    
    # Mettre à jour projet
    project.saka_score += cost
    project.save()
```

**Effet** : Si deux requêtes tentent de booster le même projet simultanément, la seconde attend la fin de la première (sérialisation).

#### Transactions atomiques

Toutes les écritures SAKA critiques sont dans des **transactions atomiques** :

```python
@transaction.atomic
def spend_saka(user, amount: int, reason: str) -> bool:
    """Soit tout passe, soit rien ne passe"""
    wallet = SakaWallet.objects.select_for_update().get(user=user)
    
    if wallet.balance < amount:
        return False  # Rollback automatique
    
    wallet.balance -= amount
    wallet.save()
    
    SakaTransaction.objects.create(
        user=user,
        direction='SPEND',
        amount=amount,
        reason=reason
    )
    
    return True  # Commit automatique
```

**Effet** : En cas d'erreur, toutes les modifications sont annulées (pas de solde partiellement débité).

### Tests de concurrence automatisés

Les tests utilisent `TransactionTestCase` (au lieu de `TestCase`) pour tester la concurrence réelle :

```python
# backend/core/tests_saka.py
class SakaConcurrencyTestCase(TransactionTestCase):
    def test_concurrent_boost_double_spend_prevention(self):
        """Deux boosts simultanés ne peuvent pas dépenser plus que disponible"""
        # Test avec threads réels (TransactionTestCase permet la vraie concurrence)
        # Valide que les verrous select_for_update() empêchent la double dépense
        # Vérifie que le solde final est cohérent (jamais négatif)
        ...
```

**Objectif** : Vérifier qu'il n'y a pas de double dépense, de solde négatif, ou de score incohérent.

### Invariants garantis

Le système garantit les invariants suivants :

1. **Un solde SAKA ne devient jamais négatif**
   - Vérification avant chaque dépense
   - Verrouillage du wallet pendant la vérification + débit

2. **Un boost ne peut pas être appliqué si le solde est insuffisant**
   - Vérification dans `spend_saka()` avant la mise à jour du projet
   - Transaction atomique : si `spend_saka()` échoue, le projet n'est pas mis à jour

3. **Les scores de projet (`saka_score`) sont cohérents avec la somme des boosts réussis**
   - Chaque boost réussi incrémente `saka_score` de manière atomique
   - Le score peut être recalculé depuis `SakaProjectSupport.total_saka_spent` si besoin

4. **Les transactions sont traçables**
   - Chaque opération SAKA crée une `SakaTransaction` avec métadonnées
   - Journal complet pour audit et debugging

---

## 8. Alignement avec la philosophie produit

Cette architecture technique permet de supporter les principes fondamentaux d'EGOEJO :

### Temps cyclique (saisons, compost)

Le système SAKA suit un **cycle naturel** (récolte → plantation → compost) plutôt qu'une logique d'accumulation infinie. L'architecture technique le reflète :
- **Modèle `SakaCycle`** : Représente les saisons/cycles SAKA (ex: "Saison 2026 - Printemps") avec période définie (start_date, end_date)
- **Tâches Celery périodiques** : Le compost s'exécute automatiquement (tous les lundis à 3h UTC) et s'associe au cycle actif
- **Modèles de cycle** : `SakaCompostLog` enregistre chaque cycle avec ses paramètres et est lié à un `SakaCycle` (optionnel)
- **Stats temporelles** : `get_cycle_stats()` agrège les montants récoltés, plantés et compostés par période, permettant de suivre l'évolution de l'économie SAKA sur différentes saisons
- **API des cycles** : `GET /api/saka/cycles/` expose les cycles avec leurs statistiques pour le monitoring et l'affichage frontend

### Double métrique (euros / SAKA)

L'architecture sépare strictement les **wallets financiers** (`UserWallet`) et les **wallets SAKA** (`SakaWallet`), permettant de mesurer simultanément :
- **P1 (Performance Financière)** : Euros mobilisés, investissements
- **P2 (Performance Vivante)** : SAKA récolté, engagé, composté

L'endpoint `/api/impact/global-assets/` expose les deux métriques côte à côte, offrant une vision complète de la contribution d'un utilisateur.

### Subsidiarité (décisions au niveau des communautés)

Les boosts SAKA et votes quadratiques permettent aux utilisateurs d'**influencer directement** les projets qu'ils soutiennent, sans passer par une hiérarchie centralisée. L'architecture technique le supporte :
- **Endpoints décentralisés** : `/api/projets/<pk>/boost/` et `/api/polls/<pk>/vote/` sont accessibles à tous les utilisateurs authentifiés
- **Scores agrégés** : `Projet.saka_score` reflète la somme des engagements communautaires
- **Pas de modération centralisée** : Les boosts sont appliqués immédiatement (sous réserve de solde suffisant)

### Préparation à l'ouverture de l'API SAKA (futur)

L'organisation en **services réutilisables** (`core/services/saka.py`, `saka_stats.py`) prépare l'ouverture future de l'API SAKA à des partenaires externes :
- Les services peuvent être exposés via des endpoints dédiés (`/api/saka/external/`)
- La logique métier est déjà isolée et testable
- Les permissions peuvent être étendues (tokens API partenaires)

---

## 9. Prochaines étapes techniques

### Court terme (1-2 mois)

- ✅ **Finaliser configuration S3 en prod** : Activer `USE_S3_STORAGE=True` sur Railway, configurer R2 Cloudflare
- ✅ **Ajouter plus de tests d'intégration SAKA** : Tests boost + compost + cycles dans `tests_saka.py`
- ✅ **Tests de concurrence** : `SakaConcurrencyTestCase` avec threads pour valider la double dépense
- ✅ **Modèle SakaCycle** : Implémenté pour agréger les stats par période
- ⏳ **Exposer un endpoint public (read-only) pour les stats globales SAKA/4P** : `/api/public/saka/stats/` (sans authentification, cache 5 min)
- ⏳ **Documenter les Feature Flags SAKA** : Ajouter une section dans `PROTOCOLE_SAKA_V2.1.md` expliquant `ENABLE_SAKA`, `SAKA_VOTE_ENABLED`, `SAKA_PROJECT_BOOST_ENABLED`, `SAKA_COMPOST_ENABLED`

### Moyen terme (3-6 mois)

- ⏳ **Optimiser les requêtes SAKA** : Ajouter des index sur `SakaTransaction` (user, direction, reason, created_at)
- ⏳ **Mettre en place un dashboard de monitoring SAKA** : Grafana ou Sentry Dashboard avec métriques clés
- ⏳ **Améliorer la résilience Celery** : Retry automatique pour les tâches de compost, alertes sur échecs
- ⏳ **Préparer l'ouverture API SAKA** : Endpoints partenaires, documentation OpenAPI, rate limiting spécifique

### Long terme (6-12 mois)

- ⏳ **Évaluer la nécessité de microservices** : Si le monolithe devient un goulot d'étranglement, extraire les services SAKA dans un service dédié
- ⏳ **Mettre en place un système de redistribution du Silo** : Logique pour redistribuer les grains compostés (mécanisme à définir)
- ⏳ **Intégrer SAKA dans d'autres domaines** : Chat, contenus éducatifs, gouvernance (votes actionnaires V2.0)

---

## 📚 Documentation Complémentaire

- **Protocole SAKA** : `PROTOCOLE_SAKA_V2.1.md`
- **Architecture globale** : `ARCHITECTURE_SLEEPING_GIANT_V1.6_V2.0.md`
- **Configuration** : `backend/config/settings.py`
- **Services SAKA** : `backend/core/services/saka.py`, `saka_stats.py`
- **Tests** : `backend/core/tests_saka.py`

---

**Dernière mise à jour** : 2025-12-16  
**Version** : 2.0.0 🏗️

