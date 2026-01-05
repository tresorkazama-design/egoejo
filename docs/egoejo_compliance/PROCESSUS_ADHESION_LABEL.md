# 📋 Processus d'Adhésion au Label "EGOEJO COMPLIANT"

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Document Public - Projets Tiers

---

## 🎯 Objectif

Ce document définit le processus d'adhésion au label **"EGOEJO COMPLIANT"** pour les projets tiers (non-EGOEJO).

Le label est **ouvert** à tout projet respectant les principes philosophiques, techniques et structurels d'EGOEJO, sans dépendance à l'entreprise EGOEJO.

---

## 📊 Vue d'Ensemble du Processus

```
1. Auto-déclaration
   ↓
2. Audit Technique (automatique)
   ↓
3. Audit Philosophique (manuel)
   ↓
4. Décision du Comité
   ↓
5. Attribution du Label
   ↓
6. Surveillance Continue
```

---

## 🔄 Étape 1 : Auto-Déclaration

### 1.1 Formulaire d'Auto-Déclaration

Le projet candidat doit remplir un formulaire d'auto-déclaration incluant :

**Informations Générales** :
- Nom du projet
- URL du dépôt Git
- Description du projet
- Contact responsable

**Conformité Technique** :
- ✅ Tests de compliance automatiques présents
- ✅ CI/CD bloquante configurée
- ✅ Settings critiques protégés
- ✅ Endpoint public de vérification (`/api/public/egoejo-compliance.json`)

**Conformité Philosophique** :
- ✅ Séparation stricte SAKA / EUR (ou équivalent)
- ✅ Anti-accumulation (compostage ou mécanisme équivalent)
- ✅ Circulation obligatoire (redistribution ou mécanisme équivalent)
- ✅ Non-monétisation (aucune conversion possible)

**Documentation** :
- ✅ Manifeste philosophique publié
- ✅ Documentation technique complète
- ✅ README avec badge EGOEJO COMPLIANT

### 1.2 Soumission

**Formulaire** : [À créer : formulaire en ligne ou GitHub Issue]

**Délai de traitement** : 30 jours ouvrés

**Frais** : Gratuit (label ouvert et non-commercial)

---

## 🔍 Étape 2 : Audit Technique (Automatique)

### 2.1 Vérifications Automatiques

Le comité du label exécute automatiquement :

**Tests de Compliance** :
```bash
# Exécution des tests de compliance du projet candidat
pytest -m egoejo_compliance -v --tb=short
```

**Vérification CI/CD** :
- Workflow GitHub Actions présent
- Workflow bloque si tests échouent
- Tests tagués `@egoejo_compliance`

**Vérification Code** :
- Scan automatique pour détecter :
  - Fonctions de conversion SAKA ↔ EUR
  - Désactivation du compostage
  - Contournement des tests

**Vérification Endpoint** :
- Endpoint `/api/public/egoejo-compliance.json` accessible
- Réponse JSON conforme au schéma
- Statut de conformité à jour

### 2.2 Critères de Validation Technique

**Minimum Requis** :
- ✅ 80% des tests de compliance passent (minimum)
- ✅ CI/CD bloquante active
- ✅ Settings critiques protégés
- ✅ Endpoint public fonctionnel

**Recommandé** :
- ✅ 100% des tests de compliance passent
- ✅ Documentation complète
- ✅ Monitoring temps réel

### 2.3 Rapport d'Audit Technique

Le comité génère un rapport d'audit technique incluant :

- Résultats des tests (passés/échoués)
- Points de conformité validés
- Points de non-conformité identifiés
- Recommandations d'amélioration

**Délai** : 7 jours ouvrés après soumission

---

## 🧠 Étape 3 : Audit Philosophique (Manuel)

### 3.1 Vérifications Philosophiques

Le comité du label effectue un audit philosophique manuel :

**Séparation SAKA / EUR** :
- ✅ Aucune conversion possible (vérifié dans le code)
- ✅ Modèles séparés (pas de ForeignKey directe)
- ✅ Services séparés (pas d'import croisé)
- ✅ Affichage non-monétaire (grains, pas €)

**Anti-Accumulation** :
- ✅ Compostage obligatoire (ou mécanisme équivalent)
- ✅ Redistribution équitable (ou mécanisme équivalent)
- ✅ Limites quotidiennes respectées
- ✅ Aucune accumulation passive possible

**Circulation Obligatoire** :
- ✅ Redistribution du Silo Commun (ou équivalent)
- ✅ Aucune thésaurisation possible
- ✅ Mécanisme de circulation actif

**Non-Monétisation** :
- ✅ Aucun rendement financier
- ✅ Aucun affichage monétaire
- ✅ Documentation explicite (non-financier, non-monétaire)

### 3.2 Entretien avec le Projet

Le comité organise un entretien (visioconférence) avec le projet candidat :

**Objectifs** :
- Comprendre la philosophie du projet
- Vérifier la compréhension des principes EGOEJO
- Clarifier les adaptations locales
- Valider l'engagement à long terme

**Durée** : 1-2 heures

**Participants** :
- Représentants du projet candidat
- Membres du comité du label
- Expert technique (optionnel)

### 3.3 Rapport d'Audit Philosophique

Le comité génère un rapport d'audit philosophique incluant :

- Évaluation de la conformité philosophique
- Points forts identifiés
- Points d'attention
- Recommandations d'amélioration

**Délai** : 14 jours ouvrés après audit technique

---

## ⚖️ Étape 4 : Décision du Comité

### 4.1 Comité du Label

**Composition** :
- 3-5 membres indépendants
- Au moins un représentant de l'association Guardian
- Au moins un expert technique
- Au moins un expert philosophique

**Règles de Décision** :
- **Majorité simple** pour l'attribution du label
- **Unanimité** pour le retrait du label
- **Veto** de l'association Guardian possible

### 4.2 Critères de Décision

**Attribution du Label** :
- ✅ Audit technique : 80% minimum des tests passent
- ✅ Audit philosophique : Conformité validée
- ✅ Engagement du projet : Charte signée
- ✅ Documentation : Complète et publique

**Refus du Label** :
- ❌ Audit technique : < 80% des tests passent
- ❌ Audit philosophique : Non-conformité majeure
- ❌ Engagement manquant : Charte non signée
- ❌ Documentation insuffisante

### 4.3 Notification

**Délai** : 7 jours ouvrés après décision

**Contenu** :
- Décision (attribution ou refus)
- Justification détaillée
- Recommandations d'amélioration (si refus)
- Prochaines étapes (si attribution)

---

## 🏅 Étape 5 : Attribution du Label

### 5.1 Conditions d'Attribution

Le label est attribué si :

1. ✅ Audit technique validé (80% minimum)
2. ✅ Audit philosophique validé
3. ✅ Charte des projets labellisés signée
4. ✅ Badge SVG intégré au README
5. ✅ Endpoint public configuré

### 5.2 Niveaux de Label

**EGOEJO Compliant - Core** :
- Tous les critères Core validés
- 80-99% des tests passent
- Conformité philosophique validée

**EGOEJO Compliant - Extended** :
- Tous les critères Core + Extended validés
- 100% des tests passent
- Gouvernance protectrice active
- Monitoring temps réel

### 5.3 Badge et Documentation

**Badge SVG** :
- Fourni par le comité du label
- Intégration au README obligatoire
- Lien vers l'endpoint de vérification

**Documentation** :
- Liste publique des projets labellisés
- Statut de conformité mis à jour
- Date d'attribution et date d'expiration

---

## 🔄 Étape 6 : Surveillance Continue

### 6.1 Vérifications Périodiques

**Fréquence** : Trimestrielle

**Vérifications** :
- Exécution automatique des tests de compliance
- Vérification de l'endpoint public
- Scan du code pour violations
- Audit des logs de compliance

### 6.2 Rapport de Surveillance

Le comité génère un rapport trimestriel incluant :

- Statut de conformité (maintenu / à risque / non-conforme)
- Évolution des tests (amélioration / dégradation)
- Points d'attention identifiés
- Recommandations d'amélioration

### 6.3 Conditions de Maintien

Le label est maintenu si :

- ✅ Tests de compliance : 80% minimum passent
- ✅ Endpoint public : Fonctionnel et à jour
- ✅ Conformité philosophique : Maintenue
- ✅ Charte respectée : Engagements tenus

---

## 🚫 Conditions de Retrait

### Retrait Automatique

Le label est **automatiquement retiré** si :

1. ❌ Tests de compliance : < 80% passent (pendant 30 jours)
2. ❌ Endpoint public : Non accessible (pendant 7 jours)
3. ❌ Conversion SAKA ↔ EUR : Détectée dans le code
4. ❌ Compostage désactivé : En production

### Retrait par Décision du Comité

Le comité peut **recommander le retrait** si :

1. ⚠️ Violation grave de la charte
2. ⚠️ Non-respect des engagements
3. ⚠️ Dégradation continue de la conformité
4. ⚠️ Refus de collaboration avec le comité

**Procédure** :
1. Notification au projet (délai 30 jours)
2. Délai de correction
3. Décision finale du comité
4. Retrait du label et publication

---

## 📝 Formulaire d'Auto-Déclaration

### Template GitHub Issue

```markdown
# Demande d'Adhésion au Label "EGOEJO COMPLIANT"

## Informations Générales

- **Nom du projet** : [Nom]
- **URL du dépôt Git** : [URL]
- **Description** : [Description]
- **Contact responsable** : [Email]

## Conformité Technique

- [ ] Tests de compliance automatiques présents
- [ ] CI/CD bloquante configurée
- [ ] Settings critiques protégés
- [ ] Endpoint public de vérification (`/api/public/egoejo-compliance.json`)

## Conformité Philosophique

- [ ] Séparation stricte SAKA / EUR (ou équivalent)
- [ ] Anti-accumulation (compostage ou mécanisme équivalent)
- [ ] Circulation obligatoire (redistribution ou mécanisme équivalent)
- [ ] Non-monétisation (aucune conversion possible)

## Documentation

- [ ] Manifeste philosophique publié
- [ ] Documentation technique complète
- [ ] README avec badge EGOEJO COMPLIANT (à ajouter après attribution)

## Engagements

- [ ] Charte des projets labellisés acceptée
- [ ] Surveillance continue acceptée
- [ ] Transparence acceptée
```

---

## 🔗 Liens Utiles

- [Charte des Projets Labellisés](CHARTE_PROJETS_LABELLISES.md)
- [Gouvernance du Label](GOUVERNANCE_LABEL.md)
- [Label EGOEJO COMPLIANT](LABEL_EGOEJO_COMPLIANT.md)
- [Clarifications Interdictions vs Adaptations](CLARIFICATIONS_LABEL.md)

---

**Fin du Processus d'Adhésion**

*Dernière mise à jour : 2025-01-27*

