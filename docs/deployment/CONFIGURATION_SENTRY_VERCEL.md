# Configuration Sentry dans Vercel

## 📋 Étapes pour configurer VITE_SENTRY_DSN

### 1. Créer un compte Sentry

1. Aller sur https://sentry.io
2. Créer un compte (gratuit)
3. Créer une nouvelle organisation (si nécessaire)

### 2. Créer un projet Sentry

1. Dans le dashboard Sentry, cliquer sur **"Create Project"**
2. Sélectionner **"React"** comme plateforme
3. Donner un nom au projet (ex: "egoejo-frontend")
4. Cliquer sur **"Create Project"**

### 3. Obtenir le DSN

1. Après la création du projet, Sentry affiche le **DSN** (Data Source Name)
2. Le DSN ressemble à : `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`
3. **Copier ce DSN** (vous en aurez besoin)

### 4. Configurer dans Vercel

#### Option A : Via l'interface Vercel (recommandé)

1. Aller sur https://vercel.com
2. Sélectionner votre projet **frontend**
3. Aller dans **Settings** → **Environment Variables**
4. Cliquer sur **"Add New"**
5. Remplir :
   - **Name**: `VITE_SENTRY_DSN`
   - **Value**: Coller le DSN Sentry (ex: `https://xxxxx@xxxxx.ingest.sentry.io/xxxxx`)
   - **Environment**: Sélectionner **Production**, **Preview**, et **Development** (ou seulement Production)
6. Cliquer sur **"Save"**

#### Option B : Via Vercel CLI

```powershell
# Se placer dans le dossier frontend
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Ajouter la variable pour Production
vercel env add VITE_SENTRY_DSN production
# Entrer le DSN quand demandé

# Ajouter pour Preview (branches)
vercel env add VITE_SENTRY_DSN preview
# Entrer le DSN quand demandé

# Ajouter pour Development (optionnel)
vercel env add VITE_SENTRY_DSN development
# Entrer le DSN quand demandé
```

### 5. Redéployer l'application

Après avoir ajouté la variable d'environnement :

1. Aller dans **Deployments** sur Vercel
2. Cliquer sur **"Redeploy"** sur le dernier déploiement
3. Ou pousser un nouveau commit pour déclencher un nouveau déploiement

### 6. Vérifier que Sentry fonctionne

1. Une fois redéployé, visiter votre site en production
2. Aller dans le dashboard Sentry
3. Vous devriez voir des événements apparaître (métriques de performance, etc.)
4. Si vous générez une erreur volontairement, elle devrait apparaître dans Sentry

## 🔍 Vérification

### Vérifier que la variable est bien configurée

```powershell
# Via Vercel CLI
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
vercel env ls
```

Vous devriez voir `VITE_SENTRY_DSN` dans la liste.

### Tester en local (optionnel)

Créer un fichier `.env.local` dans `frontend/frontend/` :

```env
VITE_SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

Puis redémarrer le serveur de développement.

## 📊 Utilisation de Sentry

### Dashboard Sentry

- **Issues** : Liste des erreurs détectées
- **Performance** : Métriques de performance (LCP, FID, CLS, etc.)
- **Releases** : Versions de l'application déployées
- **Alerts** : Alertes configurées

### Configurer des alertes

1. Dans Sentry, aller dans **Alerts** → **Create Alert Rule**
2. Configurer les conditions (ex: erreur critique, LCP > 2.5s)
3. Choisir les canaux de notification (email, Slack, etc.)
4. Sauvegarder

### Métriques disponibles

Le monitoring envoie automatiquement :
- **LCP** (Largest Contentful Paint)
- **FID** (First Input Delay)
- **CLS** (Cumulative Layout Shift)
- **TTFB** (Time to First Byte)
- **PageLoad** (Temps de chargement)
- **API_Duration** (Durée des requêtes API)

## 🚨 Dépannage

### Sentry ne capture pas les erreurs

1. Vérifier que `VITE_SENTRY_DSN` est bien configuré dans Vercel
2. Vérifier que l'application est en production (Sentry est désactivé en développement)
3. Vérifier la console du navigateur pour des erreurs de chargement de Sentry
4. Vérifier que `@sentry/react` est installé (dépendance optionnelle)

### Installer @sentry/react (si nécessaire)

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
npm install @sentry/react
```

## 📝 Notes

- Sentry est **automatiquement désactivé en développement** pour ne pas polluer les logs
- Les métriques sont envoyées **uniquement en production**
- Les erreurs sensibles (tokens, etc.) sont **filtrées automatiquement**
- Le monitoring est **non bloquant** : si Sentry échoue, l'application continue de fonctionner

