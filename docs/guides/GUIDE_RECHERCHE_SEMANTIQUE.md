# 🔍 Guide Recherche Sémantique (pgvector) - EGOEJO

**Date** : 2025-01-27  
**Objectif** : Préparer l'infrastructure pour recherche vectorielle sémantique

---

## 🎯 Objectif

Permettre la recherche sémantique (concepts, pas mots-clés) pour relier des contenus conceptuellement proches.

**Exemple** :
- Projet "Permaculture" → Embedding vectoriel
- Contenu "Rudolf Steiner" → Embedding vectoriel
- Similarité cosinus → Suggestion automatique

---

## 📦 Préparation (Actuelle)

### 1. Champs Embedding Créés

**Modèles modifiés** :
- ✅ `EducationalContent.embedding` (JSONField)
- ✅ `Projet.embedding` (JSONField)

**Migration** : `0011_add_embedding_fields.py`

### 2. Structure des Embeddings

Les embeddings seront des vecteurs de dimension 1536 (OpenAI) ou 384 (Sentence Transformers).

**Format JSON** :
```json
{
  "model": "text-embedding-3-small",
  "dimension": 1536,
  "vector": [0.123, -0.456, 0.789, ...]
}
```

---

## 🚀 Implémentation Future (Phase 2)

### Étape 1 : Installer pgvector

```bash
# Sur PostgreSQL (Railway ou local)
CREATE EXTENSION IF NOT EXISTS vector;
```

### Étape 2 : Migration vers VectorField

```python
# Migration future
from pgvector.django import VectorField

class Projet(models.Model):
    # ...
    embedding = VectorField(dimensions=1536, null=True, blank=True)
```

### Étape 3 : Génération d'Embeddings

**Option A : OpenAI API**
```python
import openai

def generate_embedding(text):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

**Option B : Sentence Transformers (local)**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text):
    return model.encode(text).tolist()
```

### Étape 4 : Recherche Sémantique

```python
from pgvector.django import L2Distance

def semantic_search(query, limit=10):
    # Générer embedding de la requête
    query_embedding = generate_embedding(query)
    
    # Recherche par similarité cosinus
    results = Projet.objects.annotate(
        distance=L2Distance('embedding', query_embedding)
    ).order_by('distance')[:limit]
    
    return results
```

---

## 📋 Cas d'Usage

### 1. Suggestions de Contenus Liés

```python
def get_related_contents(projet):
    # Trouver des contenus conceptuellement proches
    related = EducationalContent.objects.annotate(
        similarity=1 - L2Distance('embedding', projet.embedding)
    ).filter(
        similarity__gt=0.7  # Seuil de similarité
    ).order_by('-similarity')[:5]
    
    return related
```

### 2. Recherche Sémantique Avancée

```python
def semantic_search_projects(query):
    query_embedding = generate_embedding(query)
    
    # Combiner recherche textuelle (pg_trgm) et sémantique
    text_results = Projet.objects.search(query)  # pg_trgm
    semantic_results = Projet.objects.annotate(
        similarity=1 - L2Distance('embedding', query_embedding)
    ).filter(similarity__gt=0.6)
    
    # Fusionner les résultats
    return (text_results | semantic_results).distinct()
```

### 3. Constellation des Savoirs

Visualiser les liens sémantiques entre :
- Projets
- Contenus éducatifs
- Concepts (Steiner, Biodynamie, Permaculture)

---

## 🔧 Configuration Future

### Variables d'Environnement

```env
# Option A : OpenAI
OPENAI_API_KEY=...

# Option B : Sentence Transformers (local)
# Aucune clé nécessaire
```

### Dépendances Futures

```txt
# requirements.txt (futur)
pgvector>=0.2.0  # Extension PostgreSQL
openai>=1.0.0  # Ou sentence-transformers>=2.2.0
```

---

## 📊 Métriques de Succès

- **Précision suggestions** : > 80%
- **Temps recherche** : < 300ms
- **Couverture sémantique** : Tous les projets et contenus ont un embedding

---

## 🎯 Roadmap

### Phase 1 : Préparation (Actuelle) ✅
- [x] Champs embedding créés
- [x] Migration préparée

### Phase 2 : Infrastructure (Futur)
- [ ] Installer pgvector
- [ ] Migrer vers VectorField
- [ ] Configurer génération embeddings

### Phase 3 : Génération (Futur)
- [ ] Task Celery pour générer embeddings
- [ ] Génération automatique à la création
- [ ] Batch processing pour contenus existants

### Phase 4 : Recherche (Futur)
- [ ] Endpoint recherche sémantique
- [ ] Suggestions automatiques
- [ ] Visualisation constellation

---

**Dernière mise à jour** : 2025-01-27  
**Statut** : 📋 Infrastructure préparée, implémentation future

