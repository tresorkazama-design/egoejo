# 📜 Charte des Projets Labellisés "EGOEJO COMPLIANT"

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Document Contractuel - Engagement Opposable

---

## 🎯 Préambule

En adhérant au label **"EGOEJO COMPLIANT"**, le projet s'engage à respecter les principes philosophiques, techniques et structurels définis dans cette charte.

Cette charte est **opposable** et peut entraîner le retrait du label en cas de violation.

---

## ✅ Devoirs des Projets Labellisés

### 1. Transparence

#### 1.1 Documentation Publique

Le projet labellisé s'engage à :

- ✅ **Publier publiquement** son manifeste philosophique
- ✅ **Documenter** sa conformité aux critères du label
- ✅ **Maintenir à jour** la documentation technique
- ✅ **Exposer** un endpoint public de vérification (`/api/public/egoejo-compliance.json`)

#### 1.2 Badge Public

Le projet labellisé s'engage à :

- ✅ **Afficher** le badge "EGOEJO COMPLIANT" dans son README
- ✅ **Lier** le badge à l'endpoint de vérification
- ✅ **Mettre à jour** le badge si le statut change

#### 1.3 Communication Honnête

Le projet labellisé s'engage à :

- ✅ **Ne jamais** présenter le SAKA (ou équivalent) comme un instrument financier
- ✅ **Ne jamais** présenter le SAKA comme une monnaie électronique
- ✅ **Toujours** mentionner la séparation SAKA / EUR (ou équivalent)
- ✅ **Toujours** documenter les métriques avec leurs métadonnées

---

### 2. Auditabilité

#### 2.1 Tests de Compliance

Le projet labellisé s'engage à :

- ✅ **Maintenir** des tests de compliance automatiques (minimum 80% passent)
- ✅ **Tagger** les tests avec `@egoejo_compliance` (ou équivalent)
- ✅ **Exécuter** les tests en CI/CD de manière bloquante
- ✅ **Documenter** les tests et leur objectif

#### 2.2 Endpoint Public

Le projet labellisé s'engage à :

- ✅ **Exposer** un endpoint `/api/public/egoejo-compliance.json` (ou équivalent)
- ✅ **Maintenir** l'endpoint accessible 24/7
- ✅ **Mettre à jour** l'endpoint en temps réel
- ✅ **Conformer** la réponse au schéma JSON défini

#### 2.3 Logs et Traçabilité

Le projet labellisé s'engage à :

- ✅ **Logger** les modifications directes des wallets (SAKA ou équivalent)
- ✅ **Tracer** les opérations critiques (compostage, redistribution)
- ✅ **Conserver** les logs pendant au moins 1 an
- ✅ **Rendre accessibles** les logs au comité du label sur demande

---

### 3. Conformité Continue

#### 3.1 Maintien des Critères Core

Le projet labellisé s'engage à :

- ✅ **Maintenir** la séparation SAKA / EUR (ou équivalent)
- ✅ **Maintenir** l'anti-accumulation (compostage ou mécanisme équivalent)
- ✅ **Maintenir** la circulation obligatoire (redistribution ou mécanisme équivalent)
- ✅ **Maintenir** la non-monétisation (aucune conversion possible)

#### 3.2 Maintien des Critères Extended (si applicable)

Le projet labellisé s'engage à :

- ✅ **Maintenir** la gouvernance protectrice
- ✅ **Maintenir** les audit logs centralisés
- ✅ **Maintenir** le monitoring temps réel

#### 3.3 Amélioration Continue

Le projet labellisé s'engage à :

- ✅ **Améliorer** progressivement sa conformité
- ✅ **Répondre** aux recommandations du comité
- ✅ **Collaborer** avec le comité pour résoudre les problèmes

---

### 4. Collaboration avec le Comité

#### 4.1 Réponses aux Demandes

Le projet labellisé s'engage à :

- ✅ **Répondre** aux demandes du comité dans un délai de 15 jours
- ✅ **Fournir** les informations demandées (logs, code, documentation)
- ✅ **Participer** aux audits périodiques
- ✅ **Assister** aux réunions du comité si convoqué

#### 4.2 Notification des Changements

Le projet labellisé s'engage à :

- ✅ **Notifier** le comité de tout changement majeur (architecture, philosophie)
- ✅ **Demander** validation avant de modifier les tests de compliance
- ✅ **Informer** le comité de toute violation détectée
- ✅ **Signaler** toute tentative de contournement

---

## 🚫 Interdictions Absolues

### Ce que le Label N'Autorise JAMAIS

Le projet labellisé s'engage à **NE JAMAIS** :

1. ❌ **Convertir** SAKA ↔ EUR (ou équivalent) directement ou indirectement
2. ❌ **Présenter** le SAKA comme un instrument financier ou une monnaie électronique
3. ❌ **Désactiver** le compostage (ou mécanisme équivalent) en production
4. ❌ **Désactiver** la redistribution (ou mécanisme équivalent) en production
5. ❌ **Modifier** les tests de compliance sans validation du comité
6. ❌ **Contourner** les tests de compliance (désactivation, modification)
7. ❌ **Accumuler** passivement le SAKA (sans compostage)
8. ❌ **Afficher** le SAKA avec un symbole monétaire (€, $, etc.)
9. ❌ **Calculer** un rendement financier sur le SAKA
10. ❌ **Vendre** ou **acheter** le SAKA contre de l'argent

**Violation de ces interdictions entraîne le retrait immédiat du label.**

---

## 🔄 Adaptations Locales Autorisées

### Ce qui est Adaptable

Le projet labellisé peut **adapter localement** :

1. ✅ **Terminologie** : Utiliser des termes locaux (ex: "grains" → "seeds")
2. ✅ **Mécanismes techniques** : Implémenter le compostage différemment (tant que l'effet est équivalent)
3. ✅ **Architecture** : Utiliser une stack technique différente (tant que les principes sont respectés)
4. ✅ **Interface utilisateur** : Adapter le design (tant que l'affichage reste non-monétaire)
5. ✅ **Gouvernance** : Adapter la gouvernance locale (tant que la protection est équivalente)

### Conditions d'Adaptation

Les adaptations locales sont autorisées si :

- ✅ **Principe respecté** : Le principe philosophique est maintenu
- ✅ **Effet équivalent** : L'effet technique est équivalent
- ✅ **Documentation** : L'adaptation est documentée
- ✅ **Validation** : L'adaptation est validée par le comité

---

## ⚖️ Sanctions en Cas de Violation

### Violation Mineure

**Exemples** :
- Documentation non à jour
- Endpoint public temporairement inaccessible
- Tests de compliance : 70-79% passent

**Sanctions** :
- ⚠️ Avertissement écrit
- ⚠️ Délai de correction : 30 jours
- ⚠️ Surveillance renforcée

---

### Violation Majeure

**Exemples** :
- Tests de compliance : < 70% passent
- Compostage désactivé temporairement
- Documentation manquante

**Sanctions** :
- ⚠️ Suspension du label (temporaire)
- ⚠️ Délai de correction : 60 jours
- ⚠️ Audit approfondi

---

### Violation Grave

**Exemples** :
- Conversion SAKA ↔ EUR détectée
- Compostage désactivé définitivement
- Tests de compliance contournés

**Sanctions** :
- ❌ Retrait immédiat du label
- ❌ Publication de la violation
- ❌ Interdiction de ré-adhésion pendant 1 an

---

## 📋 Checklist d'Engagement

### Avant l'Adhésion

- [ ] Manifeste philosophique publié
- [ ] Tests de compliance automatiques (80% minimum)
- [ ] CI/CD bloquante configurée
- [ ] Endpoint public configuré
- [ ] Documentation complète

### Après l'Adhésion

- [ ] Badge intégré au README
- [ ] Charte signée et publiée
- [ ] Surveillance continue acceptée
- [ ] Collaboration avec le comité acceptée

### Maintenance Continue

- [ ] Tests de compliance maintenus (80% minimum)
- [ ] Endpoint public maintenu
- [ ] Documentation mise à jour
- [ ] Conformité philosophique maintenue

---

## 🔗 Références

- [Processus d'Adhésion](PROCESSUS_ADHESION_LABEL.md)
- [Gouvernance du Label](GOUVERNANCE_LABEL.md)
- [Clarifications Interdictions vs Adaptations](CLARIFICATIONS_LABEL.md)
- [Label EGOEJO COMPLIANT](LABEL_EGOEJO_COMPLIANT.md)

---

**Fin de la Charte**

*Dernière mise à jour : 2025-01-27*

