# 🔧 Fix: Incompatibilité Django 4.2 / Python 3.14

**Date** : 2025-01-27  
**Erreur** : `AttributeError: 'super' object has no attribute 'dicts'`  
**Cause** : Django 4.2.26 n'est pas compatible avec Python 3.14.0

---

## 🐛 Problème

L'erreur se produit lors de l'accès à `/admin/core/projet/add/` :

```
AttributeError: 'super' object has no attribute 'dicts' and no __dict__ for setting new attributes
Exception Location: django/template/context.py, line 39, in __copy__
```

**Cause** : Django 4.2.26 n'a pas été testé avec Python 3.14.0 (qui n'est pas encore officiellement sorti). Django 4.2 supporte Python 3.8-3.12.

---

## ✅ Solution

### Option 1 : Upgrader Django vers 5.0+ (Recommandé)

Django 5.0+ supporte mieux Python 3.13+ et devrait fonctionner avec Python 3.14.

**Changements dans `requirements.txt`** :
```txt
Django>=5.0,<6.0
djangorestframework>=3.15.0
```

**Commandes** :
```bash
cd backend
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install --upgrade Django>=5.0 djangorestframework>=3.15.0
pip install -r requirements.txt
```

### Option 2 : Downgrader Python vers 3.12 ou 3.13

Si vous préférez rester sur Django 4.2 :

1. Installer Python 3.12 ou 3.13
2. Créer un nouveau virtualenv avec cette version
3. Réinstaller les dépendances

---

## 🔄 Migration Django 4.2 → 5.0

### Changements Majeurs

1. **Python 3.10+ requis** (vous avez 3.14, donc OK ✅)
2. **`USE_TZ = True` par défaut** (déjà dans settings.py probablement)
3. **Changements dans les modèles** :
   - `on_delete` est maintenant obligatoire pour ForeignKey
   - Certaines méthodes dépréciées ont été supprimées

### Vérifications à Faire

1. **Vérifier les ForeignKey** :
   ```python
   # Avant (Django 4.2)
   projet = models.ForeignKey("Projet")
   
   # Après (Django 5.0) - doit avoir on_delete
   projet = models.ForeignKey("Projet", on_delete=models.CASCADE)
   ```

2. **Vérifier les migrations** :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Tester l'admin** :
   ```bash
   python manage.py runserver
   # Accéder à http://127.0.0.1:8000/admin/core/projet/add/
   ```

---

## 📝 Checklist

- [x] Requirements.txt mis à jour
- [ ] Installer Django 5.0+
- [ ] Vérifier les ForeignKey (on_delete)
- [ ] Lancer les migrations
- [ ] Tester l'admin
- [ ] Tester les API

---

## 🚀 Commandes Rapides

```bash
# 1. Activer le virtualenv
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Upgrader Django
pip install --upgrade "Django>=5.0,<6.0" "djangorestframework>=3.15.0"

# 3. Installer toutes les dépendances
pip install -r requirements.txt

# 4. Vérifier les migrations
python manage.py makemigrations
python manage.py migrate

# 5. Tester
python manage.py runserver
```

---

## ⚠️ Notes

- Django 5.0 est stable et recommandé pour Python 3.14
- Les changements sont généralement rétrocompatibles
- Si des erreurs apparaissent, vérifier la [documentation de migration Django 5.0](https://docs.djangoproject.com/en/5.0/releases/5.0/)

---

## 🔍 Si le Problème Persiste

1. Vérifier la version de Python :
   ```bash
   python --version
   ```

2. Vérifier la version de Django :
   ```bash
   python -c "import django; print(django.get_version())"
   ```

3. Vérifier les logs Django pour plus de détails

4. Considérer un downgrade vers Python 3.12 si nécessaire

