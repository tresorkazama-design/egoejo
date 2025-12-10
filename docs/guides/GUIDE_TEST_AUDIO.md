# 🎙️ Guide Test Génération Audio (TTS)

**Date** : 2025-01-27  
**Version** : 1.5.0

---

## 🎯 Objectif

Tester la génération automatique de fichiers audio (TTS) pour les contenus éducatifs.

---

## 📋 Prérequis

1. ✅ **Variables d'environnement configurées** :
   - `OPENAI_API_KEY` (ou `ELEVENLABS_API_KEY`)
   - `TTS_PROVIDER` (openai ou elevenlabs)
   - `TTS_VOICE` (alloy, echo, etc.)

2. ✅ **Celery en cours d'exécution** (pour traitement asynchrone)

3. ✅ **Contenu éducatif publié** dans la base de données

---

## 🚀 Méthode 1 : Via Script Python (Recommandé)

### Script automatique

```bash
cd backend
python scripts/test_audio_generation.py
```

**Options** :
- `--content-id ID` : ID spécifique du contenu (sinon utilise le premier publié)
- `--provider openai|elevenlabs` : Provider TTS (défaut: depuis env)
- `--voice VOICE` : Voix à utiliser (défaut: depuis env)
- `--sync` : Exécution synchrone (bloquante) au lieu d'asynchrone

**Exemples** :
```bash
# Test avec contenu spécifique
python scripts/test_audio_generation.py --content-id 1

# Test avec provider spécifique
python scripts/test_audio_generation.py --provider openai --voice nova

# Test synchrone (pour debug)
python scripts/test_audio_generation.py --sync
```

---

## 🐍 Méthode 2 : Via Django Shell

### Commande

```bash
cd backend
python manage.py shell
```

### Code Python

```python
from core.models.content import EducationalContent
from core.tasks_audio import generate_audio_content

# Récupérer un contenu publié
content = EducationalContent.objects.filter(status='published').first()

# Lancer la génération audio (asynchrone)
task = generate_audio_content.delay(content.id, 'openai', 'alloy')
print(f"Task ID: {task.id}")

# Attendre le résultat (optionnel)
# result = task.get(timeout=120)  # 2 minutes timeout
```

### Vérifier le résultat

```python
# Rafraîchir le contenu
content.refresh_from_db()

if content.audio_file:
    print(f"✅ Audio généré: {content.audio_file}")
else:
    print("❌ Aucun audio généré")
```

---

## 🔄 Méthode 3 : Via Publication de Contenu

### Automatique lors de la publication

La génération audio est **automatique** lors de la publication d'un contenu via l'endpoint :

**POST** `/api/contents/<id>/publish/`

**Exemple avec curl** :
```bash
curl -X POST https://egoejo-production.up.railway.app/api/contents/1/publish/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Résultat** : La tâche Celery `generate_audio_content` est lancée automatiquement.

---

## 🔍 Vérification

### 1. Vérifier via l'API

**GET** `/api/contents/<id>/`

**Réponse** :
```json
{
  "id": 1,
  "title": "Mon Contenu",
  "audio_file": "/media/educational_contents/audio/audio_1_openai.mp3",
  ...
}
```

### 2. Vérifier via Django Shell

```python
from core.models.content import EducationalContent

content = EducationalContent.objects.get(id=1)
if content.audio_file:
    print(f"✅ Audio: {content.audio_file.url}")
else:
    print("❌ Aucun audio")
```

### 3. Vérifier les logs Celery

```bash
celery -A config worker -l info
```

Les logs afficheront :
```
[INFO] Audio généré avec succès pour contenu 1
```

---

## 🐛 Dépannage

### Erreur : "OPENAI_API_KEY non configuré"

**Solution** :
1. Vérifier que `OPENAI_API_KEY` est dans `.env` ou variables d'environnement
2. Redémarrer Celery si nécessaire

### Erreur : "Texte trop court"

**Cause** : Le contenu n'a pas assez de texte (titre + description < 10 caractères).

**Solution** : Ajouter une description au contenu.

### La tâche reste en "PENDING"

**Cause** : Celery n'est pas en cours d'exécution.

**Solution** :
```bash
celery -A config worker -l info
```

### Audio non généré après publication

**Vérifications** :
1. Vérifier les logs Celery pour erreurs
2. Vérifier que `OPENAI_API_KEY` est valide
3. Vérifier que le contenu a assez de texte
4. Vérifier les quotas OpenAI (limites API)

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
[INFO] Audio généré avec succès pour contenu 1
[INFO] Fichier audio généré: educational_contents/audio/audio_1_openai.mp3
```

---

## ⚙️ Configuration

### Variables d'environnement

Voir `GUIDE_VARIABLES_ENVIRONNEMENT_V1.5.0.md` pour la configuration complète.

**Minimum requis** :
```env
OPENAI_API_KEY=sk-...
TTS_PROVIDER=openai
TTS_VOICE=alloy
```

---

**Dernière mise à jour** : 2025-01-27

