# 🔄 Guide de Redémarrage Backend - EGOEJO

**Problème** : Erreur 500 sur `/api/auth/login/`  
**Cause** : Le serveur backend doit être redémarré après les modifications

---

## 🔧 Solution : Redémarrer le Backend

### Étape 1 : Arrêter le serveur actuel

Dans le terminal où le backend tourne :
- Appuyez sur `Ctrl+C` pour arrêter le serveur

### Étape 2 : Redémarrer le serveur

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source venv/bin/activate  # Linux/Mac

python manage.py runserver
```

---

## ✅ Vérification

Après redémarrage, vérifiez que le backend fonctionne :

1. **Health Check** :
   ```bash
   curl http://localhost:8000/api/health/
   ```
   Devrait retourner : `{"status": "ok", ...}`

2. **API Root** :
   ```bash
   curl http://localhost:8000/api/
   ```
   Devrait retourner la liste des endpoints

3. **Test Login** :
   - Ouvrez http://localhost:5173/login
   - L'erreur "Failed to fetch" devrait disparaître

---

## 🔍 Si l'erreur persiste

### Vérifier les logs du backend

Dans le terminal où le backend tourne, vous devriez voir les erreurs détaillées.

### Vérifier la base de données

```bash
cd backend
python manage.py migrate
python manage.py check
```

### Vérifier les variables d'environnement

Assurez-vous que `.env` contient :
- `DJANGO_SECRET_KEY` (au moins 50 caractères)
- `DEBUG=1` (pour le développement)
- `ALLOWED_HOSTS=localhost,127.0.0.1` (optionnel en dev)

---

## 💡 Note

**Le backend doit être redémarré après chaque modification de `settings.py` ou des fichiers de configuration.**

---

**Après redémarrage, l'erreur 500 devrait être résolue !** ✅

