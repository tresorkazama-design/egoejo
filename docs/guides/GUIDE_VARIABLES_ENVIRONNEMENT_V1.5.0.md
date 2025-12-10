# 🔧 Guide Configuration Variables d'Environnement v1.5.0

**Date** : 2025-01-27  
**Version** : 1.5.0 - Connecté & Visuel

---

## 📋 Variables d'Environnement Requises

### 🎙️ Text-to-Speech (TTS) - Audio-First

#### Option 1 : OpenAI TTS (Recommandé)

```env
# OpenAI TTS
OPENAI_API_KEY=sk-...  # Clé API OpenAI
TTS_PROVIDER=openai    # Provider à utiliser
TTS_VOICE=alloy        # Voix OpenAI : 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'
```

**Voix disponibles OpenAI** :
- `alloy` : Voix neutre, polyvalente
- `echo` : Voix masculine
- `fable` : Voix expressive
- `onyx` : Voix masculine profonde
- `nova` : Voix féminine
- `shimmer` : Voix féminine douce

#### Option 2 : ElevenLabs TTS (Alternative)

```env
# ElevenLabs TTS
ELEVENLABS_API_KEY=...  # Clé API ElevenLabs
TTS_PROVIDER=elevenlabs # Provider à utiliser
TTS_VOICE=default       # ID de voix ElevenLabs (ou 'default')
```

**Note** : Si `OPENAI_API_KEY` est configuré, OpenAI sera utilisé par défaut. Sinon, si `ELEVENLABS_API_KEY` est configuré, ElevenLabs sera utilisé.

---

## 🚀 Configuration Backend (Railway)

### Variables à ajouter dans Railway

1. **Ouvrir Railway Dashboard** → Votre projet → Variables

2. **Ajouter les variables** :

```env
# TTS Configuration
OPENAI_API_KEY=sk-...
TTS_PROVIDER=openai
TTS_VOICE=alloy
```

**OU** (si vous préférez ElevenLabs) :

```env
ELEVENLABS_API_KEY=...
TTS_PROVIDER=elevenlabs
TTS_VOICE=default
```

3. **Redéployer** l'application pour que les variables soient prises en compte.

---

## 🧪 Configuration Développement Local

### Fichier `.env` (backend)

Créer ou mettre à jour `backend/.env` :

```env
# ... autres variables existantes ...

# TTS Configuration
OPENAI_API_KEY=sk-...
TTS_PROVIDER=openai
TTS_VOICE=alloy
```

**Note** : Ne jamais committer le fichier `.env` dans Git !

---

## 📝 Notes Importantes

### Génération Audio Automatique

- La génération audio est **automatique** lors de la publication d'un contenu éducatif.
- Si `OPENAI_API_KEY` ou `ELEVENLABS_API_KEY` n'est pas configuré, la génération audio sera ignorée (pas d'erreur).
- Les fichiers audio sont stockés sur R2/S3 (si configuré) ou localement.

### Coûts

- **OpenAI TTS** : Payant (voir tarifs OpenAI)
- **ElevenLabs TTS** : Payant (voir tarifs ElevenLabs)
- **Sentence Transformers** : Gratuit (local, mais pas pour TTS, seulement pour embeddings)

### Recommandation

Pour commencer, utilisez **OpenAI TTS** (`TTS_PROVIDER=openai`) car :
- Intégration simple
- Qualité vocale correcte
- Tarifs raisonnables

---

## ✅ Vérification

Pour vérifier que la configuration est correcte :

1. **Publier un contenu éducatif** via l'admin ou l'API
2. **Vérifier les logs Celery** pour voir si la tâche `generate_audio_content` s'exécute
3. **Vérifier le champ `audio_file`** du contenu dans la base de données

---

**Dernière mise à jour** : 2025-01-27

