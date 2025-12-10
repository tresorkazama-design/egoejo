# 🔒 Commandes pour la Sécurité Renforcée

## 📍 Navigation vers les répertoires

### Backend
```powershell
cd C:\Users\treso\Downloads\egoejo\backend
```

### Frontend
```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
```

## 🔧 Installation des Dépendances

### Backend (Déjà fait ✅)
```powershell
cd C:\Users\treso\Downloads\egoejo\backend
pip install -r requirements.txt
```

**✅ Dépendances installées avec succès !**
- `cryptography>=41.0.0` ✅ (déjà installé)
- Toutes les autres dépendances ✅

### Frontend
```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
npm install
```

## 🧪 Tests de Sécurité

### Backend
```powershell
cd C:\Users\treso\Downloads\egoejo\backend
python manage.py test core.security
```

### Frontend
```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
npm test -- security
```

## 🚀 Démarrage du Backend

```powershell
cd C:\Users\treso\Downloads\egoejo\backend

# Activer l'environnement virtuel (si présent)
if (Test-Path venv\Scripts\Activate.ps1) {
    .\venv\Scripts\Activate.ps1
}

# Démarrer le serveur
python manage.py runserver
```

## 🔐 Configuration Optionnelle

### Variable d'Environnement pour le Chiffrement

Si vous voulez utiliser une clé de chiffrement personnalisée (optionnel) :

```powershell
# Dans Railway ou votre fichier .env
ENCRYPTION_KEY=votre-cle-de-chiffrement-ici
```

**Note** : Si `ENCRYPTION_KEY` n'est pas définie, une clé sera automatiquement générée depuis `SECRET_KEY`.

## 📋 Vérification

### Vérifier que les modules de sécurité sont bien importés

```powershell
cd C:\Users\treso\Downloads\egoejo\backend
python manage.py shell
```

Puis dans le shell Python :
```python
# Tester l'import des modules de sécurité
from core.security.encryption import encrypt_sensitive_data
from core.security.sanitization import sanitize_string
from core.security.middleware import SecurityHeadersMiddleware

# Tester le chiffrement
encrypted = encrypt_sensitive_data("test")
print("✅ Chiffrement fonctionne")

# Tester la sanitization
cleaned = sanitize_string("<script>alert('XSS')</script>")
print(f"✅ Sanitization fonctionne: {cleaned}")
```

## 🎯 Endpoints de Sécurité Disponibles

Une fois le serveur démarré :

- `GET /api/security/audit/` - Audit de sécurité (admin uniquement)
- `GET /api/security/metrics/` - Métriques de sécurité (admin uniquement)
- `GET /api/user/data-export/` - Export des données (utilisateur authentifié)
- `DELETE /api/user/data-delete/` - Suppression des données (utilisateur authentifié)

## ✅ Checklist

- [x] Dépendances backend installées
- [ ] Dépendances frontend installées (`npm install`)
- [ ] Tests de sécurité passent
- [ ] Serveur backend démarre sans erreur
- [ ] Modules de sécurité importables

---

**💡 Astuce** : Pour éviter de retaper le chemin complet, vous pouvez créer un alias PowerShell :

```powershell
# Ajouter au profil PowerShell
function cd-egoejo {
    cd C:\Users\treso\Downloads\egoejo
}
function cd-backend {
    cd C:\Users\treso\Downloads\egoejo\backend
}
function cd-frontend {
    cd C:\Users\treso\Downloads\egoejo\frontend\frontend
}
```

Puis utilisez simplement :
```powershell
cd-backend
cd-frontend
```

