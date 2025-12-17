# Audit des Tests Frontend (Vitest) - EGOEJO

**Date** : 2025-01-16  
**Objectif** : Inventaire des tests existants et plan de complétion

---

## 📊 Inventaire des Tests Existants

### Tests de Pages (`src/app/pages/__tests__/`)

| Page | Fichier de Test | Statut |
|------|----------------|--------|
| **Home** | `Home.test.jsx` | ✅ Testé |
| **Rejoindre** | `Rejoindre.test.jsx` | ✅ Testé |
| **Admin** | `Admin.test.jsx` | ✅ Testé |
| **Votes** | `Votes.test.jsx` | ✅ Testé |
| **Contenus** | `Contenus.test.jsx` | ✅ Testé |
| **Alliances** | `Alliances.test.jsx` | ✅ Testé |
| **Communaute** | `Communaute.test.jsx` | ✅ Testé |
| **Vision** | `Vision.test.jsx` | ✅ Testé |
| **Projets** | `Projets.test.jsx` | ✅ Testé (basique) |
| **Univers** | `Univers.test.jsx` | ✅ Testé |
| **NotFound** | `NotFound.test.jsx` | ✅ Testé |
| **Chat** | `Chat.test.jsx` | ✅ Testé |
| **SakaSeasons** | `SakaSeasons.test.tsx` | ✅ Testé |
| **Dashboard** | ❌ **MANQUANT** | 🔴 Critique |
| **SakaMonitor** | ❌ **MANQUANT** | 🔴 Critique |
| **SakaSilo** | ❌ **MANQUANT** | 🟡 Important |
| **Login** | ❌ **MANQUANT** | 🟡 Important |
| **Register** | ❌ **MANQUANT** | 🟡 Important |
| **Impact** | ❌ **MANQUANT** | 🟡 Important |
| **MyCard** | ❌ **MANQUANT** | 🟢 Optionnel |
| **Mycelium** | ❌ **MANQUANT** | 🟢 Optionnel |
| **Podcast** | ❌ **MANQUANT** | 🟢 Optionnel |
| **RacinesPhilosophie** | ❌ **MANQUANT** | 🟢 Optionnel |
| **Citations** | ❌ **MANQUANT** | 🟢 Optionnel |

### Tests de Composants (`src/components/__tests__/`)

| Composant | Fichier de Test | Statut |
|-----------|----------------|--------|
| **FourPStrip** | `FourPStrip.test.jsx` | ✅ Testé |
| **SakaSeasonBadge** | `SakaSeasonBadge.test.jsx` | ✅ Testé |
| **Button** | `Button.test.jsx` | ✅ Testé |
| **Input** | `Input.test.jsx` | ✅ Testé |
| **Navbar** | `Navbar.test.jsx` | ✅ Testé |
| **Layout** | `Layout.test.jsx` | ✅ Testé |
| **Loader** | `Loader.test.jsx` | ✅ Testé |
| **ErrorBoundary** | `ErrorBoundary.test.jsx` | ✅ Testé |
| **ChatWindow** | `ChatWindow.test.jsx` | ✅ Testé |
| **ChatList** | `ChatList.test.jsx` | ✅ Testé |
| **FullscreenMenu** | `FullscreenMenu.test.jsx` | ✅ Testé |
| **CustomCursor** | `CustomCursor.test.jsx` | ✅ Testé |
| **UserImpact4P** | ❌ **MANQUANT** | 🔴 Critique |
| **Impact4PCard** | ❌ **MANQUANT** | 🔴 Critique |
| **QuadraticVote** | ❌ **MANQUANT** | 🟡 Important |
| **SemanticSearch** | ❌ **MANQUANT** | 🟡 Important |
| **Notification** | ❌ **MANQUANT** | 🟡 Important |
| **NotificationContainer** | ❌ **MANQUANT** | 🟡 Important |
| **EcoModeToggle** | ❌ **MANQUANT** | 🟢 Optionnel |
| **LanguageSelector** | ❌ **MANQUANT** | 🟢 Optionnel |
| **HeroSorgho** | ❌ **MANQUANT** | 🟢 Optionnel |
| **MyceliumVisualization** | ❌ **MANQUANT** | 🟢 Optionnel |
| **CardTilt** | ❌ **MANQUANT** | 🟢 Optionnel |
| **AudioPlayer** | ❌ **MANQUANT** | 🟢 Optionnel |

### Tests de Hooks (`src/hooks/__tests__/`)

| Hook | Fichier de Test | Statut |
|------|----------------|--------|
| **useFetch** | `useFetch.test.js` | ✅ Testé |
| **useLocalStorage** | `useLocalStorage.test.js` | ✅ Testé |
| **useDebounce** | `useDebounce.test.js` | ✅ Testé |
| **useToggle** | `useToggle.test.js` | ✅ Testé |
| **useMediaQuery** | `useMediaQuery.test.js` | ✅ Testé |
| **useClickOutside** | `useClickOutside.test.jsx` | ✅ Testé |
| **useGlobalAssets** | ❌ **MANQUANT** | 🔴 Critique |
| **useSaka** | ❌ **MANQUANT** | 🔴 Critique |
| **useSakaSilo** | ❌ **MANQUANT** | 🔴 Critique |
| **useSakaCycles** | ❌ **MANQUANT** | 🔴 Critique |
| **useNotification** | ❌ **MANQUANT** | 🟡 Important |
| **useSEO** | ❌ **MANQUANT** | 🟡 Important |
| **useWebSocket** | ❌ **MANQUANT** | 🟡 Important |
| **useEasterEgg** | ❌ **MANQUANT** | 🟢 Optionnel |
| **useLowPowerMode** | ❌ **MANQUANT** | 🟢 Optionnel |

### Tests de Contextes (`src/contexts/__tests__/`)

| Contexte | Fichier de Test | Statut |
|----------|----------------|--------|
| **AuthContext** | `AuthContext.test.jsx` | ✅ Testé |
| **LanguageContext** | ❌ **MANQUANT** | 🟡 Important |
| **NotificationContext** | ❌ **MANQUANT** | 🟡 Important |
| **EcoModeContext** | ❌ **MANQUANT** | 🟢 Optionnel |

### Tests Utilitaires (`src/utils/__tests__/`)

| Utilitaire | Fichier de Test | Statut |
|------------|----------------|--------|
| **api** | `api.test.js` | ✅ Testé |
| **format** | `format.test.js` | ✅ Testé |
| **validation** | `validation.test.js` | ✅ Testé |
| **backend-connection** | `backend-connection.test.js` | ✅ Testé |
| **integration-backend** | `integration-backend.test.js` | ✅ Testé |
| **performance** | `performance.test.js` | ✅ Testé |
| **security** | `security.test.js` | ✅ Testé |
| **money** | ❌ **MANQUANT** | 🟡 Important |
| **i18n** | ❌ **MANQUANT** | 🟡 Important |
| **logger** | ❌ **MANQUANT** | 🟢 Optionnel |
| **analytics** | ❌ **MANQUANT** | 🟢 Optionnel |
| **gdpr** | ❌ **MANQUANT** | 🟢 Optionnel |

### Tests d'Intégration (`src/__tests__/`)

| Domaine | Fichier de Test | Statut |
|---------|----------------|--------|
| **API Integration** | `integration/api.test.jsx` | ✅ Testé |
| **Router** | `app/__tests__/router.test.jsx` | ✅ Testé |
| **Navigation** | `app/__tests__/navigation.test.jsx` | ✅ Testé |
| **Chat Integration** | `app/__tests__/chat-integration.test.jsx` | ✅ Testé |
| **Accessibility** | `accessibility/*.test.jsx` | ✅ Testé (4 fichiers) |
| **Performance** | `performance/*.test.js` | ✅ Testé (3 fichiers) |

---

## 🎯 Plan de Complétion

### Priorité 🔴 (Critique)

#### Pages Manquantes

1. **`src/app/pages/__tests__/Dashboard.test.jsx`**
   - Page critique : affiche le patrimoine utilisateur, 4P, SAKA
   - Scénarios à tester (voir section détaillée ci-dessous)

2. **`src/app/pages/__tests__/SakaMonitor.test.jsx`**
   - Page critique : monitoring SAKA pour admins
   - Scénarios à tester (voir section détaillée ci-dessous)

3. **`src/app/pages/__tests__/SakaSilo.test.jsx`**
   - Page importante : affichage du Silo Commun SAKA
   - Scénarios : affichage du solde, historique, redistribution

#### Composants Manquants

4. **`src/components/__tests__/UserImpact4P.test.jsx`**
   - Composant critique : affiche l'impact 4P utilisateur
   - Scénarios : calcul P1/P2/P3/P4, affichage avec/without data, tooltips proxy

5. **`src/components/__tests__/Impact4PCard.test.jsx`**
   - Composant critique : affiche les scores 4P d'un projet
   - Scénarios : mode compact/full, affichage des 4 dimensions, tooltips proxy

#### Hooks Manquants

6. **`src/hooks/__tests__/useGlobalAssets.test.js`**
   - Hook critique : récupère les assets globaux (financier, SAKA, impact)
   - Scénarios : fetch réussi, erreur API, loading state, refetch

7. **`src/hooks/__tests__/useSaka.test.js`**
   - Hook critique : gestion SAKA (balance, compost, stats)
   - Scénarios : fetch balance, compost preview, stats, erreurs

8. **`src/hooks/__tests__/useSakaSilo.test.ts`**
   - Hook critique : récupère les données du Silo Commun
   - Scénarios : fetch réussi, erreur, loading, structure des données

9. **`src/hooks/__tests__/useSakaCycles.test.ts`**
   - Hook critique : récupère les cycles SAKA
   - Scénarios : fetch réussi, liste des cycles, stats par cycle

### Priorité 🟡 (Important)

#### Pages

10. **`src/app/pages/__tests__/Login.test.jsx`**
    - Scénarios : formulaire valide/invalide, erreur API, redirection après login

11. **`src/app/pages/__tests__/Register.test.jsx`**
    - Scénarios : formulaire valide/invalide, validation email/password, erreur API

12. **`src/app/pages/__tests__/Impact.test.jsx`**
    - Scénarios : affichage des métriques d'impact, graphiques, filtres

#### Composants

13. **`src/components/__tests__/QuadraticVote.test.jsx`**
    - Scénarios : sélection d'intensité, calcul du coût SAKA, soumission du vote

14. **`src/components/__tests__/SemanticSearch.test.jsx`**
    - Scénarios : recherche, suggestions, résultats, erreurs

15. **`src/components/__tests__/Notification.test.jsx`**
    - Scénarios : affichage success/error/info, auto-dismiss, actions

16. **`src/components/__tests__/NotificationContainer.test.jsx`**
    - Scénarios : gestion de plusieurs notifications, queue, position

#### Hooks

17. **`src/hooks/__tests__/useNotification.test.js`**
    - Scénarios : showSuccess, showError, showInfo, auto-dismiss

18. **`src/hooks/__tests__/useSEO.test.js`**
    - Scénarios : génération des meta tags, JSON-LD, title/description

19. **`src/hooks/__tests__/useWebSocket.test.js`**
    - Scénarios : connexion, messages, déconnexion, reconnexion

#### Contextes

20. **`src/contexts/__tests__/LanguageContext.test.jsx`**
    - Scénarios : changement de langue, persistance, fallback

21. **`src/contexts/__tests__/NotificationContext.test.jsx`**
    - Scénarios : ajout/suppression de notifications, queue management

#### Utilitaires

22. **`src/utils/__tests__/money.test.js`**
    - Scénarios : formatMoney, toDecimal, arrondis, devises

23. **`src/utils/__tests__/i18n.test.js`**
    - Scénarios : traduction, interpolation, fallback, pluriels

### Priorité 🟢 (Optionnel)

- Pages : MyCard, Mycelium, Podcast, RacinesPhilosophie, Citations
- Composants : EcoModeToggle, LanguageSelector, HeroSorgho, MyceliumVisualization, CardTilt, AudioPlayer
- Hooks : useEasterEgg, useLowPowerMode
- Contextes : EcoModeContext
- Utilitaires : logger, analytics, gdpr

---

## 📝 Scénarios de Tests Détaillés pour Pages Critiques

### 1. Dashboard (`src/app/pages/__tests__/Dashboard.test.jsx`)

#### Scénario 1 : Affichage des 3 blocs 4P
- **Setup** : Mock `useGlobalAssets` avec données complètes (financial, saka, impact)
- **Actions** : Rendre `<Dashboard />`
- **Assertions** :
  - `FourPStrip` est affiché avec les 3 valeurs (financial, saka, impact)
  - `UserImpact4P` est affiché avec les 4 dimensions calculées
  - `SakaSeasonBadge` est affiché avec le bon badge selon le solde SAKA

#### Scénario 2 : Comportement en erreur API
- **Setup** : Mock `useGlobalAssets` pour retourner une erreur
- **Actions** : Rendre `<Dashboard />`
- **Assertions** :
  - Message d'erreur affiché
  - Bouton "Réessayer" présent
  - Les composants 4P ne sont pas affichés (ou affichent des valeurs par défaut)

#### Scénario 3 : Affichage du graphique de répartition
- **Setup** : Mock `useGlobalAssets` avec données de pockets (cash, donations, equity)
- **Actions** : Rendre `<Dashboard />`
- **Assertions** :
  - Graphique PieChart est rendu
  - Les 3 segments sont présents avec les bonnes couleurs
  - La légende affiche les montants corrects

#### Scénario 4 : Transfert vers pocket
- **Setup** : Mock `fetchAPI` pour `/api/wallet/pockets/transfer/`
- **Actions** :
  - Ouvrir le modal de transfert
  - Remplir le formulaire
  - Soumettre
- **Assertions** :
  - Requête API avec les bons paramètres
  - Notification de succès affichée
  - Assets rechargés après transfert

### 2. Projets (`src/app/pages/__tests__/Projets.test.jsx` - Compléter)

#### Scénario 1 : Affichage de la liste des projets avec Impact4P
- **Setup** : Mock `fetchAPI('/projets/')` avec projets incluant `impact_4p`
- **Actions** : Rendre `<Projets />`
- **Assertions** :
  - Liste des projets affichée
  - `Impact4PCard` présent pour chaque projet avec `impact_4p`
  - Scores 4P affichés correctement (P1, P2, P3, P4)

#### Scénario 2 : Boost SAKA d'un projet
- **Setup** :
  - Mock `useGlobalAssets` avec solde SAKA suffisant (ex: 100)
  - Mock `fetchAPI` pour `/api/saka/projects/<id>/boost/`
- **Actions** :
  - Cliquer sur le bouton "Boost" d'un projet
  - Confirmer
- **Assertions** :
  - Requête API avec `project_id` et `amount=10`
  - Notification de succès
  - Solde SAKA mis à jour (100 → 90)
  - Badge "Boosté" affiché sur le projet

#### Scénario 3 : Erreur lors du boost (solde insuffisant)
- **Setup** :
  - Mock `useGlobalAssets` avec solde SAKA insuffisant (ex: 5)
  - Mock `fetchAPI` pour retourner 400 "Solde insuffisant"
- **Actions** :
  - Cliquer sur le bouton "Boost"
- **Assertions** :
  - Message d'erreur affiché
  - Solde SAKA non modifié
  - Bouton "Boost" désactivé ou message explicite

#### Scénario 4 : Filtrage et recherche
- **Setup** : Mock `fetchAPI` avec plusieurs projets
- **Actions** :
  - Utiliser le champ de recherche
  - Appliquer un filtre (catégorie, statut)
- **Assertions** :
  - Requête API avec les bons query params
  - Liste filtrée affichée correctement

### 3. SakaMonitor (`src/app/pages/__tests__/SakaMonitor.test.jsx`)

#### Scénario 1 : Affichage des KPIs SAKA
- **Setup** :
  - Mock `useAuth` avec user admin
  - Mock `useSakaStats` avec données de stats
- **Actions** : Rendre `<SakaMonitor />`
- **Assertions** :
  - Graphique LineChart affiché avec les données
  - Métriques clés affichées (total harvested, planted, composted)
  - Filtres (days, limit) fonctionnels

#### Scénario 2 : Exécution d'un dry-run de compost
- **Setup** :
  - Mock `useSakaCompostRun` avec fonction `runCompostDryRun`
  - Mock `fetchAPI` pour `/api/saka/compost/preview/`
- **Actions** :
  - Cliquer sur "Dry Run"
  - Attendre le résultat
- **Assertions** :
  - Requête API effectuée
  - Résultat affiché (wallets affectés, montant composté)
  - Log de compost créé avec `dry_run=true`

#### Scénario 3 : Affichage des logs de compost
- **Setup** : Mock `useSakaCompostLogs` avec liste de logs
- **Actions** : Rendre `<SakaMonitor />`
- **Assertions** :
  - Table des logs affichée
  - Colonnes : date, wallets_affected, total_composted, source, dry_run
  - Logs triés par date décroissante

#### Scénario 4 : Accès refusé pour non-admin
- **Setup** : Mock `useAuth` avec user non-admin
- **Actions** : Rendre `<SakaMonitor />`
- **Assertions** :
  - Message "Accès réservé aux administrateurs" affiché
  - Aucun graphique ou données affichées

#### Scénario 5 : Comportement en erreur API
- **Setup** : Mock `useSakaStats` pour retourner une erreur
- **Actions** : Rendre `<SakaMonitor />`
- **Assertions** :
  - Message d'erreur affiché
  - Bouton "Réessayer" présent
  - Graphiques non affichés

---

## 📋 Liste de Fichiers de Tests à Créer

### Priorité 🔴 (Critique - 9 fichiers)

1. `src/app/pages/__tests__/Dashboard.test.jsx`
2. `src/app/pages/__tests__/SakaMonitor.test.jsx`
3. `src/app/pages/__tests__/SakaSilo.test.jsx`
4. `src/components/__tests__/UserImpact4P.test.jsx`
5. `src/components/__tests__/Impact4PCard.test.jsx`
6. `src/hooks/__tests__/useGlobalAssets.test.js`
7. `src/hooks/__tests__/useSaka.test.js`
8. `src/hooks/__tests__/useSakaSilo.test.ts`
9. `src/hooks/__tests__/useSakaCycles.test.ts`

### Priorité 🟡 (Important - 14 fichiers)

10. `src/app/pages/__tests__/Login.test.jsx`
11. `src/app/pages/__tests__/Register.test.jsx`
12. `src/app/pages/__tests__/Impact.test.jsx`
13. `src/components/__tests__/QuadraticVote.test.jsx`
14. `src/components/__tests__/SemanticSearch.test.jsx`
15. `src/components/__tests__/Notification.test.jsx`
16. `src/components/__tests__/NotificationContainer.test.jsx`
17. `src/hooks/__tests__/useNotification.test.js`
18. `src/hooks/__tests__/useSEO.test.js`
19. `src/hooks/__tests__/useWebSocket.test.js`
20. `src/contexts/__tests__/LanguageContext.test.jsx`
21. `src/contexts/__tests__/NotificationContext.test.jsx`
22. `src/utils/__tests__/money.test.js`
23. `src/utils/__tests__/i18n.test.js`

### Priorité 🟢 (Optionnel - 15+ fichiers)

- Pages : MyCard, Mycelium, Podcast, RacinesPhilosophie, Citations
- Composants : EcoModeToggle, LanguageSelector, HeroSorgho, MyceliumVisualization, CardTilt, AudioPlayer
- Hooks : useEasterEgg, useLowPowerMode
- Contextes : EcoModeContext
- Utilitaires : logger, analytics, gdpr

---

## 📊 Résumé Statistique

- **Tests existants** : ~51 fichiers
- **Tests manquants (critique)** : 9 fichiers
- **Tests manquants (important)** : 14 fichiers
- **Tests manquants (optionnel)** : 15+ fichiers
- **Taux de couverture estimé** : ~60% (pages critiques), ~40% (composants critiques), ~30% (hooks critiques)

---

## 🎯 Recommandations

1. **Prioriser les tests critiques** : Dashboard, SakaMonitor, hooks SAKA
2. **Compléter les tests existants** : Projets.test.jsx est basique, ajouter les scénarios de boost SAKA
3. **Tester les intégrations** : Vérifier que les hooks et composants fonctionnent ensemble
4. **Mocking cohérent** : Utiliser MSW (Mock Service Worker) pour les appels API
5. **Tests d'accessibilité** : Maintenir la couverture a11y existante

---

**Prochaine étape** : Créer les tests critiques dans l'ordre de priorité défini.

