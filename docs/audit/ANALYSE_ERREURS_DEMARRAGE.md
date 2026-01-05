# 🔍 ANALYSE DES ERREURS DE DÉMARRAGE
## EGOEJO - Diagnostic Frontend & Backend

**Date** : 2025-12-21  
**Contexte** : Erreurs après démarrage des serveurs backend et frontend

---

## 📋 RÉSUMÉ EXÉCUTIF

### 🔴 Erreur 1 : Frontend - Fichier CSS Manquant
**Erreur** : `ENOENT: no such file or directory, open 'C:\Users\treso\Downloads\egoejo\frontend\design-tokens\tokens.css'`

**Impact** : ⚠️ **BLOQUANT** - Le frontend ne peut pas compiler et affiche une erreur overlay.

### 🔴 Erreur 2 : Backend - Connexion Refusée
**Erreur** : `ERR_CONNECTION_REFUSED` sur `localhost:8000/api/health/`

**Impact** : ⚠️ **BLOQUANT** - Le backend ne répond pas aux requêtes HTTP.

---

## 1. 🔴 ERREUR FRONTEND : Fichier `tokens.css` Manquant

### 1.1 Description de l'Erreur

```
[plugin:vite:css] [postcss] ENOENT: no such file or directory, 
open 'C:\Users\treso\Downloads\egoejo\frontend\design-tokens\tokens.css'
```

**Source** : `frontend/frontend/src/styles/global.css:2`
```css
@import '../design-tokens/tokens.css';
```

### 1.2 Analyse du Chemin

**Chemin relatif dans `global.css`** :
- Fichier : `frontend/frontend/src/styles/global.css`
- Import : `@import '../design-tokens/tokens.css';`
- Chemin résolu : `frontend/frontend/src/design-tokens/tokens.css` ❌

**Chemin attendu selon l'erreur** :
- Erreur : `C:\Users\treso\Downloads\egoejo\frontend\design-tokens\tokens.css`
- Chemin résolu : `frontend/design-tokens/tokens.css` ❌

**Problème** : Le chemin relatif `../design-tokens/tokens.css` depuis `src/styles/global.css` pointe vers `src/design-tokens/tokens.css`, mais le fichier n'existe pas.

### 1.3 Fichiers Utilisant `design-tokens`

**Fichiers référençant `design-tokens`** (12 fichiers) :
1. `frontend/frontend/src/styles/global.css` - Import CSS
2. `frontend/frontend/src/components/HeroSorgho.jsx` - Import JS
3. `frontend/frontend/src/components/MyceliumVisualization.jsx` - Import JS
4. `frontend/frontend/src/contexts/EcoModeContext.jsx` - Import JS
5. `frontend/frontend/src/components/EcoModeToggle.jsx` - Import JS
6. `frontend/frontend/src/components/FullscreenMenu.jsx` - Import JS
7. `frontend/frontend/src/components/CustomCursor.jsx` - Import JS
8. `frontend/frontend/src/components/Loader.jsx` - Import JS
9. `frontend/frontend/src/components/OfflineIndicator.jsx` - Import JS
10. `frontend/frontend/src/components/HeroSorghoLazy.jsx` - Import JS
11. `frontend/frontend/src/app/pages/SakaSeasons.tsx` - Import JS (alias `@/design-tokens`)
12. `frontend/frontend/src/components/CardTilt.jsx` - Import JS

**Imports JavaScript** :
```javascript
import { getSobrietyFeature } from '../design-tokens';
import { SobrietyLevel, getSobrietyConfig } from '../design-tokens';
import { zIndexLayers } from '../design-tokens';
import { breakpoints } from '../design-tokens';
import { getSobrietyFeature } from "@/design-tokens"; // Alias @
```

### 1.4 Structure de Répertoires Attendue

**Répertoires existants** :
- ✅ `frontend/frontend/src/styles/` (contient `global.css`, `eco-mode.css`)
- ❌ `frontend/frontend/src/design-tokens/` (n'existe pas)
- ❌ `frontend/design-tokens/` (n'existe pas)

**Structure attendue** :
```
frontend/frontend/src/
  ├── styles/
  │   └── global.css (importe '../design-tokens/tokens.css')
  └── design-tokens/
      ├── tokens.css (❌ MANQUANT)
      └── index.js (probablement, pour les imports JS)
```

### 1.5 Impact

**Blocage** :
- ⚠️ Le frontend ne peut pas compiler (`npm run dev` échoue)
- ⚠️ L'overlay d'erreur Vite bloque l'affichage de l'application
- ⚠️ Tous les composants utilisant `design-tokens` sont affectés

**Composants affectés** :
- `HeroSorgho`, `MyceliumVisualization`, `EcoModeContext`, `EcoModeToggle`, `FullscreenMenu`, `CustomCursor`, `Loader`, `OfflineIndicator`, `HeroSorghoLazy`, `SakaSeasons`, `CardTilt`

---

## 2. 🔴 ERREUR BACKEND : Connexion Refusée

### 2.1 Description de l'Erreur

```
ERR_CONNECTION_REFUSED
localhost a refusé de se connecter.
```

**URL testée** : `http://localhost:8000/api/health/`

### 2.2 Analyse des Processus

**Processus Python actifs** :
```
ProcessName    Id StartTime          
-----------    -- ---------          
python        792 21/12/2025 21:43:44
python       4072 21/12/2025 21:43:42
python      14720 21/12/2025 23:52:20
python      20264 21/12/2025 23:52:24
```

**Processus Node.js actifs** :
```
ProcessName    Id StartTime          
-----------    -- ---------          
node         4660 20/12/2025 02:57:06
node         5720 19/12/2025 22:37:09
node         7560 19/12/2025 22:37:08
node         8752 21/12/2025 23:52:21
node        18384 21/12/2025 23:52:21
node        23488 21/12/2025 21:42:19
node        24320 19/12/2025 22:37:08
node        25040 19/12/2025 23:27:10
node        27516 19/12/2025 23:27:10
node        29500 21/12/2025 21:42:19
node        30512 19/12/2025 17:45:15
```

**Vérification du port 8000** :
```bash
netstat -ano | findstr ":8000"
# Résultat : Aucun processus n'écoute sur le port 8000
```

### 2.3 Causes Possibles

1. **Backend non démarré** :
   - Le processus Python peut être un autre script (migration, test, etc.)
   - Le serveur Django n'a peut-être pas démarré correctement

2. **Erreur au démarrage** :
   - Erreur de configuration (settings.py)
   - Erreur de base de données (connexion impossible)
   - Erreur d'import (module manquant)
   - Port déjà utilisé (mais `netstat` ne montre rien)

3. **Processus en arrière-plan** :
   - Le processus Python peut avoir crashé immédiatement
   - Le processus peut être bloqué sur une erreur

### 2.4 Impact

**Blocage** :
- ⚠️ Le frontend ne peut pas communiquer avec le backend
- ⚠️ Toutes les requêtes API échouent (`ERR_CONNECTION_REFUSED`)
- ⚠️ L'application frontend ne peut pas charger les données

**Fonctionnalités affectées** :
- Authentification (login, register)
- Dashboard (chargement des assets)
- SAKA (historique, compost, silo)
- Projets, contenus, votes
- Chat (WebSocket)

---

## 3. 📊 SYNTHÈSE DES PROBLÈMES

### 3.1 Priorité des Erreurs

| Erreur | Priorité | Impact | Blocage |
|--------|----------|--------|---------|
| Frontend `tokens.css` | 🔴 **CRITIQUE** | Compilation impossible | ✅ OUI |
| Backend `ERR_CONNECTION_REFUSED` | 🔴 **CRITIQUE** | API inaccessible | ✅ OUI |

### 3.2 Dépendances

**Ordre de résolution recommandé** :
1. **D'abord** : Résoudre l'erreur `tokens.css` (frontend)
2. **Ensuite** : Résoudre l'erreur backend (connexion refusée)

**Raison** : Le frontend doit compiler avant de pouvoir tester la connexion au backend.

---

## 4. 🔍 DIAGNOSTIC DÉTAILLÉ

### 4.1 Frontend : Fichier `tokens.css` Manquant

**Hypothèses** :
1. **Fichier jamais créé** : Le répertoire `design-tokens` n'a jamais été créé
2. **Fichier supprimé** : Le fichier a été supprimé par erreur
3. **Chemin incorrect** : Le chemin relatif dans `global.css` est incorrect
4. **Fichier dans un autre emplacement** : Le fichier existe ailleurs mais pas au bon endroit

**Vérifications nécessaires** :
- ✅ Recherche globale : Aucun fichier `tokens.css` trouvé dans `frontend/`
- ✅ Répertoires : `frontend/frontend/src/design-tokens/` n'existe pas
- ✅ Imports JS : 11 fichiers importent depuis `../design-tokens` (structure attendue : `src/design-tokens/index.js`)

**Conclusion** : Le répertoire `design-tokens` et ses fichiers (`tokens.css`, `index.js`) sont **complètement manquants**.

### 4.2 Backend : Connexion Refusée

**Hypothèses** :
1. **Processus crashé** : Le serveur Django a crashé au démarrage
2. **Erreur silencieuse** : Le processus tourne mais n'écoute pas sur le port 8000
3. **Port différent** : Le serveur écoute sur un autre port
4. **Erreur de configuration** : Problème dans `settings.py` ou variables d'environnement

**Vérifications nécessaires** :
- ⚠️ `netstat` : Aucun processus n'écoute sur le port 8000
- ⚠️ Processus Python : 4 processus actifs mais aucun n'écoute sur 8000
- ⚠️ Logs : Pas de logs visibles (processus en arrière-plan)

**Conclusion** : Le serveur Django **n'est pas démarré** ou **a crashé immédiatement**.

---

## 5. 🎯 RECOMMANDATIONS

### 5.1 Frontend : Créer le Répertoire `design-tokens`

**Actions requises** :
1. Créer le répertoire `frontend/frontend/src/design-tokens/`
2. Créer le fichier `tokens.css` avec les variables CSS nécessaires
3. Créer le fichier `index.js` pour les exports JavaScript (si nécessaire)

**Structure attendue** :
```
frontend/frontend/src/design-tokens/
  ├── tokens.css (variables CSS)
  └── index.js (exports JS : getSobrietyFeature, SobrietyLevel, zIndexLayers, breakpoints, etc.)
```

### 5.2 Backend : Vérifier le Démarrage

**Actions requises** :
1. Vérifier les logs du processus Python (erreurs au démarrage)
2. Vérifier la configuration (`settings.py`, variables d'environnement)
3. Vérifier la base de données (connexion possible)
4. Redémarrer le serveur en mode visible (pas en arrière-plan) pour voir les erreurs

**Commandes de diagnostic** :
```bash
# Vérifier les erreurs
cd backend
python manage.py check
python manage.py runserver 8000

# Vérifier la base de données
python manage.py migrate --check
```

---

## 6. 📝 CONCLUSION

### État Actuel

- 🔴 **Frontend** : Bloqué par fichier CSS manquant (`tokens.css`)
- 🔴 **Backend** : Bloqué par connexion refusée (serveur non démarré ou crashé)

### Actions Immédiates

1. **Créer le répertoire `design-tokens`** avec les fichiers nécessaires
2. **Diagnostiquer le backend** en mode visible pour voir les erreurs
3. **Vérifier les dépendances** (npm install, pip install)

### Prochaines Étapes

Une fois les erreurs corrigées :
- Tester la compilation frontend (`npm run dev`)
- Tester le démarrage backend (`python manage.py runserver`)
- Vérifier la connexion frontend → backend (`/api/health/`)

---

**Date de génération** : 2025-12-21  
**Version** : 1.0.0

