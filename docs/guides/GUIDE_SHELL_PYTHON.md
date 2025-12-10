# 📖 Guide : Shell Python vs PowerShell

## ⚠️ Différence Importante

### Shell Python (`python manage.py shell`)
- **Pour** : Tester du code Python, importer des modules Django
- **Commandes** : Code Python uniquement
- **Exemple** : `from core.security.encryption import encrypt_sensitive_data`

### PowerShell (Terminal normal)
- **Pour** : Exécuter des commandes système, lancer des scripts
- **Commandes** : Commandes PowerShell/Windows
- **Exemple** : `python manage.py runserver`, `cd backend`

## 🔧 Comment Utiliser

### 1. Dans le Shell Python (après `python manage.py shell`)

```python
# ✅ CORRECT - Pas d'indentation au début
from core.security.encryption import encrypt_sensitive_data
from core.security.sanitization import sanitize_string

# Tester le chiffrement
encrypted = encrypt_sensitive_data("test")
print(encrypted)

# Tester la sanitization
cleaned = sanitize_string("<script>alert('XSS')</script>")
print(cleaned)

# Quitter le shell Python
exit()
```

### 2. Dans PowerShell (terminal normal)

```powershell
# Naviguer vers le backend
cd C:\Users\treso\Downloads\egoejo\backend

# Démarrer le serveur
python manage.py runserver

# Exécuter le script de test
python TEST_SECURITE.py

# Ouvrir le shell Python
python manage.py shell
```

## 🚨 Erreurs Courantes

### ❌ FAUX - Commandes PowerShell dans le shell Python
```python
>>> cd C:\Users\treso\Downloads\egoejo\backend
# ❌ Erreur : IndentationError
```

### ✅ CORRECT - Utiliser exit() puis PowerShell
```python
>>> exit()  # Quitter le shell Python
```
Puis dans PowerShell :
```powershell
cd C:\Users\treso\Downloads\egoejo\backend
python manage.py runserver
```

## 📝 Script de Test Automatique

Pour éviter les confusions, utilisez le script de test :

```powershell
cd C:\Users\treso\Downloads\egoejo\backend
python TEST_SECURITE.py
```

Ce script teste automatiquement tous les modules de sécurité sans avoir à utiliser le shell Python interactif.

## 🎯 Résumé

| Action | Où l'exécuter | Commande |
|--------|---------------|----------|
| Tester les modules | PowerShell | `python TEST_SECURITE.py` |
| Démarrer le serveur | PowerShell | `python manage.py runserver` |
| Tester du code Python | Shell Python | `from module import fonction` |
| Naviguer dans les dossiers | PowerShell | `cd chemin` |
| Quitter le shell Python | Shell Python | `exit()` |

---

**💡 Astuce** : Si vous êtes dans le shell Python et que vous voulez revenir à PowerShell, tapez simplement `exit()` puis appuyez sur Entrée.

