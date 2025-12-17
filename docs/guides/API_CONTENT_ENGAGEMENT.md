# Documentation API - Content & Engagement

## Vue d'ensemble

Cette documentation décrit les endpoints API pour gérer les contenus éducatifs et les engagements d'aide dans EGOEJO.

**Base URL** : `/api/`

**Format** : JSON

**Permissions** : La plupart des endpoints sont publics (`AllowAny`), sauf indication contraire.

---

## 📚 Contenus Éducatifs (`/api/contents/`)

### Vue d'ensemble

Les contenus éducatifs incluent : podcasts, vidéos, PDF, articles, poèmes, chansons, etc.

**ViewSet** : `EducationalContentViewSet`

**Permissions** : `AllowAny` (public)

**Cache** : Les contenus publiés sont mis en cache Redis pendant 10 minutes.

---

### 1. Liste des contenus

**GET** `/api/contents/`

Liste tous les contenus éducatifs disponibles, avec filtrage optionnel par statut.

#### Query Parameters

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `status` | string | Non | Filtre par statut. Valeurs possibles :<br>- `"published"` : Contenus publiés (par défaut, mis en cache)<br>- `"pending"` : Contenus en attente de validation<br>- `"draft"` : Brouillons<br>- `"rejected"` : Contenus rejetés |

#### Exemples de requêtes

```bash
# Liste tous les contenus publiés (par défaut)
GET /api/contents/

# Liste les contenus en attente
GET /api/contents/?status=pending

# Liste les brouillons
GET /api/contents/?status=draft
```

#### Réponse (200 OK)

```json
[
  {
    "id": 1,
    "title": "Introduction à la biodynamie",
    "slug": "introduction-biodynamie",
    "type": "article",
    "status": "published",
    "category": "racines-philosophie",
    "description": "Une introduction aux principes de la biodynamie...",
    "content": "# Introduction\n\nLa biodynamie est...",
    "tags": ["biodynamie", "agriculture", "steiner"],
    "author": 5,
    "file": "/media/contents/biodynamie.pdf",
    "audio_file": "/media/audio/biodynamie.mp3",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-16T14:20:00Z"
  },
  ...
]
```

#### Notes

- Les contenus publiés sont mis en cache Redis pendant 10 minutes pour améliorer les performances.
- Le tri est par date de création décroissante (plus récents en premier).

---

### 2. Détail d'un contenu

**GET** `/api/contents/{id}/`

Retourne les détails complets d'un contenu éducatif spécifique.

#### Réponse (200 OK)

Même structure que la liste, mais pour un seul objet.

#### Réponse (404 Not Found)

```json
{
  "detail": "Not found."
}
```

---

### 3. Créer un contenu

**POST** `/api/contents/`

Propose un nouveau contenu éducatif. Le contenu est créé avec le statut `"pending"` (en attente de validation).

#### Body JSON (requis)

```json
{
  "title": "Mon article sur la permaculture",
  "slug": "mon-article-permaculture",  // Optionnel, généré automatiquement si non fourni
  "type": "article",  // "podcast", "video", "pdf", "article", "poeme", "chanson", "autre"
  "category": "guides",  // "ressources", "guides", "videos", "racines-philosophie", "autres"
  "description": "Une description courte...",
  "content": "# Mon article\n\nContenu complet en markdown...",
  "tags": ["permaculture", "jardinage"],
  "file": null  // Optionnel : fichier uploadé (PDF, audio, vidéo, image)
}
```

#### Réponse (201 Created)

Contenu créé avec toutes les données, y compris l'ID généré.

#### Réponse (400 Bad Request)

```json
{
  "title": ["This field is required."],
  "type": ["Invalid choice."]
}
```

#### Comportement automatique

- **Scan antivirus** : Si un fichier est uploadé, un scan antivirus asynchrone est lancé (Celery).
- **Validation du type MIME** : Vérification que le fichier est de type PDF, audio, vidéo ou image.
- **Génération d'embedding** : Un embedding est généré en arrière-plan pour la recherche sémantique.
- **Invalidation du cache** : Le cache des contenus publiés est invalidé.

#### Notes

- L'auteur est défini automatiquement si l'utilisateur est authentifié, sinon `null`.
- Le contenu doit être validé par un admin via l'endpoint `/publish/` avant d'être visible publiquement.

---

### 4. Publier un contenu

**POST** `/api/contents/{id}/publish/`

Publie un contenu (change le statut de `"pending"` à `"published"`). Généralement appelé par un admin après validation.

#### Body JSON

Aucun requis.

#### Réponse (200 OK)

Contenu publié avec les données complètes.

#### Comportement automatique

- **Génération d'audio** : L'audio du contenu est généré automatiquement en arrière-plan (TTS).
  - Utilise le provider configuré (OpenAI par défaut, ou ElevenLabs).
  - Vérifie le hash pour éviter les régénérations inutiles.
- **Invalidation du cache** : Le cache des contenus publiés est invalidé.

#### Notes

- La génération d'audio est asynchrone (Celery) et peut prendre quelques minutes.
- Le contenu devient visible publiquement après publication.

---

### 5. Marquer un contenu comme consommé

**POST** `/api/contents/{id}/mark-consumed/`

Marque un contenu comme consommé et déclenche la récolte SAKA si le seuil de progression est atteint.

**Permissions** : `IsAuthenticated` (requis)

#### Body JSON (optionnel)

```json
{
  "progress": 100  // Pourcentage de consommation (0-100), défaut: 100
}
```

#### Réponse (200 OK - Succès)

Si `progress >= 80%` (seuil de consommation) :

```json
{
  "ok": true,
  "message": "Contenu marqué comme consommé. Grains SAKA récoltés.",
  "content_id": 1,
  "progress": 100
}
```

#### Réponse (400 Bad Request - Progression insuffisante)

Si `progress < 80%` :

```json
{
  "ok": false,
  "message": "Progression insuffisante (50% < 80%)",
  "progress": 50
}
```

#### Réponse (401 Unauthorized)

Si l'utilisateur n'est pas authentifié :

```json
{
  "error": "Authentification requise"
}
```

#### Notes

- **Seuil de consommation** : 80% minimum pour considérer le contenu comme "lu/écouté".
- **Récolte SAKA** : Des grains SAKA sont récoltés automatiquement (Knowledge Mining, Phase 1).
- **Raison SAKA** : `CONTENT_READ`
- Cette action fait partie du système SAKA pour récompenser l'engagement dans la consommation de contenu éducatif.

---

## 🤝 Engagements d'Aide (`/api/engagements/`)

### Vue d'ensemble

Les engagements d'aide sont des offres d'aide déposées par les membres (financier, temps, compétences, matériel).

**ViewSet** : `EngagementViewSet`

**Permissions** : `AllowAny` (public)

**Note** : Correspond au formulaire "Je veux aider" côté frontend.

---

### 1. Liste des engagements

**GET** `/api/engagements/`

Liste tous les engagements d'aide disponibles.

#### Query Parameters

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `help_request` | integer | Non | ID d'une demande d'aide (HelpRequest). Filtre les engagements liés à cette demande spécifique. |

#### Exemples de requêtes

```bash
# Liste tous les engagements
GET /api/engagements/

# Liste les engagements liés à une demande d'aide spécifique
GET /api/engagements/?help_request=123
```

#### Réponse (200 OK)

```json
[
  {
    "id": 1,
    "user": 5,  // ID utilisateur si authentifié, sinon null
    "help_request": 123,  // ID demande d'aide si lié, sinon null
    "help_type": "competences",  // "financier", "temps", "competences", "materiel"
    "description": "Je peux aider avec mes compétences en développement web...",
    "scope": "both",  // "local", "international", "both"
    "anonymity": "pseudo",  // "pseudo", "team_only"
    "status": "new",  // "new", "in_review", "active", "archived"
    "contact_email": "john@example.com",
    "contact_phone": "+33123456789",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  },
  ...
]
```

#### Notes

- Le tri est par date de création décroissante (plus récents en premier).
- Les engagements sont visibles selon les règles d'anonymité définies.

---

### 2. Créer un engagement

**POST** `/api/engagements/`

Crée un nouvel engagement d'aide. L'engagement est créé avec le statut `"new"` (nouvel engagement).

#### Body JSON (requis)

```json
{
  "help_request": 123,  // Optionnel : ID demande d'aide si lié, sinon null
  "help_type": "competences",  // "financier", "temps", "competences", "materiel"
  "description": "Je peux aider avec mes compétences en développement web...",
  "scope": "both",  // "local", "international", "both"
  "anonymity": "pseudo",  // "pseudo", "team_only"
  "contact_email": "john@example.com",  // Requis
  "contact_phone": "+33123456789"  // Optionnel
}
```

#### Réponse (201 Created)

Engagement créé avec toutes les données, y compris l'ID généré.

#### Réponse (400 Bad Request)

```json
{
  "contact_email": ["This field is required."],
  "help_type": ["Invalid choice."]
}
```

#### Notes

- L'utilisateur est défini automatiquement si authentifié, sinon `null`.
- L'engagement peut être lié à une demande d'aide spécifique (`help_request`).
- L'équipe EGOEJO peut voir tous les engagements pour les matcher avec les besoins.

---

## 🔐 Authentification

La plupart des endpoints sont publics (`AllowAny`), mais certains nécessitent une authentification :

- **Marquer un contenu comme consommé** (`/api/contents/{id}/mark-consumed/`) : Requiert une authentification JWT.

Pour les autres endpoints, l'authentification est optionnelle mais peut influencer les données retournées (ex: auteur d'un contenu).

---

## 📝 Notes importantes

### Cache

- Les contenus publiés sont mis en cache Redis pendant 10 minutes.
- Le cache est invalidé automatiquement lors de la création ou publication d'un nouveau contenu.

### Tâches asynchrones (Celery)

Plusieurs actions déclenchent des tâches asynchrones :

- **Scan antivirus** : Lors de l'upload d'un fichier.
- **Validation du type MIME** : Lors de l'upload d'un fichier.
- **Génération d'embedding** : Lors de la création d'un contenu.
- **Génération d'audio (TTS)** : Lors de la publication d'un contenu.

Ces tâches sont exécutées en arrière-plan et peuvent prendre quelques minutes.

### SAKA

Le système SAKA récompense l'engagement dans la consommation de contenu :

- **Récolte SAKA** : Lorsqu'un contenu est marqué comme consommé (≥80% de progression).
- **Raison** : `CONTENT_READ` (Knowledge Mining, Phase 1).

---

## 🐛 Gestion des erreurs

### Codes de statut HTTP

- **200 OK** : Succès (GET, PUT, PATCH)
- **201 Created** : Ressource créée avec succès (POST)
- **400 Bad Request** : Erreur de validation
- **401 Unauthorized** : Authentification requise
- **404 Not Found** : Ressource introuvable
- **500 Internal Server Error** : Erreur serveur

### Format des erreurs

```json
{
  "detail": "Message d'erreur",
  // ou
  "field_name": ["Erreur de validation pour ce champ"]
}
```

---

## 📚 Ressources supplémentaires

- [Documentation Django REST Framework](https://www.django-rest-framework.org/)
- [Documentation SAKA Protocol](../architecture/PROTOCOLE_SAKA_V2.1.md)
- [Architecture EGOEJO](../architecture/ARCHITECTURE_V2_SCALE.md)

