# ⚖️ Cadre Juridique du Label "EGOEJO COMPLIANT"

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Document Juridique-Technique

---

## 🎯 Objectif

Ce document aligne le label **"EGOEJO COMPLIANT"** avec le cadre juridique d'EGOEJO, notamment :

- **SAS à mission** (raison d'être, objectifs statutaires, comité de mission)
- **Association loi 1901 "Guardian"** (protection de la mission)
- **Obligations de gouvernance** (pacte d'associés, golden share)

---

## 📋 Points de Jonction Label ↔ Cadre Juridique

### 1. Raison d'Être (SAS à Mission)

**Article L210-10 du Code de commerce** : La SAS peut définir une raison d'être dans ses statuts.

**Correspondance Label** :
- ✅ **Critère Core** : "Structure Relationnelle > Structure Instrumentale"
- ✅ **Critère Core** : "Séparation stricte SAKA / EUR"
- ✅ **Critère Core** : "Anti-accumulation"

**Clause Statutaire Recommandée** :

```markdown
Article X - Raison d'Être

La société a pour raison d'être de promouvoir une économie relationnelle 
où la structure relationnelle (SAKA) prime toujours sur la structure 
instrumentale (EUR). 

La société s'engage à :
- Maintenir une séparation stricte entre SAKA (non-financier, non-monétaire) 
  et EUR (monnaie fiduciaire)
- Garantir l'anti-accumulation du SAKA par le compostage obligatoire
- Assurer la circulation obligatoire du SAKA via la redistribution équitable
- Ne jamais permettre de conversion SAKA ↔ EUR
- Ne jamais présenter le SAKA comme un instrument financier ou monétaire
```

---

### 2. Objectifs Statutaires

**Article L210-10 du Code de commerce** : Les objectifs sociaux doivent être compatibles avec la raison d'être.

**Correspondance Label** :
- ✅ **Critère Core** : "Tests de Compliance Automatiques"
- ✅ **Critère Core** : "CI/CD Bloquante"
- ✅ **Critère Core** : "Protection Settings Critiques"

**Clause Statutaire Recommandée** :

```markdown
Article Y - Objectifs Statutaires

La société s'engage à :
- Maintenir des tests de compliance automatiques qui vérifient la conformité 
  philosophique (tests tagués @egoejo_compliance)
- Garantir que la CI/CD bloque toute fusion violant la philosophie EGOEJO
- Protéger les settings critiques (compostage, redistribution) par validation 
  au démarrage (fail-fast)
- Documenter publiquement le statut de conformité via l'endpoint 
  /api/public/egoejo-compliance.json
```

---

### 3. Comité de Mission

**Article L210-10 du Code de commerce** : Le comité de mission surveille l'exécution de la raison d'être.

**Correspondance Label** :
- ✅ **Critère Extended** : "Gouvernance Protectrice"
- ✅ **Critère Extended** : "Audit Logs Centralisés"
- ✅ **Critère Extended** : "Monitoring Temps Réel"

**Clause Statutaire Recommandée** :

```markdown
Article Z - Comité de Mission

Le comité de mission est composé de [X] membres indépendants, dont au moins 
un représentant de l'association Guardian.

Le comité de mission a pour mission de :
- Vérifier que les tests de compliance passent (83/83)
- S'assurer que le label "EGOEJO COMPLIANT" est maintenu
- Auditer les logs de compliance (modifications directes SakaWallet, etc.)
- Surveiller le monitoring temps réel (compostage, redistribution)
- Recommander le retrait du label en cas de violation grave

Le comité de mission se réunit au moins [trimestriellement] et peut demander 
un audit technique à tout moment.
```

---

### 4. Pacte d'Associés (Golden Share)

**Droit des sociétés** : Le pacte d'associés peut prévoir des clauses de protection.

**Correspondance Label** :
- ✅ **Critère Core** : "Primauté Relationnelle > Instrumentale"
- ✅ **Critère Core** : "Non-Monétisation"

**Clause Pacte Recommandée** :

```markdown
Article A - Golden Share (Association Guardian)

L'association Guardian détient une "golden share" qui lui confère un droit 
de veto sur toute décision violant la philosophie EGOEJO, notamment :

- Activation de V2.0 (Investment) sans validation du comité de mission
- Désactivation du compostage ou de la redistribution SAKA
- Introduction d'une conversion SAKA ↔ EUR
- Modification des tests de compliance sans validation
- Changement de la raison d'être sans validation

La golden share est inaliénable et ne peut être transférée qu'à une autre 
association à but non lucratif partageant la même mission.
```

---

## 🔄 Traduction Critères Label → Clauses Statutaires

### Matrice Label ↔ Statuts ↔ Code

| # | Critère Label | Clause Statutaire | Engagement Opposable | Règle Gouvernance | Preuve Technique |
|---|---------------|-------------------|---------------------|-------------------|------------------|
| **1** | **Séparation SAKA / EUR** | Raison d'être : "SAKA ≠ EUR" | Interdiction conversion | Golden share veto | Tests `test_no_saka_eur_conversion.py` |
| **2** | **Anti-Accumulation** | Raison d'être : "Compostage obligatoire" | Compostage activé en prod | Comité mission audit | Tests `test_anti_accumulation.py` |
| **3** | **Tests Compliance** | Objectif statutaire : "Tests automatiques" | Tests tagués `@egoejo_compliance` | CI/CD bloquante | Tests `test_ci_cd_protection.py` |
| **4** | **CI/CD Bloquante** | Objectif statutaire : "CI/CD bloque violations" | Workflow bloque merges | Comité mission vérification | Workflow `.github/workflows/egoejo-compliance.yml` |
| **5** | **Protection Settings** | Objectif statutaire : "Settings protégés" | Validation fail-fast | Comité mission audit | Tests `test_settings_protection.py` |
| **6** | **Structure Relationnelle > Instrumentale** | Raison d'être : "Primauté relationnelle" | SAKA non-financier | Golden share veto | Tests `test_double_structure.py` |
| **7** | **Circulation Obligatoire** | Raison d'être : "Redistribution équitable" | Redistribution activée | Comité mission audit | Tests `test_silo_redistribution.py` |
| **8** | **Non-Monétisation** | Raison d'être : "SAKA non-monétaire" | Affichage en grains | Golden share veto | Tests `test_no_monetary_display.py` |
| **9** | **Déclaration Non-Financière** | Raison d'être : "SAKA non-financier" | Documentation explicite | Comité mission vérification | Manifeste SAKA/EUR |
| **10** | **Déclaration Non-Monétaire** | Raison d'être : "SAKA non-monétaire" | Documentation explicite | Comité mission vérification | Manifeste SAKA/EUR |
| **11** | **Gouvernance Protectrice** | Comité de mission | Surveillance continue | Comité mission réunions | Audit logs |
| **12** | **Audit Logs Centralisés** | Comité de mission | Logs accessibles | Comité mission audit | Système de logs |
| **13** | **Monitoring Temps Réel** | Comité de mission | Dashboard monitoring | Comité mission surveillance | Dashboard métriques |

---

## 🚫 Conditions de Retrait du Label

### Retrait Automatique

Le label est **automatiquement retiré** si :

1. ❌ **Tests de compliance échouent** : Un ou plusieurs tests `@egoejo_compliance` échouent
2. ❌ **CI/CD non bloquante** : Le workflow de compliance n'est plus bloquant
3. ❌ **Settings critiques désactivés** : Compostage ou redistribution désactivés en production
4. ❌ **Conversion SAKA ↔ EUR** : Une fonction ou endpoint de conversion est détecté
5. ❌ **Accumulation possible** : Le compostage ne fonctionne plus ou est contourné

**Preuve Technique** : Endpoint `/api/public/egoejo-compliance.json` retourne `"compliance_status": "non-compliant"`

---

### Retrait par Décision du Comité de Mission

Le comité de mission peut **recommander le retrait** si :

1. ⚠️ **Violation grave de la raison d'être** : Décision violant la philosophie EGOEJO
2. ⚠️ **Contournement des tests** : Tests désactivés ou modifiés sans validation
3. ⚠️ **Non-respect de la gouvernance** : Décision prise sans validation du comité
4. ⚠️ **Violation du pacte d'associés** : Décision violant la golden share

**Procédure** :
1. Le comité de mission constate la violation
2. Notification écrite à la direction
3. Délai de correction : 30 jours
4. Si non corrigé : Recommandation de retrait au conseil d'administration
5. Décision finale : Conseil d'administration (majorité qualifiée)

---

## 👥 Autorité de Retrait

### Hiérarchie des Autorités

1. **Tests Automatiques** (Priorité 1)
   - **Autorité** : Système de tests
   - **Action** : Retrait automatique si tests échouent
   - **Réversibilité** : Oui (si tests repassent)

2. **Comité de Mission** (Priorité 2)
   - **Autorité** : Comité de mission (majorité simple)
   - **Action** : Recommandation de retrait
   - **Réversibilité** : Oui (si violation corrigée)

3. **Conseil d'Administration** (Priorité 3)
   - **Autorité** : Conseil d'administration (majorité qualifiée)
   - **Action** : Décision finale de retrait
   - **Réversibilité** : Oui (si conditions remplies)

4. **Association Guardian** (Priorité 4 - Veto)
   - **Autorité** : Golden share (droit de veto)
   - **Action** : Veto sur toute décision violant la philosophie
   - **Réversibilité** : Non (veto définitif)

---

## ⚖️ Arbitrage des Conflits

### Procédure d'Arbitrage

**Étape 1 : Médiation Interne**
- Conflit signalé au comité de mission
- Délai : 15 jours
- Objectif : Résolution amiable

**Étape 2 : Arbitrage Technique**
- Si conflit technique : Audit par un expert indépendant
- Délai : 30 jours
- Objectif : Vérification technique de la conformité

**Étape 3 : Arbitrage Juridique**
- Si conflit juridique : Recours à un arbitre (CNUDCI)
- Délai : 60 jours
- Objectif : Décision juridique définitive

**Étape 4 : Recours Judiciaire** (Dernier recours)
- Si arbitrage insatisfaisant : Recours au tribunal compétent
- Délai : Variable
- Objectif : Décision judiciaire définitive

---

### Règles d'Arbitrage

1. **Primauté de la Raison d'Être** : Toute décision doit respecter la raison d'être
2. **Preuve Technique** : Les tests de compliance font foi
3. **Principe de Précaution** : En cas de doute, le label est retiré
4. **Transparence** : Toutes les décisions sont publiques (sauf données sensibles)

---

## 📝 Recommandations de Rédaction Statutaire

### 1. Raison d'Être (Article X)

**Texte Recommandé** :

```markdown
Article X - Raison d'Être

La société a pour raison d'être de promouvoir une économie relationnelle 
où la structure relationnelle (SAKA) prime toujours sur la structure 
instrumentale (EUR).

La société s'engage à :
1. Maintenir une séparation stricte entre SAKA (non-financier, non-monétaire, 
   non-convertible) et EUR (monnaie fiduciaire)
2. Garantir l'anti-accumulation du SAKA par le compostage obligatoire après 
   [X] jours d'inactivité
3. Assurer la circulation obligatoire du SAKA via la redistribution équitable 
   du Silo Commun
4. Ne jamais permettre de conversion SAKA ↔ EUR, ni directement ni indirectement
5. Ne jamais présenter le SAKA comme un instrument financier, une monnaie 
   électronique, ou un actif financier
6. Maintenir des tests de compliance automatiques qui vérifient la conformité 
   philosophique (tests tagués @egoejo_compliance)
7. Garantir que la CI/CD bloque toute fusion violant la philosophie EGOEJO
8. Protéger les settings critiques (compostage, redistribution) par validation 
   au démarrage (fail-fast)

Toute violation de cette raison d'être entraîne le retrait automatique du 
label "EGOEJO COMPLIANT" et peut entraîner des sanctions statutaires.
```

---

### 2. Objectifs Statutaires (Article Y)

**Texte Recommandé** :

```markdown
Article Y - Objectifs Statutaires

Les objectifs sociaux de la société sont :
1. Développer et maintenir une plateforme d'engagement citoyen conforme à 
   la philosophie EGOEJO
2. Garantir la conformité continue aux critères du label "EGOEJO COMPLIANT"
3. Documenter publiquement le statut de conformité via l'endpoint 
   /api/public/egoejo-compliance.json
4. Assurer la transparence des métriques et des scores (métadonnées obligatoires)
5. Protéger la gouvernance contre toute dérive financière ou spéculative

Ces objectifs sont incompatibles avec :
- Toute conversion SAKA ↔ EUR
- Tout rendement financier sur le SAKA
- Toute accumulation passive du SAKA
- Toute présentation du SAKA comme instrument financier ou monétaire
```

---

### 3. Comité de Mission (Article Z)

**Texte Recommandé** :

```markdown
Article Z - Comité de Mission

Le comité de mission est composé de [X] membres indépendants, dont :
- Au moins un représentant de l'association Guardian
- Au moins un expert technique (développeur senior)
- Au moins un expert juridique (avocat spécialisé)

Le comité de mission a pour mission de :
1. Vérifier que les tests de compliance passent (83/83 minimum)
2. S'assurer que le label "EGOEJO COMPLIANT" est maintenu
3. Auditer les logs de compliance (modifications directes SakaWallet, etc.)
4. Surveiller le monitoring temps réel (compostage, redistribution)
5. Recommander le retrait du label en cas de violation grave
6. Valider toute modification des tests de compliance
7. Valider toute activation de V2.0 (Investment)

Le comité de mission se réunit au moins [trimestriellement] et peut demander 
un audit technique à tout moment. Les décisions sont prises à la majorité 
simple. En cas d'égalité, la voix du représentant de l'association Guardian 
est prépondérante.
```

---

### 4. Pacte d'Associés - Golden Share (Article A)

**Texte Recommandé** :

```markdown
Article A - Golden Share (Association Guardian)

L'association Guardian détient une "golden share" qui lui confère un droit 
de veto sur toute décision violant la philosophie EGOEJO, notamment :

1. Activation de V2.0 (Investment) sans validation du comité de mission
2. Désactivation du compostage ou de la redistribution SAKA
3. Introduction d'une conversion SAKA ↔ EUR (directe ou indirecte)
4. Modification des tests de compliance sans validation du comité de mission
5. Changement de la raison d'être sans validation du comité de mission
6. Présentation du SAKA comme instrument financier ou monétaire
7. Introduction d'un rendement financier sur le SAKA

La golden share est :
- Inaliénable : Ne peut être vendue ou transférée à un tiers
- Intransmissible : Ne peut être héritée (sauf à une autre association à but non lucratif)
- Irrévocable : Ne peut être révoquée que par dissolution de l'association Guardian

En cas de violation, l'association Guardian peut :
1. Exercer son droit de veto (blocage immédiat)
2. Demander le retrait du label "EGOEJO COMPLIANT"
3. Saisir le comité de mission pour audit
4. Engager une procédure d'arbitrage
```

---

## 🔗 Correspondance Label ↔ Code

### Matrice Complète

| Critère Label | Fichier Code | Test Compliance | Clause Statutaire |
|---------------|--------------|-----------------|-------------------|
| **Séparation SAKA / EUR** | `backend/core/models/saka.py`<br>`backend/finance/models.py` | `test_no_saka_eur_conversion.py` | Raison d'être §1 |
| **Anti-Accumulation** | `backend/core/services/saka.py`<br>`backend/config/settings.py` | `test_anti_accumulation.py` | Raison d'être §2 |
| **Circulation Obligatoire** | `backend/core/services/saka.py`<br>`backend/config/celery.py` | `test_silo_redistribution.py` | Raison d'être §3 |
| **Non-Conversion** | `backend/core/services/saka.py`<br>`backend/finance/services.py` | `test_no_saka_eur_conversion.py` | Raison d'être §4 |
| **Non-Monétisation** | `frontend/frontend/src/utils/saka.ts` | `saka-protection.test.ts` | Raison d'être §5 |
| **Tests Compliance** | `backend/tests/compliance/` | `test_ci_cd_protection.py` | Raison d'être §6 |
| **CI/CD Bloquante** | `.github/workflows/egoejo-compliance.yml` | `test_ci_cd_protection.py` | Raison d'être §7 |
| **Protection Settings** | `backend/config/settings.py` | `test_settings_protection.py` | Raison d'être §8 |
| **Gouvernance** | `backend/core/api/compliance_views.py` | Audit manuel | Comité de mission |
| **Audit Logs** | `backend/core/models/saka.py`<br>`backend/core/services/saka.py` | `test_admin_protection.py` | Comité de mission |
| **Monitoring** | `backend/core/api/saka_metrics_views.py` | Audit manuel | Comité de mission |

---

## 📚 Références Juridiques

### Textes Applicables

1. **Code de commerce** : Article L210-10 (SAS à mission)
2. **Loi PACTE** : Article 1835 du Code civil (raison d'être)
3. **Loi 1901** : Association Guardian (protection de la mission)
4. **Règlement Général sur la Protection des Données (RGPD)** : Transparence des métriques

### Jurisprudence

- **Arrêt Cour de cassation** : Primauté de la raison d'être sur les intérêts financiers
- **Décision AMF** : Distinction instruments financiers / monnaies électroniques
- **Directive DSP2** : Exclusion des monnaies non-fiduciaires

---

## ✅ Checklist de Conformité Juridique

### Statuts

- [ ] Raison d'être définie (Article X)
- [ ] Objectifs statutaires compatibles (Article Y)
- [ ] Comité de mission constitué (Article Z)
- [ ] Golden share définie (Article A)

### Pacte d'Associés

- [ ] Golden share inaliénable
- [ ] Droit de veto défini
- [ ] Procédure d'arbitrage prévue

### Code

- [ ] Tests de compliance automatiques
- [ ] CI/CD bloquante
- [ ] Settings critiques protégés
- [ ] Endpoint public de vérification

### Documentation

- [ ] Manifeste SAKA/EUR publié
- [ ] Label EGOEJO COMPLIANT documenté
- [ ] Procédure de retrait documentée

---

**Fin du Document Juridique-Technique**

*Dernière mise à jour : 2025-01-27*

