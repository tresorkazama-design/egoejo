# 📊 Matrice Label ↔ Statuts ↔ Code

**Version** : 1.0  
**Date** : 2025-01-27

---

## 🎯 Vue d'Ensemble

Cette matrice établit la correspondance entre :
- **Label** : Critères du label "EGOEJO COMPLIANT"
- **Statuts** : Clauses statutaires (SAS à mission)
- **Code** : Fichiers et tests de compliance

---

## 📋 Matrice Complète

| # | Critère Label | Niveau | Clause Statutaire | Engagement Opposable | Fichier Code | Test Compliance | Preuve Technique |
|---|---------------|--------|-------------------|---------------------|--------------|-----------------|------------------|
| **1** | **Séparation SAKA / EUR** | Core | Raison d'être §1 | Interdiction conversion | `backend/core/models/saka.py`<br>`backend/finance/models.py` | `test_no_saka_eur_conversion.py` | Aucune ForeignKey SAKA ↔ EUR |
| **2** | **Anti-Accumulation** | Core | Raison d'être §2 | Compostage obligatoire | `backend/core/services/saka.py`<br>`backend/config/settings.py` | `test_anti_accumulation.py` | `SAKA_COMPOST_ENABLED=True` |
| **3** | **Tests Compliance** | Core | Raison d'être §6 | Tests tagués `@egoejo_compliance` | `backend/tests/compliance/` | `test_ci_cd_protection.py` | 83 tests passent |
| **4** | **CI/CD Bloquante** | Core | Raison d'être §7 | Workflow bloque merges | `.github/workflows/egoejo-compliance.yml` | `test_ci_cd_protection.py` | Workflow bloque si tests échouent |
| **5** | **Protection Settings** | Core | Raison d'être §8 | Validation fail-fast | `backend/config/settings.py` | `test_settings_protection.py` | Validation au démarrage |
| **6** | **Structure Relationnelle > Instrumentale** | Core | Raison d'être (préambule) | SAKA non-financier | `backend/core/services/saka.py` | `test_double_structure.py` | Aucun import finance dans saka.py |
| **7** | **Circulation Obligatoire** | Core | Raison d'être §3 | Redistribution équitable | `backend/core/services/saka.py`<br>`backend/config/celery.py` | `test_silo_redistribution.py` | `SAKA_SILO_REDIS_ENABLED=True` |
| **8** | **Non-Monétisation** | Core | Raison d'être §5 | Affichage en grains | `frontend/frontend/src/utils/saka.ts` | `saka-protection.test.ts` | `formatSakaAmount()` |
| **9** | **Déclaration Non-Financière** | Core | Raison d'être §5 | Documentation explicite | `docs/philosophie/MANIFESTE_SAKA_EUR.md` | Audit manuel | Manifeste publié |
| **10** | **Déclaration Non-Monétaire** | Core | Raison d'être §5 | Documentation explicite | `docs/philosophie/MANIFESTE_SAKA_EUR.md` | Audit manuel | Manifeste publié |
| **11** | **Gouvernance Protectrice** | Extended | Comité de mission | Surveillance continue | `backend/core/api/compliance_views.py` | Audit manuel | Endpoint public |
| **12** | **Audit Logs Centralisés** | Extended | Comité de mission | Logs accessibles | `backend/core/models/saka.py`<br>`backend/core/services/saka.py` | `test_admin_protection.py` | Signal `post_save` |
| **13** | **Monitoring Temps Réel** | Extended | Comité de mission | Dashboard monitoring | `backend/core/api/saka_metrics_views.py` | Audit manuel | Dashboard métriques |

---

## 🔄 Flux de Vérification

### 1. Code → Tests

**Fichier Code** : `backend/core/services/saka.py`  
**Test Compliance** : `test_anti_accumulation.py`  
**Résultat** : Tests passent ✅

### 2. Tests → CI/CD

**Test Compliance** : `test_anti_accumulation.py`  
**CI/CD** : `.github/workflows/egoejo-compliance.yml`  
**Résultat** : Workflow bloque si tests échouent ✅

### 3. CI/CD → Label

**CI/CD** : Workflow passe ✅  
**Label** : `egoejo-compliant-core`  
**Endpoint** : `/api/public/egoejo-compliance.json`

### 4. Label → Statuts

**Label** : `egoejo-compliant-core`  
**Clause Statutaire** : Raison d'être §2  
**Engagement Opposable** : Compostage obligatoire

---

## 🚫 Conditions de Retrait

### Retrait Automatique (Code)

| Condition | Fichier | Test | Action |
|-----------|---------|------|--------|
| Tests échouent | `backend/tests/compliance/` | `test_ci_cd_protection.py` | Label → `non-compliant` |
| CI/CD non bloquante | `.github/workflows/egoejo-compliance.yml` | `test_ci_cd_protection.py` | Label → `non-compliant` |
| Settings désactivés | `backend/config/settings.py` | `test_settings_protection.py` | Label → `non-compliant` |
| Conversion détectée | `backend/core/services/saka.py` | `test_no_saka_eur_conversion.py` | Label → `non-compliant` |

### Retrait par Décision (Statuts)

| Condition | Clause Statutaire | Autorité | Action |
|-----------|-------------------|----------|--------|
| Violation raison d'être | Raison d'être | Comité de mission | Recommandation retrait |
| Contournement tests | Raison d'être §6 | Comité de mission | Recommandation retrait |
| Non-respect gouvernance | Comité de mission | Conseil d'administration | Décision retrait |
| Violation golden share | Pacte d'associés | Association Guardian | Veto |

---

## 📝 Exemples Concrets

### Exemple 1 : Séparation SAKA / EUR

**Label** : Critère Core #1  
**Statuts** : Raison d'être §1  
**Code** : `backend/core/models/saka.py` (pas de ForeignKey vers UserWallet)  
**Test** : `test_no_saka_eur_conversion.py`  
**Preuve** : Aucune fonction `convert_saka_to_eur()` détectée

---

### Exemple 2 : Anti-Accumulation

**Label** : Critère Core #2  
**Statuts** : Raison d'être §2  
**Code** : `backend/config/settings.py` (`SAKA_COMPOST_ENABLED=True`)  
**Test** : `test_anti_accumulation.py`  
**Preuve** : Compostage réduit le solde après inactivité

---

### Exemple 3 : Tests Compliance

**Label** : Critère Core #3  
**Statuts** : Raison d'être §6  
**Code** : `backend/tests/compliance/` (83 tests tagués `@egoejo_compliance`)  
**Test** : `test_ci_cd_protection.py`  
**Preuve** : Tous les tests passent (83/83)

---

## 🔗 Liens Utiles

- [Cadre Juridique du Label](CADRE_JURIDIQUE_LABEL.md)
- [Label EGOEJO COMPLIANT](LABEL_EGOEJO_COMPLIANT.md)
- [Manifeste SAKA/EUR](../../philosophie/MANIFESTE_SAKA_EUR.md)

---

**Fin de la Matrice**

*Dernière mise à jour : 2025-01-27*

