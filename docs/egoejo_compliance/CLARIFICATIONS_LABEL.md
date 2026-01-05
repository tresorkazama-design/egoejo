# 🔍 Clarifications : Interdictions vs Adaptations Locales

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Document Public - Projets Tiers

---

## 🎯 Objectif

Ce document clarifie ce que le label **"EGOEJO COMPLIANT"** :
- ❌ **N'autorise JAMAIS** (interdictions absolues)
- ✅ **Autorise** (adaptations locales possibles)

---

## 🚫 Ce que le Label N'Autorise JAMAIS

### 1. Conversion SAKA ↔ EUR (ou Équivalent)

**Interdiction Absolue** :
- ❌ Aucune fonction de conversion
- ❌ Aucun endpoint API de conversion
- ❌ Aucun mécanisme de conversion (direct ou indirect)
- ❌ Aucun calcul d'équivalent monétaire

**Exemples Interdits** :
```python
# ❌ INTERDIT
def convert_saka_to_eur(amount_saka):
    return amount_saka * EXCHANGE_RATE

# ❌ INTERDIT
def get_saka_value_in_eur(amount_saka):
    return amount_saka * 0.01  # 1 SAKA = 0.01 EUR
```

**Justification** : La conversion violerait la séparation stricte SAKA / EUR, transformant le SAKA en instrument financier.

---

### 2. Présentation du SAKA comme Instrument Financier

**Interdiction Absolue** :
- ❌ Présenter le SAKA comme un instrument financier (AMF)
- ❌ Présenter le SAKA comme une monnaie électronique (DSP2)
- ❌ Présenter le SAKA comme un actif financier
- ❌ Présenter le SAKA comme un titre de capital

**Exemples Interdits** :
```markdown
# ❌ INTERDIT
"Investissez dans le SAKA pour un rendement de 5% par an"

# ❌ INTERDIT
"Le SAKA est un instrument financier régulé par l'AMF"
```

**Justification** : La présentation comme instrument financier violerait la nature non-financière du SAKA.

---

### 3. Désactivation du Compostage (ou Mécanisme Équivalent)

**Interdiction Absolue** :
- ❌ Désactiver le compostage en production
- ❌ Permettre l'accumulation passive
- ❌ Contourner le compostage

**Exemples Interdits** :
```python
# ❌ INTERDIT
SAKA_COMPOST_ENABLED = False  # En production

# ❌ INTERDIT
if user.is_premium:
    skip_compostage()  # Contournement
```

**Justification** : Le compostage est essentiel pour l'anti-accumulation et la circulation obligatoire.

---

### 4. Désactivation de la Redistribution (ou Mécanisme Équivalent)

**Interdiction Absolue** :
- ❌ Désactiver la redistribution en production
- ❌ Permettre la thésaurisation
- ❌ Contourner la redistribution

**Exemples Interdits** :
```python
# ❌ INTERDIT
SAKA_SILO_REDIS_ENABLED = False  # En production

# ❌ INTERDIT
if user.is_vip:
    skip_redistribution()  # Contournement
```

**Justification** : La redistribution est essentielle pour la circulation obligatoire et l'équité.

---

### 5. Affichage Monétaire du SAKA

**Interdiction Absolue** :
- ❌ Afficher le SAKA avec un symbole monétaire (€, $, etc.)
- ❌ Afficher le SAKA avec un format monétaire
- ❌ Calculer un prix en EUR pour le SAKA

**Exemples Interdits** :
```javascript
// ❌ INTERDIT
<span>{sakaBalance} €</span>

// ❌ INTERDIT
<span>Prix : {sakaPrice} EUR</span>
```

**Justification** : L'affichage monétaire violerait la nature non-monétaire du SAKA.

---

### 6. Rendement Financier sur le SAKA

**Interdiction Absolue** :
- ❌ Calculer un rendement financier
- ❌ Présenter le SAKA comme un investissement
- ❌ Promettre un retour sur investissement

**Exemples Interdits** :
```markdown
# ❌ INTERDIT
"Gagnez 5% par an sur votre SAKA"

# ❌ INTERDIT
"Investissez dans le SAKA pour un rendement garanti"
```

**Justification** : Le rendement financier violerait la nature non-financière du SAKA.

---

### 7. Modification des Tests de Compliance sans Validation

**Interdiction Absolue** :
- ❌ Désactiver les tests de compliance
- ❌ Modifier les tests sans validation du comité
- ❌ Contourner les tests

**Exemples Interdits** :
```python
# ❌ INTERDIT
@pytest.mark.skip  # Désactiver un test de compliance

# ❌ INTERDIT
# Modifier test_no_saka_eur_conversion.py sans validation
```

**Justification** : Les tests de compliance sont la garantie technique de la conformité.

---

## ✅ Ce qui est Adaptable Localement

### 1. Terminologie

**Adaptation Autorisée** :
- ✅ Utiliser des termes locaux (ex: "grains" → "seeds", "SAKA" → "LOCAL_CURRENCY")
- ✅ Traduire les messages dans la langue locale
- ✅ Adapter les noms de variables et fonctions

**Exemples Autorisés** :
```python
# ✅ AUTORISÉ
def format_local_currency_amount(amount):
    return f"{amount} seeds"  # Terme local

# ✅ AUTORISÉ
LOCAL_CURRENCY_COMPOST_ENABLED = True  # Nom local
```

**Condition** : Le principe philosophique doit être maintenu (non-financier, non-monétaire).

---

### 2. Mécanismes Techniques

**Adaptation Autorisée** :
- ✅ Implémenter le compostage différemment (tant que l'effet est équivalent)
- ✅ Implémenter la redistribution différemment (tant que l'effet est équivalent)
- ✅ Utiliser une architecture technique différente

**Exemples Autorisés** :
```python
# ✅ AUTORISÉ (si effet équivalent)
def local_compost_mechanism(wallet, days_inactive):
    # Implémentation locale différente
    if days_inactive > 90:
        wallet.balance *= 0.9  # Réduction de 10%
    return wallet

# ✅ AUTORISÉ (si effet équivalent)
def local_redistribution_mechanism(silo, active_users):
    # Implémentation locale différente
    amount_per_user = silo.balance / len(active_users)
    for user in active_users:
        user.wallet.balance += amount_per_user
    return silo
```

**Condition** : L'effet technique doit être équivalent (anti-accumulation, circulation obligatoire).

---

### 3. Architecture Technique

**Adaptation Autorisée** :
- ✅ Utiliser une stack technique différente (Python, Node.js, Rust, etc.)
- ✅ Utiliser une base de données différente (PostgreSQL, MongoDB, etc.)
- ✅ Utiliser un framework différent (Django, Express, etc.)

**Exemples Autorisés** :
```javascript
// ✅ AUTORISÉ (Node.js au lieu de Python)
async function harvestLocalCurrency(user, reason) {
    // Implémentation Node.js
    const wallet = await LocalCurrencyWallet.findOne({ user });
    wallet.balance += getReward(reason);
    await wallet.save();
}
```

**Condition** : Les principes philosophiques doivent être respectés (séparation, anti-accumulation).

---

### 4. Interface Utilisateur

**Adaptation Autorisée** :
- ✅ Adapter le design (couleurs, typographie, layout)
- ✅ Adapter les interactions (gestes, animations)
- ✅ Adapter l'accessibilité (langues, handicaps)

**Exemples Autorisés** :
```jsx
// ✅ AUTORISÉ (Design adapté)
<div className="local-currency-display">
    <span>{localCurrencyBalance} seeds</span>
    <span className="subtitle">Non-financier, non-monétaire</span>
</div>
```

**Condition** : L'affichage doit rester non-monétaire (pas de symbole €, $, etc.).

---

### 5. Gouvernance Locale

**Adaptation Autorisée** :
- ✅ Adapter la gouvernance locale (conseil, comité, vote)
- ✅ Adapter les règles de décision (majorité, unanimité)
- ✅ Adapter les mécanismes de protection

**Exemples Autorisés** :
```markdown
# ✅ AUTORISÉ
## Gouvernance Locale

- Conseil de 5 membres (au lieu de 3)
- Vote à la majorité qualifiée (au lieu de majorité simple)
- Protection via smart contract (au lieu de golden share)
```

**Condition** : La protection doit être équivalente (empêcher les violations philosophiques).

---

## 📊 Tableau Récapitulatif

| Élément | Interdit ❌ | Adaptable ✅ | Condition |
|---------|------------|-------------|-----------|
| **Conversion SAKA ↔ EUR** | ❌ Absolument | - | - |
| **Présentation financière** | ❌ Absolument | - | - |
| **Désactivation compostage** | ❌ Absolument | - | - |
| **Désactivation redistribution** | ❌ Absolument | - | - |
| **Affichage monétaire** | ❌ Absolument | - | - |
| **Rendement financier** | ❌ Absolument | - | - |
| **Modification tests** | ❌ Sans validation | ✅ Avec validation | Validation comité |
| **Terminologie** | - | ✅ Autorisé | Principe maintenu |
| **Mécanismes techniques** | - | ✅ Autorisé | Effet équivalent |
| **Architecture** | - | ✅ Autorisé | Principes respectés |
| **Interface utilisateur** | - | ✅ Autorisé | Affichage non-monétaire |
| **Gouvernance locale** | - | ✅ Autorisé | Protection équivalente |

---

## 🔍 Processus de Validation des Adaptations

### 1. Demande d'Adaptation

Le projet labellisé soumet une demande d'adaptation au comité du label :

**Contenu de la demande** :
- Description de l'adaptation
- Justification (pourquoi cette adaptation)
- Preuve que le principe est maintenu
- Preuve que l'effet est équivalent (si applicable)

### 2. Évaluation par le Comité

Le comité évalue l'adaptation :

**Critères d'évaluation** :
- ✅ Principe philosophique maintenu
- ✅ Effet technique équivalent (si applicable)
- ✅ Documentation complète
- ✅ Tests de compliance adaptés

### 3. Décision

**Décision** : Majorité simple du comité

**Délai** : 30 jours ouvrés

**Notification** : Écrite au projet

---

## 🔗 Références

- [Charte des Projets Labellisés](CHARTE_PROJETS_LABELLISES.md)
- [Processus d'Adhésion](PROCESSUS_ADHESION_LABEL.md)
- [Gouvernance du Label](GOUVERNANCE_LABEL.md)
- [Label EGOEJO COMPLIANT](LABEL_EGOEJO_COMPLIANT.md)

---

**Fin des Clarifications**

*Dernière mise à jour : 2025-01-27*

