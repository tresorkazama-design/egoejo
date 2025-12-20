# 🔌 API DE CERTIFICATION EGOEJO GUARDIAN
## Spécification Technique Complète

**Document** : Spécification API REST pour l'organisme de certification  
**Date** : 2025-12-19  
**Version** : 1.0  
**Base URL** : `https://guardian.egoejo.org/api/v1`

---

## 🔐 AUTHENTIFICATION

### API Key

Toutes les requêtes (sauf endpoints publics) nécessitent une clé API dans le header :

```
Authorization: Bearer YOUR_API_KEY
```

### Obtention d'une API Key

1. Créer un compte sur `https://guardian.egoejo.org/register`
2. Générer une API Key depuis le dashboard
3. Utiliser la clé dans les headers de requête

---

## 📋 ENDPOINTS

### 1. Soumettre un Projet pour Certification

**Endpoint** : `POST /certification/submit`

**Description** : Soumet un projet pour certification EGOEJO Compliant

**Headers** :
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body** :
```json
{
  "project_name": "Mon Projet EGOEJO",
  "project_url": "https://github.com/user/project",
  "repository_url": "https://github.com/user/project.git",
  "branch": "main",
  "contact_email": "contact@project.com",
  "description": "Description du projet",
  "version": "1.0.0",
  "license": "MIT"
}
```

**Response 201 Created** :
```json
{
  "certification_id": "cert_abc123def456",
  "status": "pending",
  "submitted_at": "2025-12-19T10:00:00Z",
  "estimated_review_time": "5-7 business days",
  "verification_url": "https://guardian.egoejo.org/certifications/cert_abc123def456"
}
```

**Errors** :
- `400 Bad Request` : Données invalides
- `401 Unauthorized` : API Key invalide
- `429 Too Many Requests` : Trop de soumissions

---

### 2. Vérifier le Statut de Certification

**Endpoint** : `GET /certification/{certification_id}`

**Description** : Récupère le statut d'une certification

**Headers** :
```
Authorization: Bearer YOUR_API_KEY (optionnel pour certifications publiques)
```

**Path Parameters** :
- `certification_id` : ID de la certification

**Response 200 OK** :
```json
{
  "certification_id": "cert_abc123def456",
  "status": "certified",
  "project_name": "Mon Projet EGOEJO",
  "project_url": "https://github.com/user/project",
  "certified_at": "2025-12-20T14:30:00Z",
  "expires_at": "2026-12-20T14:30:00Z",
  "badge_url": "https://guardian.egoejo.org/badges/cert_abc123def456.svg",
  "report_url": "https://guardian.egoejo.org/reports/cert_abc123def456.pdf",
  "score": 100,
  "checks": {
    "no_saka_eur_conversion": {
      "status": "pass",
      "message": "Aucune conversion SAKA/EUR détectée"
    },
    "no_financial_return": {
      "status": "pass",
      "message": "Aucun rendement financier sur SAKA détecté"
    },
    "no_monetary_display": {
      "status": "pass",
      "message": "Aucun affichage monétaire du SAKA détecté"
    },
    "saka_priority": {
      "status": "pass",
      "message": "SAKA est prioritaire et non désactivé"
    },
    "anti_accumulation": {
      "status": "pass",
      "message": "Mécanisme d'anti-accumulation présent"
    },
    "saka_cycle": {
      "status": "pass",
      "message": "Cycle SAKA complet et incompressible"
    }
  }
}
```

**Status possibles** :
- `pending` : En attente de vérification
- `in_review` : En cours de vérification
- `certified` : Certifié EGOEJO Compliant
- `rejected` : Rejeté (non conforme)
- `expired` : Certification expirée
- `revoked` : Certification révoquée

**Errors** :
- `404 Not Found` : Certification introuvable
- `401 Unauthorized` : Accès non autorisé

---

### 3. Vérifier la Conformité d'un Repository

**Endpoint** : `POST /certification/verify`

**Description** : Vérifie la conformité d'un repository sans créer de certification

**Headers** :
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body** :
```json
{
  "repository_url": "https://github.com/user/project.git",
  "branch": "main",
  "commit_sha": "abc123def456..." // optionnel
}
```

**Response 200 OK** :
```json
{
  "is_compliant": true,
  "violations": [],
  "checks": {
    "no_saka_eur_conversion": {
      "status": "pass",
      "message": "Aucune conversion SAKA/EUR détectée",
      "details": {}
    },
    "no_financial_return": {
      "status": "pass",
      "message": "Aucun rendement financier sur SAKA détecté",
      "details": {}
    },
    "no_monetary_display": {
      "status": "pass",
      "message": "Aucun affichage monétaire du SAKA détecté",
      "details": {}
    },
    "saka_priority": {
      "status": "pass",
      "message": "SAKA est prioritaire et non désactivé",
      "details": {}
    },
    "anti_accumulation": {
      "status": "pass",
      "message": "Mécanisme d'anti-accumulation présent",
      "details": {
        "compost_function_found": true,
        "compost_enabled": true
      }
    },
    "saka_cycle": {
      "status": "pass",
      "message": "Cycle SAKA complet et incompressible",
      "details": {
        "harvest_function": true,
        "spend_function": true,
        "compost_function": true,
        "silo_function": true,
        "redistribution_function": true
      }
    }
  },
  "score": 100,
  "certification_eligible": true,
  "warnings": []
}
```

**Response avec violations** :
```json
{
  "is_compliant": false,
  "violations": [
    {
      "rule": "no_saka_eur_conversion",
      "severity": "critical",
      "file": "services/saka.py",
      "line": 42,
      "message": "Conversion SAKA/EUR détectée: convert_saka_to_eur()"
    }
  ],
  "checks": {
    "no_saka_eur_conversion": {
      "status": "fail",
      "message": "Conversion SAKA/EUR détectée",
      "details": {
        "violations_count": 1,
        "files_affected": ["services/saka.py"]
      }
    }
  },
  "score": 0,
  "certification_eligible": false,
  "warnings": []
}
```

**Errors** :
- `400 Bad Request` : Repository invalide ou inaccessible
- `401 Unauthorized` : API Key invalide
- `429 Too Many Requests` : Trop de vérifications

---

### 4. Télécharger le Badge de Certification

**Endpoint** : `GET /certification/{certification_id}/badge`

**Description** : Récupère le badge de certification (SVG ou PNG)

**Query Parameters** :
- `format` : `svg` (défaut) ou `png`
- `size` : `small`, `medium` (défaut), `large` (uniquement pour PNG)
- `style` : `flat` (défaut) ou `plastic`

**Response 200 OK** :
- **SVG** : `Content-Type: image/svg+xml`
- **PNG** : `Content-Type: image/png`

**Exemple d'utilisation** :
```markdown
[![EGOEJO Compliant](https://guardian.egoejo.org/api/v1/certification/cert_abc123def456/badge?format=svg)](https://guardian.egoejo.org/certifications/cert_abc123def456)
```

**Errors** :
- `404 Not Found` : Certification introuvable
- `400 Bad Request` : Format ou taille invalide

---

### 5. Obtenir le Rapport de Certification

**Endpoint** : `GET /certification/{certification_id}/report`

**Description** : Télécharge le rapport de certification PDF

**Headers** :
```
Authorization: Bearer YOUR_API_KEY (optionnel pour certifications publiques)
```

**Response 200 OK** :
- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename="certification_report_cert_abc123def456.pdf"`

**Errors** :
- `404 Not Found` : Certification introuvable ou rapport non disponible
- `401 Unauthorized` : Accès non autorisé

---

### 6. Liste des Certifications Publiques

**Endpoint** : `GET /certifications/public`

**Description** : Liste publique des projets certifiés

**Query Parameters** :
- `page` : Numéro de page (défaut: 1)
- `per_page` : Nombre de résultats par page (défaut: 20, max: 100)
- `status` : Filtrer par statut (`certified`, `expired`, `revoked`)
- `sort` : Trier par (`certified_at`, `project_name`) (défaut: `certified_at`)
- `order` : Ordre (`asc`, `desc`) (défaut: `desc`)

**Response 200 OK** :
```json
{
  "total": 42,
  "page": 1,
  "per_page": 20,
  "total_pages": 3,
  "certifications": [
    {
      "certification_id": "cert_abc123def456",
      "project_name": "Mon Projet EGOEJO",
      "project_url": "https://github.com/user/project",
      "certified_at": "2025-12-20T14:30:00Z",
      "expires_at": "2026-12-20T14:30:00Z",
      "status": "certified",
      "badge_url": "https://guardian.egoejo.org/badges/cert_abc123def456.svg"
    },
    ...
  ]
}
```

---

### 7. Webhooks (Notifications)

**Endpoint** : `POST /webhooks` (côté client)

**Description** : Le système Guardian envoie des webhooks pour notifier les changements de statut

**Configuration** :
1. Configurer l'URL du webhook dans le dashboard
2. Le système enverra des notifications POST à cette URL

**Payload** :
```json
{
  "event": "certification.status_changed",
  "certification_id": "cert_abc123def456",
  "status": "certified",
  "timestamp": "2025-12-20T14:30:00Z",
  "data": {
    "previous_status": "in_review",
    "score": 100,
    "checks": {...}
  }
}
```

**Événements** :
- `certification.submitted` : Certification soumise
- `certification.status_changed` : Statut changé
- `certification.certified` : Certification accordée
- `certification.rejected` : Certification refusée
- `certification.expired` : Certification expirée
- `certification.revoked` : Certification révoquée

**Sécurité** :
- Signature HMAC-SHA256 dans le header `X-Guardian-Signature`
- Vérifier la signature côté client

---

## 📊 CODES DE STATUT HTTP

- `200 OK` : Requête réussie
- `201 Created` : Ressource créée
- `400 Bad Request` : Données invalides
- `401 Unauthorized` : Authentification requise
- `403 Forbidden` : Accès refusé
- `404 Not Found` : Ressource introuvable
- `429 Too Many Requests` : Limite de taux dépassée
- `500 Internal Server Error` : Erreur serveur
- `503 Service Unavailable` : Service temporairement indisponible

---

## 🔒 RATE LIMITING

### Limites par défaut

- **Soumission de certification** : 5 par jour
- **Vérification de repository** : 20 par jour
- **Requêtes générales** : 100 par heure

### Headers de Rate Limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## 📝 EXEMPLES D'UTILISATION

### Python

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://guardian.egoejo.org/api/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Soumettre une certification
response = requests.post(
    f"{BASE_URL}/certification/submit",
    headers=headers,
    json={
        "project_name": "Mon Projet",
        "repository_url": "https://github.com/user/project.git",
        "contact_email": "contact@project.com"
    }
)

certification = response.json()
print(f"Certification ID: {certification['certification_id']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key';
const BASE_URL = 'https://guardian.egoejo.org/api/v1';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  }
});

// Vérifier la conformité
async function verifyCompliance(repoUrl) {
  const response = await client.post('/certification/verify', {
    repository_url: repoUrl,
    branch: 'main'
  });
  
  return response.data;
}
```

### cURL

```bash
# Soumettre une certification
curl -X POST https://guardian.egoejo.org/api/v1/certification/submit \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Mon Projet",
    "repository_url": "https://github.com/user/project.git",
    "contact_email": "contact@project.com"
  }'

# Vérifier le statut
curl https://guardian.egoejo.org/api/v1/certification/cert_abc123def456 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🧪 TESTS

### Endpoint de Test

**Endpoint** : `GET /health`

**Description** : Vérifie l'état du service

**Response 200 OK** :
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-19T10:00:00Z"
}
```

---

## 📚 DOCUMENTATION COMPLÈTE

- **Documentation interactive** : https://guardian.egoejo.org/docs
- **Postman Collection** : https://guardian.egoejo.org/api/postman.json
- **OpenAPI Spec** : https://guardian.egoejo.org/api/openapi.json

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Base URL : https://guardian.egoejo.org/api/v1**

