# EGOEJO – Dossier Institutionnel ONU & Fondations

**Version** : 1.0  
**Date** : 2025-01-05  
**Statut** : Document Officiel  
**Public Cible** : Organisations Internationales (ONU, UNESCO), Fondations, Institutions Publiques  
**Langue** : Français  
**Pages** : 15-20  
**Style** : Technocratique, orienté ODD, sans vocabulaire New Age ou spirituel

---

## Table des Matières

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Solution Architecture](#3-solution-architecture)
4. [Governance Framework](#4-governance-framework)
5. [Legal Trajectory](#5-legal-trajectory)
6. [Alignment with SDGs](#6-alignment-with-sustainable-development-goals)
7. [Annexes](#7-annexes)

---

## 1. Executive Summary

**EGOEJO** est une infrastructure numérique de subsistance (Digital Subsistence Infrastructure) conçue pour soutenir des programmes régénératifs locaux tout en préservant l'autonomie des communautés vis-à-vis des marchés financiers.

### Positionnement Institutionnel

EGOEJO opère comme une **infrastructure de subsistance numérique** permettant :

- La **découverte et la participation** à des programmes régénératifs locaux (refuges, jardins nourriciers, ateliers de transmission, résidences de recherche-action)
- La **collecte de fonds transparente** avec traçabilité totale (100% des dons nets après frais de plateforme alloués aux programmes)
- La **reconnaissance de l'engagement citoyen** via un système interne non-financier et non-monétaire
- La **protection contre la capture** par des mécanismes techniques opposables encodés dans le code source

### Contribution aux Objectifs de Développement Durable (ODD)

EGOEJO contribue directement aux ODD suivants :

- **ODD 11** (Villes et communautés durables) : Facilitation de projets locaux régénératifs
- **ODD 15** (Vie terrestre) : Soutien à la régénération du vivant
- **ODD 17** (Partenariats pour la réalisation des objectifs) : Infrastructure de gouvernance des communs
- **ODD 2** (Faim zéro) : Soutien aux jardins nourriciers et systèmes alimentaires locaux

### Impact Mesurable

- **Court terme (12 mois)** : 50-100 programmes locaux référencés, 500-1000 utilisateurs actifs, 50 000-100 000 € collectés (nets après frais de plateforme)
- **Moyen terme (3 ans)** : Réseau de 200-500 programmes, 5000-10000 utilisateurs, 500 000-1 000 000 € collectés (nets après frais de plateforme)
- **Long terme (5-10 ans)** : Modèle réplicable, adoption par des projets tiers, impact mesurable sur la régénération du vivant

---

## 2. Problem Statement

### Extraction de Valeur et Dépendance aux Marchés Financiers

Les programmes régénératifs locaux rencontrent trois obstacles structurels :

#### 2.1. Extraction de Valeur par les Plateformes

Les plateformes numériques existantes appliquent des commissions élevées (15-30%) qui réduisent l'impact réel des dons. Cette extraction de valeur limite la capacité des programmes à fonctionner de manière autonome.

#### 2.2. Dépendance aux Marchés Financiers

Les mécanismes de financement traditionnels (subventions, investissements) créent une dépendance structurelle aux cycles économiques et aux priorités politiques, compromettant la pérennité des programmes.

#### 2.3. Absence de Reconnaissance de l'Engagement Relationnel

L'engagement citoyen (participation bénévole, transmission de savoirs, soin du vivant) n'est pas reconnu ni valorisé par les systèmes de mesure existants, réduisant l'incitation à la participation.

### Conséquences Observées

- **Fragmentation** : Projets isolés, difficultés de coordination
- **Instabilité financière** : Dépendance aux subventions ponctuelles
- **Dévalorisation du care** : Engagement relationnel non reconnu
- **Capture institutionnelle** : Dépendance aux bailleurs de fonds

---

## 3. Solution Architecture

### 3.1. Double Structure Protégée

EGOEJO opère selon une **double structure strictement séparée** :

#### Structure Instrumentale (EUR)

- **Fonction** : Financement des infrastructures et des opérations
- **Unité** : Euro (monnaie réelle)
- **Usage** : Dons, collecte de fonds, paiements
- **Gestion** : Stripe (paiement sécurisé, conformité PCI-DSS)
- **Allocation** : 100% des dons nets (après frais de plateforme) alloués aux programmes

#### Structure Relationnelle (SAKA)

- **Fonction** : Reconnaissance de l'engagement relationnel et du care
- **Unité** : SAKA (unité d'engagement interne, non-financière, non-monétaire)
- **Usage** : Participation aux projets, votes, gouvernance, soutien symbolique
- **Caractéristiques** :
  - Non convertible en EUR (séparation technique opposable)
  - Cycle obligatoire : semis → usage → compostage → redistribution
  - Anti-accumulation : mécanisme de compostage automatique

### 3.2. Séparation Technique Opposable

La séparation entre structures est **encodée dans le code source** et **testée automatiquement en continu** :

- **Tests bloquants** : Suite de tests vérifiant l'absence de conversion SAKA ↔ EUR
- **CI/CD protectrice** : Toute violation bloque automatiquement les déploiements
- **Vérification publique** : Endpoint `/api/public/egoejo-constitution.json` exposant le statut de conformité en temps réel

### 3.3. Transparence Financière

- **100% des dons nets** (après frais de plateforme) alloués aux programmes
- **Frais transparents** : Frais de plateforme explicitement mentionnés (Stripe : ~3%, frais de gestion : à définir)
- **Traçabilité totale** : Chaque euro est traçable de l'utilisateur au programme

---

## 4. Governance Framework

### 4.1. Constitution Opposable (Enforceable Constitution)

La gouvernance EGOEJO est encodée dans une **Constitution technique opposable** :

#### Principes Constitutionnels

1. **Séparation SAKA/EUR** : Aucune conversion possible, tests automatiques bloquants
2. **Anti-Accumulation** : Compostage obligatoire du SAKA inactif
3. **Transparence** : 100% des dons nets alloués aux programmes
4. **Non-Capture** : Mécanismes techniques empêchant la capture par des intérêts privés

#### Mécanisme d'Opposabilité

- **Encodage dans le code source** : Principes constitutionnels traduits en règles techniques
- **Tests automatiques bloquants** : Vérification continue de la conformité
- **CI/CD protectrice** : Déploiement bloqué en cas de violation
- **Badge public de conformité** : Statut de conformité exposé publiquement (`/api/public/egoejo-constitution.json`)

### 4.2. Mécanisme de Non-Dérive

Le système de non-dérive garantit la détection et la notification automatique de toute violation des principes constitutionnels :

- **Déclencheurs automatiques** : Détection en temps réel des violations (contournement, modification massive, incohérence)
- **Notification multi-canaux** : Email + Webhook (optionnel) pour alertes critiques
- **Traçabilité** : Enregistrement automatique dans `CriticalAlertEvent` pour audit
- **Auditabilité** : Export mensuel des alertes via commande management `alerts_report`

### 4.3. Gouvernance Organisationnelle

- **Conseil d'administration** : Décisions stratégiques, validation des modifications critiques
- **Comité de mission** : Veille sur la conformité aux principes constitutionnels
- **Review obligatoire** : Toute modification critique nécessite une validation
- **Formation continue** : Équipe formée aux principes constitutionnels

---

## 5. Legal Trajectory

### 5.1. Trajectoire Juridique Prévisionnelle

EGOEJO suit une trajectoire juridique progressive permettant une évolution institutionnelle adaptée :

#### Phase 1 : Association (Actuel)

- **Statut** : Association loi 1901 (ou équivalent selon juridiction)
- **Avantages** : Simplicité administrative, flexibilité opérationnelle
- **Limites** : Capacité de financement limitée, dépendance aux subventions

#### Phase 2 : Fonds de Dotation (Moyen terme)

- **Statut** : Fonds de dotation (France) ou équivalent (fondation non-reconnue d'utilité publique)
- **Avantages** : Capacité de recevoir des dons, gestion patrimoniale, pérennité
- **Conditions** : Capital initial, gouvernance structurée, conformité réglementaire

#### Phase 3 : Fondation Abritée (Long terme)

- **Statut** : Fondation abritée sous égide d'une fondation reconnue d'utilité publique
- **Avantages** : Capacité de financement maximale, crédibilité institutionnelle, avantages fiscaux
- **Conditions** : Partenariat avec fondation reconnue, conformité aux exigences de l'égide

### 5.2. Qualification Juridique du SAKA

Le **SAKA** (unité d'engagement interne) fait l'objet d'une qualification juridique explicite :

- **Unité de compte interne non-monétaire** : Destinée exclusivement à la mesure de l'engagement relationnel
- **Non-fongibilité financière** : N'est ni une monnaie électronique, ni un actif numérique (PSAN), ni un titre financier
- **Incessibilité** : Incessible entre tiers hors des mécanismes protocolaires (don, vote, redistribution)

**Objectif** : Éviter toute interprétation erronée comme crypto-actif, token financier, ou instrument financier par les régulateurs.

### 5.3. Conformité Réglementaire

- **Conformité financière** : Séparation SAKA/EUR, transparence financière, conformité PCI-DSS (Stripe)
- **Conformité données (RGPD)** : Consentement explicite, droit à l'oubli, export des données, sécurité des données
- **Conformité publicité** : Aucune promesse financière, transparence des frais, conformité éditoriale

---

## 6. Alignment with Sustainable Development Goals

### Contribution Directe aux ODD

#### ODD 11 : Villes et Communautés Durables

- **Cible 11.3** : Urbanisation inclusive et durable
- **Contribution EGOEJO** : Facilitation de projets locaux régénératifs (refuges, jardins nourriciers, ateliers de transmission)

#### ODD 15 : Vie Terrestre

- **Cible 15.1** : Conservation et restauration des écosystèmes
- **Contribution EGOEJO** : Soutien à la régénération du vivant via projets locaux

#### ODD 17 : Partenariats pour la Réalisation des Objectifs

- **Cible 17.16** : Renforcement du Partenariat mondial pour le développement durable
- **Contribution EGOEJO** : Infrastructure de gouvernance des communs, modèle réplicable

#### ODD 2 : Faim Zéro

- **Cible 2.4** : Systèmes de production alimentaire durables
- **Contribution EGOEJO** : Soutien aux jardins nourriciers et systèmes alimentaires locaux

### Indicateurs de Contribution

- **Nombre de programmes régénératifs référencés** : Objectif 50-100 (12 mois), 200-500 (3 ans)
- **Montants collectés (nets)** : Objectif 50 000-100 000 € (12 mois), 500 000-1 000 000 € (3 ans)
- **Utilisateurs actifs** : Objectif 500-1000 (12 mois), 5000-10000 (3 ans)

---

## 7. Annexes

### Annexe A : Proof of Governance (Badge Public de Conformité)

#### Endpoint Public de Vérification

**URL** : `https://egoejo.org/api/public/egoejo-constitution.json`

**Format de Réponse** :
```json
{
  "status": "compliant",
  "version": "1.0.0",
  "last_check": "2025-01-03T10:00:00Z",
  "checks": {
    "saka_separation": true,
    "anti_accumulation": true,
    "no_monetary_symbols": true,
    "editorial_compliance": true
  },
  "proof_hash": "a1b2c3d4e5f6g7h8"
}
```

#### Badge SVG Dynamique

**URL** : `https://egoejo.org/api/public/egoejo-constitution.svg`

**États Visuels** :
- **Vert** : Conforme (compliant)
- **Rouge** : Non conforme (non-compliant)
- **Orange** : Statut inconnu (unknown)

**Sécurité** : Le badge ne renvoie jamais "compliant" si :
- Le rapport de conformité est absent
- La signature HMAC-SHA256 est invalide
- Le rapport est vieux de > 24h

#### Génération Automatique

Le rapport de conformité est généré automatiquement par CI/CD après tous les tests réussis :
- **Workflow** : `.github/workflows/audit-global.yml`
- **Script** : `scripts/generate_compliance_report.py`
- **Signature** : HMAC-SHA256 avec clé secrète (`COMPLIANCE_SIGNATURE_SECRET`)

### Annexe B : Anti-Capture Clause

#### Principes Anti-Capture

La Constitution EGOEJO inclut des mécanismes techniques empêchant la capture par des intérêts privés :

1. **Séparation SAKA/EUR** : Aucune conversion possible, empêchant la monétisation du SAKA
2. **Anti-Accumulation** : Compostage obligatoire, empêchant l'accumulation passive
3. **Tests bloquants** : Toute violation bloque automatiquement les déploiements
4. **Transparence** : 100% des dons nets alloués aux programmes, frais transparents

#### Mécanismes Techniques

- **Code source ouvert** : Vérification possible par des tiers
- **Tests automatiques** : Vérification continue de la conformité
- **Badge public** : Statut de conformité exposé publiquement
- **Audit logs** : Traçabilité totale des actions critiques

#### Protection Contre la Capture

- **Aucune conversion SAKA ↔ EUR** : Empêche la spéculation sur le SAKA
- **Compostage obligatoire** : Empêche l'accumulation passive
- **Transparence financière** : Empêche l'extraction de valeur cachée
- **Gouvernance opposable** : Empêche la modification unilatérale des principes

### Annexe C : Références Techniques

#### Endpoints Publics

- `/api/public/egoejo-constitution.json` : Statut de conformité constitutionnelle
- `/api/public/egoejo-constitution.svg` : Badge SVG de conformité
- `/api/compliance/integrity/saka/` : Vérification d'intégrité SAKA (admin)

#### Commandes Management

- `python manage.py alerts_report --month YYYY-MM` : Rapport mensuel des alertes critiques

#### Documentation

- `docs/security/ALERTING_EMAIL.md` : Système d'alerte email
- `docs/security/ALERTING_WEBHOOK.md` : Système d'alerte webhook
- `docs/observability/ALERTS_METRICS.md` : Métriques et observabilité
- `docs/institutionnel/PROCEDURES_AUDIT_EXTERNE.md` : Procédures d'audit externe

---

**Document généré le** : 2025-01-05  
**Version** : 1.0  
**Statut** : Document Officiel  
**Contact** : [À compléter]  
**Structure** : Ghisi Institutionnelle (Executive Summary, Problem, Solution, Governance, Legal Trajectory, Annexes)

