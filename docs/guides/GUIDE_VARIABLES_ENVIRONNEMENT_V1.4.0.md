# 🔧 Guide Configuration Variables d'Environnement v1.4.0

**Date** : 2025-01-27  
**Objectif** : Configurer les nouvelles variables pour Intelligence Sémantique et Sécurité

---

## 📋 Variables Requises

### Backend (.env)

#### Intelligence Sémantique (Embeddings)

```env
# Option A : OpenAI (recommandé pour production)
OPENAI_API_KEY=sk-...

# Option B : Sentence Transformers (local, pas de clé nécessaire)
# Aucune variable requise
```

**Note** : Si `OPENAI_API_KEY` n'est pas configuré, le système utilisera Sentence Transformers par défaut.

#### Sécurité (Scan Anti-Virus)

```env
# ClamAV (optionnel, fallback sûr si non configuré)
CLAMAV_HOST=localhost
CLAMAV_PORT=3310

# Ou pour socket Unix (Linux/Mac)
# CLAMAV_SOCKET=/var/run/clamav/clamd.ctl
```

**Note** : Si ClamAV n'est pas disponible, les fichiers sont considérés comme sûrs (pas de blocage).

#### Celery (Déjà configuré)

```env
# Redis pour Celery (déjà requis pour Channels)
REDIS_URL=redis://localhost:6379/0
```

---

## 🚀 Configuration par Environnement

### Développement Local

```env
# .env.local
OPENAI_API_KEY=sk-test-...  # Optionnel
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
REDIS_URL=redis://localhost:6379/0
```

### Production (Railway)

**Variables à configurer dans Railway** :
- `OPENAI_API_KEY` (optionnel, recommandé)
- `CLAMAV_HOST` (optionnel, si ClamAV déployé)
- `CLAMAV_PORT` (optionnel)
- `REDIS_URL` (déjà requis)

---

## ✅ Vérification

### Tester OpenAI

```python
# Dans Django shell
import os
api_key = os.environ.get('OPENAI_API_KEY')
print(f"OpenAI configuré: {bool(api_key)}")
```

### Tester ClamAV

```python
# Dans Django shell
from core.tasks_security import scan_file_antivirus
result = scan_file_antivirus('test.txt')
print(result)
```

---

## 📚 Références

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [ClamAV Installation](https://www.clamav.net/documents/installing-clamav)
- [Sentence Transformers](https://www.sbert.net/)

---

**Dernière mise à jour** : 2025-01-27

