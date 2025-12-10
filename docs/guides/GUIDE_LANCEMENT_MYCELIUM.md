# 🍄 Guide Lancement Réduction Dimensionnalité (Mycélium)

**Date** : 2025-01-27  
**Version** : 1.5.0

---

## 🎯 Objectif

Lancer la réduction de dimensionnalité pour transformer les embeddings haute dimension en coordonnées 3D (x, y, z) pour la visualisation "Mycélium Numérique".

---

## 📋 Prérequis

1. ✅ **Dépendances installées** : `umap-learn` et `scikit-learn`
2. ✅ **Embeddings générés** : Les projets et contenus doivent avoir des embeddings
3. ✅ **Celery en cours d'exécution** : Pour traiter les tâches asynchrones

---

## 🚀 Méthode 1 : Via l'API (Recommandé)

### Endpoint Admin

**POST** `/api/mycelium/reduce/`

**Headers** :
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Body** :
```json
{
  "content_type": "both",  // "projet", "educational_content", ou "both"
  "method": "umap"         // "umap" ou "tsne"
}
```

**Exemple avec curl** :
```bash
curl -X POST https://egoejo-production.up.railway.app/api/mycelium/reduce/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "both", "method": "umap"}'
```

**Réponse** :
```json
{
  "success": true,
  "task_id": "abc123...",
  "content_type": "both",
  "method": "umap"
}
```

---

## 🐍 Méthode 2 : Via Script Python (Recommandé)

### Script automatique

```bash
cd backend
python scripts/launch_mycelium_reduction.py --method tsne --type both
```

**Options** :
- `--method tsne|umap` : Méthode de réduction (default: tsne)
- `--type both|projet|educational_content` : Type de contenu (default: both)
- `--sync` : Exécution synchrone (bloquante) au lieu d'asynchrone

**Exemples** :
```bash
# Réduction avec t-SNE (recommandé pour Python 3.14+)
python scripts/launch_mycelium_reduction.py --method tsne

# Réduction avec UMAP (si disponible)
python scripts/launch_mycelium_reduction.py --method umap

# Uniquement les projets
python scripts/launch_mycelium_reduction.py --type projet

# Exécution synchrone (pour test)
python scripts/launch_mycelium_reduction.py --method tsne --sync
```

---

## 🐍 Méthode 3 : Via Django Shell

### Commande

```bash
cd backend
python manage.py shell
```

### Code Python

```python
from core.tasks_mycelium import reduce_embeddings_to_3d

# Lancer la tâche (asynchrone)
result = reduce_embeddings_to_3d.delay('both', 'tsne')

# Vérifier le statut
print(f"Task ID: {result.id}")
print(f"Status: {result.status}")

# Attendre le résultat (optionnel, peut prendre du temps)
# result.get(timeout=300)  # 5 minutes timeout
```

### Alternative : Exécution synchrone (pour test)

```python
from core.tasks_mycelium import reduce_embeddings_to_3d

# Exécution synchrone (bloquante)
result = reduce_embeddings_to_3d('both', 'tsne')
print(result)
```

---

## 🔍 Vérification

### 1. Vérifier les coordonnées 3D

```python
from core.models.projects import Projet
from core.models.content import EducationalContent

# Vérifier un projet
projet = Projet.objects.filter(embedding__isnull=False).first()
if projet and projet.embedding:
    coords = projet.embedding.get('coordinates_3d')
    if coords:
        print(f"Projet {projet.titre}: x={coords['x']}, y={coords['y']}, z={coords['z']}")

# Vérifier un contenu
contenu = EducationalContent.objects.filter(embedding__isnull=False).first()
if contenu and contenu.embedding:
    coords = contenu.embedding.get('coordinates_3d')
    if coords:
        print(f"Contenu {contenu.title}: x={coords['x']}, y={coords['y']}, z={coords['z']}")
```

### 2. Vérifier via l'API

**GET** `/api/mycelium/data/`

**Réponse** :
```json
{
  "projets": [
    {
      "id": 1,
      "titre": "Potager Partagé",
      "x": 0.5,
      "y": -0.3,
      "z": 0.8,
      "url": "/projets/1"
    }
  ],
  "contenus": [
    {
      "id": 1,
      "title": "Cours aux Agriculteurs",
      "x": 0.4,
      "y": -0.2,
      "z": 0.7,
      "url": "/contenus/cours-aux-agriculteurs"
    }
  ]
}
```

---

## ⚙️ Paramètres

### `content_type`

- `"projet"` : Uniquement les projets
- `"educational_content"` : Uniquement les contenus éducatifs
- `"both"` : Projets et contenus (recommandé)

### `method`

- `"umap"` : UMAP (Uniform Manifold Approximation and Projection)
  - **Avantages** : Plus rapide, préserve mieux les structures globales
  - **Recommandé** pour la plupart des cas
  
- `"tsne"` : t-SNE (t-Distributed Stochastic Neighbor Embedding)
  - **Avantages** : Meilleure séparation des clusters
  - **Inconvénients** : Plus lent, peut perdre les structures globales

**Recommandation** : Utiliser `"umap"` par défaut.

---

## ⏱️ Temps d'Exécution

- **Petit dataset** (< 100 éléments) : ~10-30 secondes
- **Dataset moyen** (100-500 éléments) : ~1-3 minutes
- **Grand dataset** (> 500 éléments) : ~5-15 minutes

**Note** : L'exécution est asynchrone via Celery, vous pouvez continuer à utiliser l'application pendant le traitement.

---

## 🐛 Dépannage

### Erreur : "Aucun embedding trouvé"

**Cause** : Aucun projet ou contenu n'a d'embedding généré.

**Solution** :
1. Générer les embeddings d'abord (via `generate_embedding_task`)
2. Vérifier que les embeddings sont bien stockés dans la base de données

### Erreur : "umap-learn non installé"

**Cause** : La dépendance n'est pas installée.

**Solution** :
```bash
pip install umap-learn scikit-learn
```

### Erreur : "scikit-learn non installé"

**Cause** : La dépendance n'est pas installée.

**Solution** :
```bash
pip install scikit-learn
```

### La tâche reste en "PENDING"

**Cause** : Celery n'est pas en cours d'exécution.

**Solution** :
1. Démarrer Celery : `celery -A config worker -l info`
2. Vérifier que Redis est accessible

---

## 📊 Monitoring

### Via Flower (si configuré)

Accéder à `http://localhost:5555` pour voir les tâches en cours.

### Via Logs Celery

```bash
celery -A config worker -l info
```

Les logs afficheront :
```
[INFO] Réduction UMAP réussie pour 150 éléments
```

---

**Dernière mise à jour** : 2025-01-27

