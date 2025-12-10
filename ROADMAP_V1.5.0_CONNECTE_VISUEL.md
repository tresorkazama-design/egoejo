# 🚀 Roadmap v1.5.0 - EGOEJO "Connecté & Visuel"

**Date** : 2025-01-27  
**Objectif** : Rendre le système "Connecté" (Fediverse) et "Visuel" (Mycélium 3D)

---

## 🎯 Vue d'Ensemble

Après avoir rendu EGOEJO "Intelligent" (v1.4.0) et "Sécurisé", cette version le rend "Connecté" au Fediverse et "Visuel" avec une visualisation 3D des données.

---

## 📋 Axes d'Implémentation

### 1. 🌐 Le "Mycélium Numérique" (Visualisation 3D des Données)

**Concept** : Visualisation 3D des projets et contenus éducatifs basée sur leurs embeddings sémantiques.

**Technique** :
- Réduction de dimensionnalité (UMAP ou t-SNE) via Celery
- Transformation embeddings (haute dimension) → coordonnées 3D (x, y, z)
- Visualisation Three.js côté frontend

**Résultat** : L'utilisateur voit visuellement que le projet "Potager Partagé" est proche de la conférence "Cours aux Agriculteurs" (Steiner), créant un réseau de savoir visible.

**Implémentation** :
- [ ] Tâche Celery `reduce_embeddings_to_3d` (UMAP/t-SNE)
- [ ] Modèle `Projet` et `EducationalContent` : champs `coordinates_3d` (JSONField)
- [ ] Composant React `MyceliumVisualization` (Three.js)
- [ ] Page `/mycelium` pour visualisation complète
- [ ] Endpoint API `/api/mycelium/data/` pour récupérer coordonnées

**Priorité** : 🔴 HAUTE (impact visuel fort)

---

### 2. 🌍 Fédération (ActivityPub)

**Concept** : Intégrer EGOEJO au Fediverse (Mastodon, Lemmy, PeerTube).

**Pourquoi** : Les projets/contenus EGOEJO peuvent être suivis et commentés depuis Mastodon, augmentant la portée sans créer de compte.

**Technique** :
- Implémenter protocole ActivityPub (Actor, Outbox, Inbox)
- Endpoints WebFinger pour découverte
- Endpoints ActivityPub pour activités (Create, Update, Delete)
- Signature HTTP pour authentification

**Implémentation** :
- [ ] Package Python `django-activitypub` ou implémentation custom
- [ ] Modèle `Actor` pour représenter Projet/Contenu comme acteur Fediverse
- [ ] Endpoints ActivityPub : `/api/activitypub/actor/<id>/`, `/api/activitypub/outbox/`, etc.
- [ ] WebFinger : `/.well-known/webfinger`
- [ ] Signature HTTP (HTTP Signatures)
- [ ] Documentation intégration Mastodon/Lemmy

**Priorité** : 🟡 MOYENNE (impact réseau, complexité moyenne)

---

### 3. 🔊 Accessibilité "Audio-First" (TTS)

**Concept** : Génération automatique de versions audio pour contenus éducatifs.

**Pourquoi** : Public cible souvent dehors, les mains dans la terre, loin des écrans.

**Technique** :
- Tâche Celery `generate_audio_content` (OpenAI TTS ou ElevenLabs)
- Stockage MP3 sur R2/S3
- Mode "Podcast" dans l'interface

**Implémentation** :
- [ ] Tâche Celery `generate_audio_content` (OpenAI TTS ou ElevenLabs)
- [ ] Modèle `EducationalContent` : champ `audio_file` (FileField)
- [ ] Génération automatique lors de publication
- [ ] Composant React `AudioPlayer` pour lecture
- [ ] Page `/podcast` pour liste des contenus audio
- [ ] Endpoint API `/api/contents/<id>/audio/` pour streaming

**Priorité** : 🔴 HAUTE (accessibilité terrain)

---

## 📊 Plan d'Implémentation

### Phase 1 : Mycélium Numérique (Semaine 1-2)
- [ ] Installer dépendances (umap-learn ou scikit-learn pour t-SNE)
- [ ] Créer tâche Celery réduction dimensionnalité
- [ ] Ajouter champs `coordinates_3d` aux modèles
- [ ] Créer composant Three.js `MyceliumVisualization`
- [ ] Créer page `/mycelium`
- [ ] Endpoint API pour données 3D

### Phase 2 : TTS Audio-First (Semaine 3-4)
- [ ] Installer dépendances (openai pour TTS)
- [ ] Créer tâche Celery génération audio
- [ ] Ajouter champ `audio_file` à `EducationalContent`
- [ ] Génération automatique lors publication
- [ ] Créer composant `AudioPlayer`
- [ ] Page `/podcast`

### Phase 3 : Fédération ActivityPub (Semaine 5-6)
- [ ] Rechercher/installer package ActivityPub ou implémentation custom
- [ ] Créer modèle `Actor`
- [ ] Implémenter endpoints ActivityPub
- [ ] WebFinger discovery
- [ ] Signature HTTP
- [ ] Tests intégration Mastodon

---

## 🛠️ Dépendances Requises

### Backend
- `umap-learn>=0.5.0` ou `scikit-learn>=1.0.0` (pour t-SNE) - Mycélium
- `openai>=1.0.0` (déjà installé) - TTS
- `django-activitypub` (optionnel) ou implémentation custom - Fediverse

### Frontend
- `three` (déjà installé) - Visualisation 3D
- `@react-three/fiber` (déjà installé) - React Three.js
- `@react-three/drei` (déjà installé) - Helpers Three.js

---

## 📋 Checklist Implémentation

### Mycélium Numérique
- [ ] Tâche Celery créée
- [ ] Champs `coordinates_3d` ajoutés
- [ ] Composant React créé
- [ ] Page `/mycelium` créée
- [ ] Endpoint API créé

### TTS Audio-First
- [ ] Tâche Celery créée
- [ ] Champ `audio_file` ajouté
- [ ] Génération automatique configurée
- [ ] Composant `AudioPlayer` créé
- [ ] Page `/podcast` créée

### Fédération ActivityPub
- [ ] Package/implémentation choisie
- [ ] Modèle `Actor` créé
- [ ] Endpoints ActivityPub créés
- [ ] WebFinger configuré
- [ ] Tests intégration

---

**Dernière mise à jour** : 2025-01-27  
**Statut** : 📋 Plan d'action détaillé

