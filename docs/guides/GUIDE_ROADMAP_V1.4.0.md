# 🚀 Roadmap v1.4.0 - EGOEJO

**Date** : 2025-01-27  
**Objectif** : Intelligence Sémantique, Gouvernance Décentralisée, Sécurité & Qualité

---

## 📊 Points de Vigilance Adressés

### 1. Mix React / TypeScript
- ✅ ESLint configuré pour interdire nouveaux `.jsx`
- ✅ TypeScript Strict Mode configuré
- ✅ Migration progressive documentée

### 2. Complexité Déploiement
- ✅ Monitoring Flower + Sentry
- ✅ Health checks à implémenter
- ✅ Logs structurés recommandés

---

## 🎯 Axe 1 : Intelligence Sémantique (RAG Léger)

### Objectif
Créer des liens de sens entre "Philosophie" et "Projets" via embeddings vectoriels.

### Implémentation

#### 1. Installation pgvector

```bash
# Sur PostgreSQL (Railway ou local)
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. Tâches Celery Créées

**Fichier** : `backend/core/tasks_embeddings.py`

**Tâches disponibles** :
- `generate_embedding_task` : Génère embedding pour un contenu
- `batch_generate_embeddings` : Génère embeddings pour tous les contenus

**Modèles supportés** :
- OpenAI (`text-embedding-3-small`)
- Sentence Transformers (`all-MiniLM-L6-v2`) - local

#### 3. Utilisation

```python
from core.tasks_embeddings import generate_embedding_task

# Générer embedding après création
generate_embedding_task.delay('sentence-transformers', projet.id, 'projet')
```

#### 4. Prochaines Étapes

- [ ] Migration vers VectorField (pgvector)
- [ ] Endpoint recherche sémantique
- [ ] UI suggestions automatiques

---

## 🗳️ Axe 2 : Gouvernance Décentralisée (Vote Quadratique)

### Objectif
Mesurer l'intensité d'une préférence, pas juste la direction.

### Implémentation

#### 1. Migration Créée

**Fichier** : `backend/core/migrations/0012_add_voting_method_to_poll.py`

**Champs ajoutés** :
- `Poll.voting_method` : 'binary', 'quadratic', 'majority'
- `Poll.max_points` : Points max (Vote Quadratique)
- `PollBallot.points` : Points attribués
- `PollBallot.ranking` : Classement (Jugement Majoritaire)

#### 2. Modèle Poll à Modifier

Ajouter les champs dans `backend/core/models/polls.py` :

```python
class Poll(models.Model):
    VOTING_METHOD_CHOICES = [
        ('binary', 'Binaire (Oui/Non)'),
        ('quadratic', 'Vote Quadratique'),
        ('majority', 'Jugement Majoritaire'),
    ]
    
    voting_method = models.CharField(
        max_length=20,
        choices=VOTING_METHOD_CHOICES,
        default='binary'
    )
    max_points = models.IntegerField(default=100, null=True, blank=True)
```

#### 3. Frontend à Adapter

- Interface distribution points (Vote Quadratique)
- Interface classement (Jugement Majoritaire)
- Calcul résultats avancés

#### 4. Prochaines Étapes

- [ ] Appliquer migration
- [ ] Modifier modèle Poll
- [ ] Adapter API endpoints
- [ ] Créer UI vote avancé

---

## 🔒 Axe 3 : Sécurité & Qualité Code

### Objectif
TypeScript Strict + Scan Anti-Virus

### Implémentation

#### 1. ESLint Configuration

**Fichier** : `frontend/frontend/.eslintrc.cjs`

**Règles** :
- Interdit nouveaux fichiers `.jsx`
- Force `.tsx` pour nouvelles features
- Ignore temporairement `.jsx` existants (migration progressive)

#### 2. TypeScript Strict Mode

**Fichier** : `frontend/frontend/tsconfig.json`

**Options strictes** :
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noUncheckedIndexedAccess: true`

#### 3. Scan Anti-Virus

**Fichier** : `backend/core/tasks_security.py`

**Tâches disponibles** :
- `scan_file_antivirus` : Scan ClamAV
- `validate_file_type` : Validation type MIME

**Utilisation** :
```python
from core.tasks_security import scan_file_antivirus

# Scanner après upload
scan_file_antivirus.delay(file_path)
```

#### 4. Dépendances Ajoutées

- `pyclamd>=1.0.0` : Scan ClamAV
- `python-magic>=0.4.27` : Validation MIME

#### 5. Configuration ClamAV

**Variables d'environnement** :
```env
CLAMAV_HOST=localhost  # Optionnel
CLAMAV_PORT=3310       # Optionnel
```

**Note** : ClamAV optionnel (fallback sûr si non disponible)

---

## 📋 Checklist Implémentation

### Phase 1 : Intelligence Sémantique
- [x] Tâches Celery embeddings créées
- [ ] Installer pgvector
- [ ] Migration VectorField
- [ ] Endpoint recherche sémantique
- [ ] UI suggestions

### Phase 2 : Vote Quadratique
- [x] Migration créée
- [ ] Modifier modèle Poll
- [ ] Adapter API
- [ ] Créer UI vote

### Phase 3 : Sécurité & Qualité
- [x] ESLint configuré
- [x] TypeScript Strict configuré
- [x] Tâches sécurité créées
- [ ] Intégrer scan dans uploads
- [ ] Tests sécurité

---

## 🚀 Prochaines Actions

1. **Immédiat** :
   - Appliquer migration `0012_add_voting_method_to_poll`
   - Modifier modèle Poll avec nouveaux champs
   - Tester tâches embeddings

2. **Court terme** :
   - Installer pgvector
   - Créer endpoint recherche sémantique
   - Intégrer scan antivirus dans uploads

3. **Moyen terme** :
   - UI vote quadratique
   - Suggestions sémantiques dans frontend
   - Migration progressive TypeScript

---

**Dernière mise à jour** : 2025-01-27  
**Statut** : 📋 Infrastructure préparée, implémentation en cours

