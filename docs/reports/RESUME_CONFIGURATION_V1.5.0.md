# ✅ Résumé Configuration v1.5.0 - Connecté & Visuel

**Date** : 2025-01-27  
**Statut** : Configuration prête ✅

---

## 📋 Checklist Configuration

### ✅ 1. Migration Appliquée

```bash
cd backend
python manage.py migrate
```

**Résultat** : Migration `0015_add_audio_file_and_coordinates_3d` appliquée avec succès.

---

### ✅ 2. Variables d'Environnement

#### Fichier `.env` (Développement Local)

Créer ou mettre à jour `backend/.env` avec :

```env
# TTS Configuration
OPENAI_API_KEY=sk-...
TTS_PROVIDER=openai
TTS_VOICE=alloy
```

**Fichier template** : `backend/env.template` (mis à jour)

#### Railway (Production)

Ajouter dans Railway Dashboard → Variables :

```env
OPENAI_API_KEY=sk-...
TTS_PROVIDER=openai
TTS_VOICE=alloy
```

**Guide complet** : Voir `GUIDE_VARIABLES_ENVIRONNEMENT_V1.5.0.md`

---

### ✅ 3. Scripts Créés

#### Script Réduction Dimensionnalité

**Fichier** : `backend/scripts/launch_mycelium_reduction.py`

**Usage** :
```bash
cd backend
python scripts/launch_mycelium_reduction.py --method tsne --type both
```

**Options** :
- `--method tsne|umap` : Méthode (default: tsne, recommandé pour Python 3.14+)
- `--type both|projet|educational_content` : Type de contenu
- `--sync` : Exécution synchrone (pour test)

#### Script Test Audio

**Fichier** : `backend/scripts/test_audio_generation.py`

**Usage** :
```bash
cd backend
python scripts/test_audio_generation.py
```

**Options** :
- `--content-id ID` : ID spécifique du contenu
- `--provider openai|elevenlabs` : Provider TTS
- `--voice VOICE` : Voix à utiliser
- `--sync` : Exécution synchrone (pour test)

---

## 🚀 Prochaines Actions

### 1. Lancer Réduction Dimensionnalité

**Méthode recommandée** (t-SNE pour Python 3.14+) :

```bash
cd backend
python scripts/launch_mycelium_reduction.py --method tsne
```

**Vérification** :
- GET `/api/mycelium/data/` pour voir les coordonnées 3D
- Visiter `/mycelium` dans le frontend

**Guide complet** : Voir `GUIDE_LANCEMENT_MYCELIUM.md`

---

### 2. Tester Génération Audio

**Méthode recommandée** :

```bash
cd backend
python scripts/test_audio_generation.py --sync
```

**Vérification** :
- GET `/api/contents/<id>/` pour voir le champ `audio_file`
- Visiter `/podcast` dans le frontend

**Guide complet** : Voir `GUIDE_TEST_AUDIO.md`

---

### 3. Publier un Contenu (Génération Auto)

La génération audio est **automatique** lors de la publication :

```bash
# Via API
POST /api/contents/<id>/publish/
```

La tâche Celery `generate_audio_content` sera lancée automatiquement.

---

## 📚 Documentation Disponible

- `GUIDE_VARIABLES_ENVIRONNEMENT_V1.5.0.md` : Configuration variables TTS
- `GUIDE_LANCEMENT_MYCELIUM.md` : Guide réduction dimensionnalité
- `GUIDE_TEST_AUDIO.md` : Guide test génération audio
- `NOTES_INSTALLATION_UMAP.md` : Notes sur UMAP (Python 3.14)
- `ROADMAP_V1.5.0_CONNECTE_VISUEL.md` : Roadmap complète

---

## ⚠️ Notes Importantes

### UMAP vs t-SNE

- **UMAP** : Non disponible sur Python 3.14+ (limitation package)
- **t-SNE** : Disponible via `scikit-learn`, recommandé pour Python 3.14+
- **Fallback automatique** : Le code utilise t-SNE si UMAP n'est pas disponible

### Génération Audio

- **Automatique** : Lors de la publication d'un contenu
- **Asynchrone** : Via Celery (ne bloque pas l'API)
- **Optionnel** : Si `OPENAI_API_KEY` n'est pas configuré, ignoré silencieusement

---

**Dernière mise à jour** : 2025-01-27  
**Statut** : ✅ Prêt pour utilisation

