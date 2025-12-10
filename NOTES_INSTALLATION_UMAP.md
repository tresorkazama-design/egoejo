# ⚠️ Notes Installation UMAP

**Date** : 2025-01-27  
**Problème** : `umap-learn` ne supporte pas Python 3.14+ (seulement <3.14)

---

## 🔍 Problème

L'installation de `umap-learn` échoue sur Python 3.14 avec l'erreur :
```
RuntimeError: Cannot install on Python version 3.14.0; only versions >=3.10,<3.14 are supported.
```

---

## ✅ Solutions

### Solution 1 : Utiliser uniquement t-SNE (Recommandé)

**Avantage** : `scikit-learn` (qui contient t-SNE) supporte Python 3.14.

**Modification** : La tâche `reduce_embeddings_to_3d` utilise automatiquement t-SNE si UMAP n'est pas disponible.

**Code** : Déjà implémenté dans `backend/core/tasks_mycelium.py` avec fallback automatique.

**Utilisation** :
```python
# Forcer t-SNE
reduce_embeddings_to_3d.delay('both', 'tsne')
```

---

### Solution 2 : Utiliser un environnement Python 3.11 ou 3.12

**Pour développement local** :
```bash
# Créer un environnement virtuel avec Python 3.12
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\Activate.ps1  # Windows

# Installer les dépendances
pip install umap-learn scikit-learn
```

**Pour production (Railway)** :
- Railway utilise généralement Python 3.11 par défaut
- UMAP devrait fonctionner correctement

---

### Solution 3 : Attendre une mise à jour de umap-learn

Le package `umap-learn` pourrait être mis à jour pour supporter Python 3.14+ dans le futur.

---

## 📝 Recommandation

**Pour l'instant** : Utiliser **t-SNE uniquement** (`method='tsne'`).

**Avantages t-SNE** :
- ✅ Supporte Python 3.14
- ✅ Déjà installé (`scikit-learn`)
- ✅ Bonne qualité de visualisation
- ✅ Fonctionne immédiatement

**Inconvénients t-SNE** :
- ⚠️ Plus lent que UMAP sur grands datasets
- ⚠️ Peut perdre certaines structures globales

**Pour la plupart des cas d'usage EGOEJO** : t-SNE est suffisant.

---

## 🔧 Code Modifié

Le code dans `backend/core/tasks_mycelium.py` gère automatiquement le fallback :

```python
def _reduce_with_umap(content_type):
    try:
        import umap
        # ... code UMAP ...
    except ImportError:
        logger.warning("umap-learn non installé, fallback sur t-SNE")
        return _reduce_with_tsne(content_type)
```

**Résultat** : Si UMAP n'est pas disponible, t-SNE est utilisé automatiquement.

---

**Dernière mise à jour** : 2025-01-27

