# Scénarios E2E Critiques Manquants

**Date** : 2025-01-27  
**Objectif** : Identifier les scénarios E2E critiques non couverts pour garantir 100% des flux utilisateur

---

## 📋 Scénarios Critiques Identifiés

### ✅ Scénarios Déjà Couverts

1. **Navigation** (`e2e/navigation.spec.js`)
   - ✅ Navigation entre toutes les pages principales
   - ✅ Gestion de la page 404
   - ✅ Bouton retour du navigateur

2. **Formulaire Rejoindre** (`e2e/rejoindre.spec.js`)
   - ✅ Affichage du formulaire
   - ✅ Validation des champs requis
   - ✅ Soumission avec données valides
   - ✅ Protection contre le spam (honeypot)

3. **Cycle SAKA Full-Stack** (`e2e/saka-cycle-fullstack.spec.js`)
   - ✅ Création utilisateur
   - ✅ Récolte SAKA (lecture contenu)
   - ✅ Plantation (boost projet)
   - ⚠️ Compost (inactivité) - **PARTIELLEMENT COUVERT** (nécessite backend réel)

4. **Vote Quadratique** (`e2e/votes-quadratic.spec.js`)
   - ✅ Affichage de la page Votes
   - ✅ Interface de vote quadratique
   - ⚠️ **MANQUE** : Flux complet avec authentification

5. **Boost Projet SAKA** (`e2e/projects-saka-boost.spec.js`)
   - ✅ Affichage des projets
   - ✅ Boost avec SAKA
   - ⚠️ **MANQUE** : Vérification du solde SAKA après boost

---

## 🔴 Scénarios Critiques Manquants

### 1. **Flux Complet : Création Compte → Réception SAKA → Vote Quadratique**

**Fichier à créer** : `e2e/flux-complet-saka-vote.spec.js`

**Scénario** :
1. ✅ Créer un compte utilisateur (POST `/api/auth/register/`)
2. ✅ S'authentifier (POST `/api/auth/login/`)
3. ✅ Lire un contenu éducatif (POST `/api/contents/<id>/mark-consumed/`)
4. ✅ Vérifier que le solde SAKA a augmenté (GET `/api/impact/global-assets/`)
5. ❌ **MANQUE** : Accéder à la page Votes (`/votes`)
6. ❌ **MANQUE** : Sélectionner un sondage actif
7. ❌ **MANQUE** : Distribuer des points dans le vote quadratique
8. ❌ **MANQUE** : Utiliser l'intensité SAKA (multiplier les points)
9. ❌ **MANQUE** : Soumettre le vote
10. ❌ **MANQUE** : Vérifier que le SAKA a été dépensé

**Priorité** : 🔴 **CRITIQUE**

**Tags** : `@fullstack`, `@saka`, `@vote`

---

### 2. **Flux Complet : Création Projet → Validation → Financement EUR**

**Fichier à créer** : `e2e/flux-complet-projet-financement.spec.js`

**Scénario** :
1. ❌ **MANQUE** : Créer un projet (POST `/api/projets/`) - nécessite authentification admin/editor
2. ❌ **MANQUE** : Vérifier que le projet est en statut "draft" ou "pending"
3. ❌ **MANQUE** : Publier le projet (POST `/api/projets/<id>/publish/`) - admin uniquement
4. ❌ **MANQUE** : Accéder à la page Projets (`/projets`)
5. ❌ **MANQUE** : Vérifier que le projet publié est visible
6. ❌ **MANQUE** : Cliquer sur "Soutenir" ou "Financer"
7. ❌ **MANQUE** : Remplir le formulaire de financement EUR (montant, méthode de paiement)
8. ❌ **MANQUE** : Soumettre le financement (POST `/api/wallet/pockets/transfer/` ou équivalent)
9. ❌ **MANQUE** : Vérifier que le projet a reçu le financement (GET `/api/projets/<id>/`)
10. ❌ **MANQUE** : Vérifier que le wallet EUR a été débité

**Priorité** : 🔴 **CRITIQUE**

**Tags** : `@fullstack`, `@projet`, `@financement`, `@eur`

**Note** : Ce flux nécessite :
- Un utilisateur authentifié avec wallet EUR
- Un projet publié
- Potentiellement un mock de Stripe/HelloAsso pour le paiement

---

### 3. **Flux Compostage : Vérifier Visuellement que le Solde Diminue**

**Fichier à créer** : `e2e/flux-compostage-visuel.spec.js`

**Scénario** :
1. ✅ Créer un utilisateur et récolter du SAKA (déjà couvert dans `saka-cycle-fullstack.spec.js`)
2. ❌ **MANQUE** : Vérifier le solde SAKA initial (GET `/api/impact/global-assets/`)
3. ❌ **MANQUE** : Simuler l'inactivité (attendre ou modifier `last_activity_date` via API admin)
4. ❌ **MANQUE** : Déclencher manuellement un cycle de compostage (POST `/api/saka/compost-trigger/` - admin uniquement)
5. ❌ **MANQUE** : Vérifier que le solde SAKA a diminué (GET `/api/impact/global-assets/`)
6. ❌ **MANQUE** : Vérifier que le Silo Commun a augmenté (GET `/api/saka/silo/`)
7. ❌ **MANQUE** : Vérifier visuellement dans l'UI que le solde a changé (page Dashboard ou Wallet)

**Priorité** : 🟡 **MOYEN** (nécessite backend réel + simulation d'inactivité)

**Tags** : `@fullstack`, `@saka`, `@compostage`, `@admin`

**Note** : Ce test nécessite :
- Backend réel avec Celery configuré
- Accès admin pour déclencher le compostage
- Simulation d'inactivité (modification `last_activity_date` ou attente réelle)

---

### 4. **Flux Redistribution Silo : Vérifier que les Wallets Actifs Reçoivent du SAKA**

**Fichier à créer** : `e2e/flux-redistribution-silo.spec.js`

**Scénario** :
1. ❌ **MANQUE** : Créer plusieurs utilisateurs actifs (avec `total_harvested >= 1`)
2. ❌ **MANQUE** : Vérifier que le Silo Commun contient du SAKA (GET `/api/saka/silo/`)
3. ❌ **MANQUE** : Déclencher manuellement une redistribution (POST `/api/saka/redistribute/` - admin uniquement)
4. ❌ **MANQUE** : Vérifier que chaque wallet actif a reçu du SAKA (GET `/api/impact/global-assets/` pour chaque user)
5. ❌ **MANQUE** : Vérifier que le Silo a diminué (GET `/api/saka/silo/`)

**Priorité** : 🟡 **MOYEN**

**Tags** : `@fullstack`, `@saka`, `@redistribution`, `@admin`

---

### 5. **Flux Création Contenu Éducatif → Publication → Récolte SAKA**

**Fichier à créer** : `e2e/flux-contenu-saka.spec.js`

**Scénario** :
1. ❌ **MANQUE** : Créer un contenu éducatif (POST `/api/contents/`) - contributor/editor
2. ❌ **MANQUE** : Vérifier que le contenu est en statut "pending"
3. ❌ **MANQUE** : Publier le contenu (POST `/api/contents/<id>/publish/`) - admin/editor
4. ❌ **MANQUE** : Accéder à la page Contenus (`/contenus`)
5. ❌ **MANQUE** : Ouvrir le contenu publié
6. ❌ **MANQUE** : Lire le contenu (scroll jusqu'à 80% ou plus)
7. ❌ **MANQUE** : Vérifier que le SAKA a été récolté (GET `/api/impact/global-assets/`)
8. ❌ **MANQUE** : Vérifier la transaction SAKA (GET `/api/saka/transactions/`)

**Priorité** : 🟡 **MOYEN**

**Tags** : `@fullstack`, `@contenu`, `@saka`, `@cms`

---

## 📊 Tableau Récapitulatif

| Scénario | Fichier | Priorité | Tags | Statut |
|:---------|:--------|:---------|:-----|:-------|
| **Création Compte → SAKA → Vote** | `flux-complet-saka-vote.spec.js` | 🔴 **CRITIQUE** | `@fullstack`, `@saka`, `@vote` | ❌ **À CRÉER** |
| **Création Projet → Financement EUR** | `flux-complet-projet-financement.spec.js` | 🔴 **CRITIQUE** | `@fullstack`, `@projet`, `@financement` | ❌ **À CRÉER** |
| **Compostage Visuel** | `flux-compostage-visuel.spec.js` | 🟡 **MOYEN** | `@fullstack`, `@saka`, `@compostage` | ❌ **À CRÉER** |
| **Redistribution Silo** | `flux-redistribution-silo.spec.js` | 🟡 **MOYEN** | `@fullstack`, `@saka`, `@redistribution` | ❌ **À CRÉER** |
| **Contenu → Publication → SAKA** | `flux-contenu-saka.spec.js` | 🟡 **MOYEN** | `@fullstack`, `@contenu`, `@saka` | ❌ **À CRÉER** |

---

## 🎯 Recommandations

### Priorité 1 (Immédiat)
1. **Créer `flux-complet-saka-vote.spec.js`** - Flux le plus critique pour valider le cycle SAKA complet
2. **Créer `flux-complet-projet-financement.spec.js`** - Flux critique pour valider le financement EUR

### Priorité 2 (Sous 1 mois)
3. **Créer `flux-compostage-visuel.spec.js`** - Valider l'anti-accumulation
4. **Créer `flux-redistribution-silo.spec.js`** - Valider la redistribution

### Priorité 3 (Amélioration continue)
5. **Créer `flux-contenu-saka.spec.js`** - Valider le CMS et la récolte SAKA

---

## 📝 Notes Techniques

### Prérequis pour les Tests Full-Stack

1. **Backend réel** :
   - Django test server (`python manage.py runserver`)
   - Base de données de test isolée
   - Celery configuré (pour compostage)

2. **Variables d'environnement** :
   ```bash
   BACKEND_URL=http://localhost:8000
   E2E_MODE=fullstack  # Au lieu de mock-only
   ```

3. **Helpers nécessaires** :
   - `createTestUser()` - Créer un utilisateur via API
   - `loginUser()` - Authentifier et obtenir token
   - `getSakaWallet()` - Récupérer le solde SAKA
   - `harvestSaka()` - Récolter du SAKA
   - `spendSaka()` - Dépenser du SAKA
   - `createProject()` - Créer un projet
   - `publishProject()` - Publier un projet
   - `triggerCompost()` - Déclencher un cycle de compostage (admin)

4. **Isolation des tests** :
   - Chaque test doit créer ses propres données
   - Nettoyer après chaque test (ou utiliser des fixtures)
   - Utiliser des noms uniques (timestamp, UUID)

---

**Document généré le** : 2025-01-27  
**Statut** : ✅ Analyse complète

