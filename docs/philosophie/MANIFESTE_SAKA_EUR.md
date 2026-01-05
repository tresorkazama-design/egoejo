# 🛡️ MANIFESTE PHILOSOPHIQUE EGOEJO
## Définition Explicite de la Séparation SAKA/EUR

**Date** : 2025-01-27  
**Version** : 1.0  
**Statut** : Document Fondateur Non Négociable

---

## PRINCIPE FONDAMENTAL

**La structure relationnelle (SAKA) prime toujours sur la structure instrumentale (EUR).**

Le SAKA est une **monnaie interne d'engagement** (Yin), strictement séparée de l'Euro (Yang).

---

## DÉFINITIONS EXPLICITES

### SAKA (Structure Relationnelle)

- **Nature** : Monnaie interne d'engagement, non-financière, non-monétaire
- **Unité** : Grains SAKA (entiers positifs)
- **Usage** : Boost de projets, votes, engagement communautaire
- **Caractéristiques** :
  - Aucune conversion SAKA ↔ EUR autorisée
  - Aucun rendement financier
  - Compostage obligatoire (anti-accumulation)
  - Redistribution du Silo Commun (circulation obligatoire)

### EUR (Structure Instrumentale)

- **Nature** : Monnaie réelle, instrumentale
- **Unité** : Euros (décimales à 2 chiffres)
- **Usage** : Dons, investissements (V2.0 dormant)
- **Caractéristiques** :
  - Gestion financière classique
  - Transactions via Stripe
  - Escrow pour sécurisation

---

## RÈGLES ABSOLUES (NON NÉGOCIABLES)

1. **Aucune conversion SAKA ↔ EUR** : Aucune fonction, aucun endpoint, aucun mécanisme ne peut convertir SAKA en EUR ou vice versa.

2. **Aucun affichage monétaire du SAKA** : Le SAKA ne doit jamais être affiché comme une monnaie (pas de symbole €, pas de format monétaire).

3. **Aucune relation directe UserWallet ↔ SakaWallet** : Aucune ForeignKey, aucune fonction ne peut lier UserWallet (EUR) et SakaWallet (SAKA).

4. **Compostage obligatoire** : Le SAKA inactif doit être composté (retour au Silo Commun).

5. **Redistribution obligatoire** : Le Silo Commun doit redistribuer le SAKA composté (circulation obligatoire).

---

## PROTECTION JURIDIQUE

Ce manifeste définit explicitement le SAKA comme :

- **NON-FINANCIER** : Le SAKA n'est pas un instrument financier (réglementation AMF non applicable).
- **NON-MONÉTAIRE** : Le SAKA n'est pas une monnaie électronique (réglementation DSP2 non applicable).
- **NON-ACCUMULABLE** : Le SAKA ne peut pas être accumulé indéfiniment (compostage obligatoire).

---

## PROTECTION TECHNIQUE

- Tests de compliance automatiques (`tests/compliance/`)
- CI/CD bloquante (GitHub Actions)
- Hooks Git pre-commit
- Validation au niveau modèle (Django)
- Protection TypeScript frontend (`utils/saka.ts`)

---

## PROTECTION HUMAINE

- Gouvernance protectrice (conseil d'administration)
- Formation obligatoire de l'équipe
- Review obligatoire pour modifications critiques

---

**Ce manifeste est NON NÉGOCIABLE et doit être préservé à tout prix.**

