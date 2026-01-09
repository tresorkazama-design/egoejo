# 📋 Exports Institutionnels EGOEJO

**Date de création** : 2025-12-10  
**Dernière mise à jour** : 2025-12-10  
**Version** : 1.0.0

---

## 🎯 Objectif

Rendre **testable et opposable** la conformité institutionnelle EGOEJO pour :
- **ONU** (Organisation des Nations Unies)
- **Fondations** (partenaires institutionnels)
- **États** (audits gouvernementaux)

---

## 📊 Endpoints Disponibles

### 1. Export Conformité ONU

**Endpoint** : `GET /api/compliance/export/un/`

**Format** : JSON

**Sections** :
- Gouvernance (Constitution, Think Tank Charter, Institut)
- Séparation SAKA/EUR (vérifications techniques, tests)
- Anti-accumulation (compostage, redistribution, métriques)
- Audits (logs, traçabilité, conformité)
- Alerting (email, Slack webhook, dédoublonnage)

**Exemple de réponse** :
```json
{
  "export_type": "un_compliance",
  "version": "1.0.0",
  "generated_at": "2025-12-10T12:00:00Z",
  "project": {
    "name": "EGOEJO",
    "url": "https://egoejo.org"
  },
  "sections": {
    "gouvernance": { ... },
    "separation_saka_eur": { ... },
    "anti_accumulation": { ... },
    "audits": { ... },
    "alerting": { ... }
  },
  "compliance_badge": {
    "url": "https://egoejo.org/api/public/egoejo-compliance-badge.svg",
    "status_endpoint": "https://egoejo.org/api/public/egoejo-compliance.json"
  }
}
```

---

### 2. Export Rapport Fondation

**Endpoint** : `GET /api/compliance/export/foundation/`

**Format** : JSON

**Sections** : Identiques à ONU + section `foundation_specific` avec :
- Transparence (rapports publics, séparation financière)
- Badge de conformité

---

### 3. Export Markdown

**Endpoints** :
- `GET /api/compliance/export/un/markdown/` - Export ONU en Markdown
- `GET /api/compliance/export/foundation/markdown/` - Export Fondation en Markdown

**Format** : Markdown (text/markdown)

**Utilisation** : Documentation, rapports imprimables, intégration dans README

---

## 🏷️ Badge "Constitution Verified"

### Endpoint Badge SVG

**Endpoint** : `GET /api/public/egoejo-compliance-badge.svg`

**Format** : SVG (image/svg+xml)

**États** :
- **Core** : Vert (conformité de base)
- **Extended** : Vert foncé (conformité étendue)
- **Non-compliant** : Gris/Rouge (non conforme)

**Caractéristiques** :
- Généré dynamiquement selon le statut de conformité
- Aucun asset externe (tout embarqué)
- Compatible README GitHub
- Change automatiquement si un test constitutionnel échoue

### Endpoint Statut JSON

**Endpoint** : `GET /api/public/egoejo-compliance.json`

**Format** : JSON

**Contenu** :
```json
{
  "compliance_status": "core" | "extended" | "non-compliant",
  "criteria": [
    {
      "id": "saka_eur_separation",
      "level": "core",
      "validated": true,
      "description": "Séparation stricte SAKA / EUR (aucune conversion possible)"
    },
    ...
  ],
  "last_audit": "2025-12-10T12:00:00Z"
}
```

---

## 🔔 Mécanisme d'Alertes Anti-Dérive

### Garanties

Le système d'alertes garantit qu'**aucune dérive** ne peut passer inaperçue :

1. **Email** : Envoi automatique d'emails pour alertes critiques
2. **Slack Webhook** : Notification en temps réel via webhook Slack
3. **Dédoublonnage** : Évite le spam d'alertes
4. **Alertes Raw SQL** : Détection automatique des tentatives de contournement

### Endpoint Métriques Alertes

**Endpoint** : `GET /api/compliance/alerts/metrics/`

**Format** : JSON

**Contenu** :
```json
{
  "total_alerts": 42,
  "alerts_by_month": [
    {"month": "2025-12", "count": 5},
    {"month": "2025-11", "count": 3},
    ...
  ],
  "last_alert_at": "2025-12-10T12:00:00Z"
}
```

---

## ✅ Tests de Validation

### Tests Automatiques

Tous les exports sont testés automatiquement :

```bash
# Tests exports institutionnels
pytest backend/core/tests/api/test_institutional_exports.py -v

# Tests badge compliance
pytest backend/core/api/__tests__/test_compliance_badge.py -v

# Tests statut compliance
pytest backend/core/api/__tests__/test_compliance_views.py -v
```

### Validations

- ✅ Format JSON valide
- ✅ Schéma respecté
- ✅ Contenu minimal présent
- ✅ Cohérence versions documents
- ✅ Badge change si test échoue
- ✅ Endpoints en lecture seule (GET uniquement)
- ✅ Accessible sans authentification (public)

---

## 📝 Documentation Complémentaire

### Sources

- **Constitution** : `/docs/constitution`
- **Think Tank Charter** : `/docs/think-tank-charter`
- **Rôle Institut** : `/docs/institute-role`

### Liens Utiles

- **Badge SVG** : `https://egoejo.org/api/public/egoejo-compliance-badge.svg`
- **Statut JSON** : `https://egoejo.org/api/public/egoejo-compliance.json`
- **Export ONU** : `https://egoejo.org/api/compliance/export/un/`
- **Export Fondation** : `https://egoejo.org/api/compliance/export/foundation/`

---

## 🔒 Sécurité

### Contraintes

- **Lecture seule** : Tous les endpoints sont en GET uniquement
- **Public** : Accessible sans authentification (transparence)
- **Cache** : Cache contrôlé (15 minutes) pour performance
- **Aucune PII** : Aucune donnée personnelle exposée

### Vérifications

- ✅ Signature HMAC-SHA256 pour rapports CI/CD
- ✅ Fraîcheur des rapports (< 24h)
- ✅ Tests automatiques bloquants en CI

---

**Dernière mise à jour** : 2025-12-10  
**Prochaine révision** : 2025-12-17

