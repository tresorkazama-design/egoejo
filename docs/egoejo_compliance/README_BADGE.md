# 🏅 Badge Public "EGOEJO COMPLIANT"

**Version** : 1.0  
**Date** : 2025-01-27

---

## 🎯 Objectif

Le badge **"EGOEJO COMPLIANT"** est un label public vérifiable qui indique le niveau de conformité d'un projet aux principes philosophiques, techniques et structurels d'EGOEJO.

---

## 📊 Statuts Disponibles

### 1. `egoejo-compliant-core` (Core)

**Critères** :
- ✅ Séparation stricte SAKA / EUR
- ✅ Anti-accumulation
- ✅ Compostage obligatoire
- ✅ Circulation obligatoire
- ✅ Tests de compliance automatiques
- ✅ CI/CD bloquante
- ✅ Protection settings critiques

**Badge** : `egoejo-compliant-core.svg`

---

### 2. `egoejo-compliant-extended` (Extended)

**Critères** :
- ✅ Tous les critères Core
- ✅ Gouvernance protectrice
- ✅ Audit logs centralisés
- ✅ Monitoring temps réel

**Badge** : `egoejo-compliant-extended.svg`

---

### 3. `non-compliant` (Non Conforme)

**Critères** :
- ❌ Un ou plusieurs critères Core non respectés

**Badge** : `non-compliant.svg`

---

## 🔍 Vérification Publique

### Endpoint API

**URL** : `/api/public/egoejo-compliance.json`

**Méthode** : `GET`

**Authentification** : Aucune (public)

**Exemple de réponse** :
```json
{
  "project_name": "EGOEJO",
  "label_version": "1.0",
  "compliance_status": "egoejo-compliant-core",
  "audit_date": "2025-01-27",
  "audit_authority": "EGOEJO Compliance Team",
  "double_structure_verified": true,
  "criteria_validated": {
    "core": [
      "saka_eur_separation",
      "anti_accumulation",
      "compostage_obligatoire",
      "circulation_obligatoire"
    ],
    "extended": []
  },
  "tests_passed": {
    "total": 83,
    "passed": 83,
    "failed": 0,
    "last_run": "2025-01-27T10:30:00Z"
  },
  "philosophical_guarantees": [
    "SAKA non-financier",
    "SAKA non-monétaire",
    "SAKA non-convertible",
    "Anti-accumulation",
    "Circulation obligatoire"
  ],
  "explicit_prohibitions": [
    "Aucune conversion SAKA ↔ EUR",
    "Aucun rendement financier SAKA",
    "Aucun affichage monétaire SAKA"
  ],
  "badge_url": "https://egoejo.org/badges/egoejo-compliant-core.svg",
  "verification_url": "https://egoejo.org/api/public/egoejo-compliance.json"
}
```

---

## 📝 Intégration README GitHub

### Exemple 1 : Badge Core

```markdown
# EGOEJO

[![EGOEJO COMPLIANT](https://egoejo.org/badges/egoejo-compliant-core.svg)](https://egoejo.org/api/public/egoejo-compliance.json)

Projet conforme aux principes philosophiques EGOEJO (Core).
```

### Exemple 2 : Badge Extended

```markdown
# EGOEJO

[![EGOEJO COMPLIANT](https://egoejo.org/badges/egoejo-compliant-extended.svg)](https://egoejo.org/api/public/egoejo-compliance.json)

Projet conforme aux principes philosophiques EGOEJO (Extended).
```

### Exemple 3 : Badge avec détails

```markdown
# EGOEJO

[![EGOEJO COMPLIANT](https://egoejo.org/badges/egoejo-compliant-core.svg)](https://egoejo.org/api/public/egoejo-compliance.json)

**Statut de conformité** : Core  
**Double structure vérifiée** : ✅ SAKA ≠ EUR  
**Tests de compliance** : 83/83 passés

[Vérifier le statut complet](https://egoejo.org/api/public/egoejo-compliance.json)
```

---

## 🎨 Caractéristiques des Badges

### Style

- **Sobre** : Couleurs institutionnelles (vert foncé pour conforme, gris pour non conforme)
- **Institutionnel** : Police Arial, taille lisible
- **Explicite** : Mention "SAKA ≠ EUR • Structure Relationnelle"

### Garanties

- ✅ **Ne jamais indiquer de rendement** : Aucun pourcentage, aucun taux
- ✅ **Ne jamais indiquer de valeur financière** : Aucun montant, aucun prix
- ✅ **Référencer explicitement la double structure** : Texte "SAKA ≠ EUR • Structure Relationnelle"

---

## 📋 Schéma JSON

Le schéma JSON est défini dans `egoejo-compliance-schema.json` et suit le standard JSON Schema Draft 7.

**Validation** :
```bash
# Valider un JSON contre le schéma
ajv validate -s egoejo-compliance-schema.json -d compliance-data.json
```

---

## 🔗 Liens Utiles

- [Label EGOEJO COMPLIANT](../LABEL_EGOEJO_COMPLIANT.md)
- [Tableau de Conformité](../TABLEAU_CONFORMITE.md)
- [Architecture des Tests](../../tests/COMPLIANCE_TESTS_ARCHITECTURE.md)

---

**Fin du README Badge**

*Dernière mise à jour : 2025-01-27*

