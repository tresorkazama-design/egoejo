# 🔧 Guide de Troubleshooting - EGOEJO

Guide pour résoudre les problèmes courants.

---

## 🐛 Problèmes Frontend

### Erreur : "Cannot find module"

**Cause** : Dépendances non installées ou corrompues

**Solution** :
```bash
cd frontend/frontend
rm -rf node_modules package-lock.json
npm install
```

### Erreur : "Port already in use"

**Cause** : Le port 5173 est déjà utilisé

**Solution** :
```bash
# Trouver le processus
lsof -ti:5173
# Tuer le processus
kill -9 <PID>
# Ou utiliser un autre port
npm run dev -- --port 5174
```

### Erreur : "Failed to fetch" (API)

**Cause** : Backend non démarré ou CORS mal configuré

**Solution** :
1. Vérifier que le backend tourne : `curl http://localhost:8000/api/`
2. Vérifier `VITE_API_URL` dans `.env`
3. Vérifier la configuration CORS dans `backend/config/settings.py`

---

## 🐛 Problèmes Backend

### Erreur : "ModuleNotFoundError"

**Cause** : Dépendances Python non installées

**Solution** :
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Erreur : "Database connection failed"

**Cause** : Base de données non accessible

**Solution** :
1. Vérifier `DATABASE_URL` ou `DB_*` dans `.env`
2. Vérifier que PostgreSQL tourne
3. Vérifier les credentials

### Erreur : "Migration conflicts"

**Cause** : Migrations en conflit

**Solution** :
```bash
python manage.py makemigrations
python manage.py migrate
```

### Erreur : "Static files not found"

**Cause** : Fichiers statiques non collectés

**Solution** :
```bash
python manage.py collectstatic --noinput
```

---

## 🔐 Problèmes de Sécurité

### Erreur : "CSRF token missing"

**Cause** : Token CSRF manquant ou invalide

**Solution** :
1. Vérifier que les cookies sont activés
2. Vérifier `CSRF_TRUSTED_ORIGINS`
3. Vérifier les headers de requête

### Erreur : "CORS policy"

**Cause** : Origine non autorisée

**Solution** :
1. Vérifier `CORS_ALLOWED_ORIGINS`
2. Ajouter l'origine frontend
3. Redémarrer le serveur

---

## ⚡ Problèmes de Performance

### Lenteur générale

**Diagnostic** :
1. Vérifier les requêtes DB avec `django-debug-toolbar`
2. Vérifier le cache Redis
3. Vérifier les logs pour les erreurs

**Solutions** :
- Optimiser les requêtes avec `select_related()`
- Activer le cache Redis
- Réduire le nombre de requêtes

### Images lentes à charger

**Solution** :
- Utiliser `OptimizedImage` avec lazy loading
- Optimiser les images (WebP, compression)
- Utiliser un CDN

---

## 🔌 Problèmes WebSocket

### Connexion échoue

**Cause** : Redis non disponible ou token invalide

**Solution** :
1. Vérifier `REDIS_URL`
2. Vérifier que le token JWT est valide
3. Vérifier les logs du serveur

### Messages non reçus

**Cause** : Consumer mal configuré

**Solution** :
1. Vérifier `consumers.py`
2. Vérifier la configuration Channels
3. Vérifier les logs WebSocket

---

## 📊 Problèmes de Tests

### Tests échouent

**Diagnostic** :
```bash
# Frontend
npm test -- --run --reporter=verbose

# Backend
pytest -v
```

**Solutions courantes** :
- Vérifier les mocks
- Vérifier les variables d'environnement de test
- Vérifier que les dépendances sont installées

---

## 🆘 Obtenir de l'Aide

1. **Vérifier les logs** :
   - Frontend : Console du navigateur
   - Backend : `python manage.py runserver` (dev) ou logs Railway

2. **Vérifier la documentation** :
   - `README.md`
   - `ARCHITECTURE_FRONTEND_BACKEND.md`
   - `CONTRIBUTING.md`

3. **Créer une issue** sur GitHub avec :
   - Description du problème
   - Étapes pour reproduire
   - Logs d'erreur
   - Environnement

---

**La plupart des problèmes peuvent être résolus en suivant ce guide !** 🔧

