# Clauses Constitutionnelles EGOEJO - Documentation Juridique

**Date** : 2025-12-19  
**Statut** : Textes juridiques à valider par avocat

---

## 📋 Vue d'Ensemble

Ce dossier contient les clauses constitutionnelles EGOEJO destinées à être intégrées dans :
- Le **Pacte d'Associés** de la SAS EGOEJO
- Les **Statuts SAS à Mission**
- Les **Conditions Générales d'Utilisation (CGU)** de la plateforme

---

## 📄 Documents Inclus

### 1. Clause Golden Share (Action G)

**Fichier** : `CLAUSE_GOLDEN_SHARE_ACTION_G.md`

**Contenu** :
- Détenteur : Association EGOEJO Guardian
- Veto absolu sur :
  - Modifications de l'algorithme de compostage SAKA
  - Convertibilité SAKA/EUR
  - Activation de la Version 2.0 sans vote conforme

**Usage** : À intégrer dans le Pacte d'Associés et les Statuts

---

### 2. Clause de Subordination - SAKA et Compostage

**Fichier** : `CLAUSE_SUBORDINATION_SAKA_COMPOSTAGE.md`

**Contenu** :
- Définition juridique du SAKA comme "unité de compte de réputation non-monétaire"
- Caractéristiques juridiques (non-monétarité, non-négociabilité, non-garantie)
- Droit au Compostage (dépréciation automatique)
- Acceptation et renonciation aux recours

**Usage** : À intégrer dans les CGU et les Statuts

---

## 🎯 Objectifs des Clauses

### Protection Constitutionnelle

Les clauses visent à protéger la **double structure économique non-négociable** EGOEJO :

1. **Structure Relationnelle SAKA** (Souveraine, Prioritaire)
   - Engagement, don, réputation
   - Cycle : Récolte → Usage → Compost → Silo → Redistribution
   - Anti-accumulation absolue

2. **Structure Instrumentale EUR** (Subordonnée, Dormante)
   - Finance, paiement, conformité
   - Ne doit JAMAIS contraindre ou corrompre le SAKA

### Garanties Juridiques

- ✅ **Veto absolu** sur les modifications critiques (Action G)
- ✅ **Définition juridique** du SAKA (non-monétaire)
- ✅ **Acceptation contractuelle** du compostage
- ✅ **Renonciation aux recours** en cas de dépréciation
- ✅ **Interdiction** de convertibilité SAKA/EUR

---

## ⚖️ Validation Juridique Requise

### Points à Valider par un Avocat

#### Pour la Clause Golden Share :

1. **Conformité avec le droit des sociétés**
   - Code de commerce (articles L225-1 et suivants)
   - Validité de l'Action G (Golden Share)
   - Irrévocabilité de la clause

2. **Modalités de veto**
   - Délais de notification et d'exercice
   - Forme de la décision de veto
   - Irrévocabilité du veto

3. **Sanctions**
   - Nullité de la décision
   - Indemnité forfaitaire
   - Possibilité de dissolution

4. **Définitions techniques**
   - Algorithme de compostage
   - Convertibilité SAKA/EUR
   - Version 2.0

---

#### Pour la Clause de Subordination :

1. **Nature juridique du SAKA**
   - Qualification d'"unité de compte de réputation non-monétaire"
   - Exclusion de la réglementation financière (AMF, Banque de France)
   - Non-qualification comme instrument financier

2. **Renonciation aux recours**
   - Validité de la renonciation (faute lourde, dol)
   - Conformité avec le droit de la consommation
   - Clauses abusives

3. **Droit au Compostage**
   - Acceptation contractuelle
   - Information du consommateur (RGPD)
   - Notification du compostage

4. **Sanctions**
   - Résiliation du compte
   - Perte du solde SAKA
   - Indemnité forfaitaire

---

## 📝 Instructions pour l'Avocat

### 1. Révision des Textes

- Vérifier la conformité avec le droit français
- Adapter les formulations selon les pratiques usuelles
- Préciser les références légales

### 2. Complétion des Éléments Manquants

Les textes contiennent des placeholders à compléter :
- `[X]` : Numéros d'articles
- `[Y]` : Références à d'autres articles
- `[ville, département]` : Compétence territoriale
- `[date]` : Date de signature
- `[montant]` : Montants d'indemnité
- `[X] jours` : Délais

### 3. Intégration dans les Documents

- **Pacte d'Associés** : Intégrer la Clause Golden Share
- **Statuts SAS à Mission** : Intégrer les deux clauses
- **CGU** : Intégrer la Clause de Subordination

### 4. Vérification Technique

- Références aux variables de configuration SAKA
- Références aux fonctions techniques
- Cohérence avec le code source

---

## 🔗 Références Techniques

### Code Source

- **Algorithme de compostage** : `backend/core/services/saka.py` (fonction `run_saka_compost_cycle()`)
- **Configuration SAKA** : `backend/config/settings.py` (variables `SAKA_*`)
- **Modèles SAKA** : `backend/core/models/saka.py`

### Documentation

- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Guardian Script** : `docs/architecture/GUARDIAN_EGOEJO_REFERENCE.md`
- **Workflow CI** : `docs/architecture/WORKFLOW_CI_CONFORMITE_EGOEJO.md`

---

## ✅ Checklist de Validation

Avant transmission à l'avocat :

- [x] Clause Golden Share rédigée
- [x] Clause de Subordination rédigée
- [x] Définitions techniques incluses
- [x] Notes pour l'avocat ajoutées
- [x] Placeholders identifiés
- [ ] Références techniques vérifiées
- [ ] Cohérence avec le code source vérifiée

Après validation par l'avocat :

- [ ] Textes validés juridiquement
- [ ] Placeholders complétés
- [ ] Intégration dans Pacte d'Associés
- [ ] Intégration dans Statuts
- [ ] Intégration dans CGU
- [ ] Signature des documents

---

## 📞 Contact

Pour toute question technique sur les clauses :
- **Architecture** : Voir `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Code Source** : Voir `backend/core/services/saka.py`
- **Tests** : Voir `backend/core/tests_saka_philosophy.py`

---

*Document généré le : 2025-12-19*  
*À compléter et valider par un avocat spécialisé*

