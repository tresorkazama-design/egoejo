# EGOEJO – Pitch pour États & Collectivités

**Version** : 3.0  
**Date** : 2025-01-27  
**Statut** : Document Officiel  
**Public Cible** : États, Collectivités territoriales, Institutions publiques  
**Pages** : 1-2 pages

---

## Résumé Exécutif

**EGOEJO** est une plateforme numérique dédiée à la régénération du vivant qui relie des citoyens à des projets sociaux à fort impact écologique et social. La plateforme opère selon un modèle de gouvernance hybride unique, combinant une structure relationnelle (SAKA, unité d'engagement interne) et une structure instrumentale (EUR, monnaie réelle), strictement séparées et protégées par des mécanismes techniques et juridiques opposables.

### Objectif Principal

Faciliter la découverte, la participation et le financement de projets régénératifs locaux (refuges, jardins nourriciers, ateliers de transmission, résidences de recherche-action) via une plateforme transparente, traçable, et conforme aux principes de gouvernance des communs.

---

## Mise en Œuvre

### Infrastructure Technique

- **Frontend** : Application web responsive (React, Vite)
- **Backend** : API REST (Django REST Framework)
- **Base de données** : PostgreSQL (données structurées, traçabilité)
- **Stockage média** : Stockage objet (S3-compatible, Cloudflare R2)
- **Paiement** : Stripe (paiement sécurisé, conformité PCI-DSS)

### Fonctionnalités Principales

1. **Référencement de projets** : Catalogue de projets locaux avec filtres, recherche, géolocalisation
2. **Collecte de fonds** : Cagnottes transparentes, traçabilité totale, 100% des dons nets (après frais de plateforme) alloués aux projets
3. **Engagement citoyen** : Système SAKA pour reconnaître et valoriser la participation (non-financier, non-monétaire)
4. **Gouvernance participative** : Votes, sondages, décisions collectives via méthodes démocratiques vérifiables
5. **Partage de contenus** : Ressources documentaires, guides pratiques, vidéos pédagogiques

### Déploiement

- **Hébergement** : Cloud (Vercel frontend, Railway backend)
- **CI/CD** : GitHub Actions (tests automatiques, déploiement conditionnel)
- **Monitoring** : Sentry (erreurs, performance), logs structurés
- **Sécurité** : Conformité RGPD, chiffrement, audit logs

---

## Conformité

### Conformité Technique

- **Tests automatiques** : Suite de tests bloquants vérifiant l'absence de conversion SAKA ↔ EUR
- **CI/CD protectrice** : Toute violation bloque automatiquement les déploiements
- **Audit logs** : Toutes les actions critiques sont tracées, horodatées, et auditées
- **Label public** : Certification "EGOEJO Compliant" vérifiable par des tiers

### Conformité Juridique

- **RGPD** : Conformité totale (consentement, droit à l'oubli, export des données)
- **Séparation SAKA/EUR** : Aucune conversion possible, tests automatiques bloquants
- **Transparence financière** : 100% des dons nets (après frais de plateforme) alloués aux projets, frais transparents
- **Gouvernance protectrice** : Conseil d'administration, comité de mission, review obligatoire

### Conformité Éditoriale

- **Contenu public = published uniquement** : Seuls les contenus avec le statut "published" sont accessibles publiquement
- **Source et licence obligatoires** : Tous les contenus publics doivent avoir une source et une licence explicites
- **Interdiction de promesses financières** : Aucun contenu ne peut promettre de rendement, de rente, ou de conversion SAKA ↔ EUR

---

## Partenariats Possibles

### Partenariats Territoriaux

- **Collectivités territoriales** : Mise en réseau de projets locaux, financement participatif, accompagnement technique
- **Associations locales** : Référencement de projets, accompagnement technique, formation

### Partenariats Institutionnels

- **Institutions publiques** : Reconnaissance, financement, déploiement à l'échelle territoriale
- **Fondations** : Financement, reconnaissance, label "EGOEJO Compliant"

---

## Garanties & Engagements

### Garanties Techniques

- **Séparation SAKA/EUR** : Encodée dans le code source, testée automatiquement, non négociable
- **Anti-accumulation** : Mécanisme de compostage obligatoire et redistribution équitable
- **Transparence totale** : Endpoints publics de vérification, documentation complète, traçabilité totale

### Engagements Institutionnels

- **Gouvernance protectrice** : Conseil d'administration, comité de mission, review obligatoire
- **Conformité continue** : Tests automatiques, audit régulier, label public vérifiable
- **Transparence financière** : 100% des dons nets (après frais de plateforme) alloués aux projets, frais transparents

---

## Contact & Documentation

- **Documentation technique** : `docs/architecture/`
- **Label EGOEJO Compliant** : `docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md`
- **Endpoints publics** : `/api/public/egoejo-compliance.json`, `/api/public/egoejo-compliance-badge.svg`
- **Dernière mise à jour** : 2025-01-27

---

**Document généré le** : 2025-01-27  
**Version** : 3.0  
**Statut** : Document Officiel
