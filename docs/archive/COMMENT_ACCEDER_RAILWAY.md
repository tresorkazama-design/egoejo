# 🚂 Comment accéder à Railway et voir les logs

## 🌐 Étape 1 : Ouvrir Railway dans votre navigateur

1. **Ouvrez votre navigateur** (Chrome, Edge, Firefox, etc.)

2. **Allez sur Railway** :
   - URL : `https://railway.app`
   - OU cliquez sur ce lien : https://railway.app

3. **Connectez-vous** (si vous n'êtes pas déjà connecté) :
   - Cliquez sur "Login"
   - Sélectionnez "Login with GitHub"
   - Autorisez Railway si demandé

---

## 📋 Étape 2 : Accéder à votre projet

1. **Dans le tableau de bord Railway**, vous verrez vos projets
2. **Trouvez votre projet** "fantastic-vibrancy" (ou le nom que vous avez donné)
3. **Cliquez sur le projet** pour l'ouvrir

---

## 📦 Étape 3 : Accéder à votre service "egoejo"

Une fois dans votre projet, dans la **sidebar de gauche**, vous verrez :
- **Postgres** (service PostgreSQL)
- **egoejo** (votre service backend)

1. **Cliquez sur "egoejo"** dans la liste à gauche
2. Cela vous amène à la page du service "egoejo"

---

## 📊 Étape 4 : Voir les déploiements et les logs

Une fois dans la page du service "egoejo", en haut vous verrez des **onglets** :

- **Deployments** ← Cliquez ici pour voir les logs !
- Variables
- Metrics
- Settings

1. **Cliquez sur l'onglet "Deployments"**
2. Vous verrez une liste de déploiements
3. **Cliquez sur le dernier déploiement** (celui le plus récent en haut)

---

## 📝 Étape 5 : Voir les logs du déploiement

Une fois dans le déploiement, vous verrez plusieurs **onglets** :

- **Details** : Informations sur le déploiement
- **Build Logs** : Logs du build (construction de l'image Docker)
- **Deploy Logs** ← Cliquez ici pour voir les erreurs au démarrage !

1. **Cliquez sur l'onglet "Deploy Logs"**
2. Vous verrez tous les logs de démarrage de votre application
3. **Cherchez les erreurs** (lignes en rouge ou messages d'erreur)

---

## ⚙️ Étape 6 : Voir les variables d'environnement

Si vous voulez vérifier les variables d'environnement :

1. **Revenez à la page du service "egoejo"** (cliquez sur "egoejo" dans la sidebar gauche)
2. **Cliquez sur l'onglet "Variables"** en haut
3. Vous verrez toutes les variables d'environnement configurées

---

## 🔍 Résumé des chemins dans Railway

```
railway.app
  └── Votre projet (fantastic-vibrancy)
      └── Service "egoejo"
          ├── Deployments ← Pour voir les logs
          │   └── Dernier déploiement
          │       └── Deploy Logs ← Pour voir les erreurs
          ├── Variables ← Pour configurer les variables d'environnement
          ├── Metrics
          └── Settings ← Pour configurer Root Directory, Dockerfile, etc.
```

---

## 🆘 Si vous ne trouvez pas votre projet

### Option 1 : Chercher dans la liste de projets
1. Sur la page d'accueil Railway (`https://railway.app/dashboard`)
2. Cherchez dans la liste de vos projets
3. Le nom peut être "fantastic-vibrancy" ou autre

### Option 2 : Utiliser la recherche
1. En haut de Railway, il y a une barre de recherche
2. Tapez "egoejo" ou "fantastic"
3. Sélectionnez votre projet dans les résultats

### Option 3 : Accéder directement via l'URL
1. L'URL devrait ressembler à : `https://railway.app/project/[id-du-projet]`
2. Vérifiez l'historique de navigation de votre navigateur

---

## 📸 Aide visuelle

Si vous êtes perdu, voici ce que vous devriez voir :

1. **Tableau de bord** : Liste de vos projets
2. **Page du projet** : Sidebar gauche avec vos services (Postgres, egoejo)
3. **Page du service** : Onglets en haut (Deployments, Variables, Metrics, Settings)
4. **Page des déploiements** : Liste des déploiements
5. **Page d'un déploiement** : Onglets (Details, Build Logs, Deploy Logs)

---

**🚀 Suivez ces étapes et dites-moi ce que vous voyez dans les "Deploy Logs" !**

