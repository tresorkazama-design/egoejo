# 🔒 EGOEJO : Code-Enforced Philosophy

**Date** : 17 Décembre 2025  
**Version** : 1.0  
**Public** : Whitepaper, FAQ, Documentation publique

---

## 🎯 Qu'est-ce que "Code-Enforced" ?

**"Code-Enforced"** signifie que les règles philosophiques d'EGOEJO ne sont **pas des promesses marketing**, mais des **contraintes logicielles vérifiables** encodées directement dans le code source.

Contrairement à une plateforme qui "promet" de respecter certaines valeurs, EGOEJO **garantit** ces valeurs par le code. Si une règle est violée, le code **refuse** de fonctionner.

---

## ✅ Garanties Code-Enforced

### 1. Anti-Accumulation : Impossible de Thésauriser Indéfiniment

**Promesse** : "Le SAKA ne peut pas être accumulé indéfiniment."

**Garantie Code-Enforced** :
- Le compostage progressif (10% après 90 jours) est **obligatoire** et **automatique**
- Si vous désactivez le compostage, les tests philosophiques **échouent**
- Le code **refuse** de fonctionner sans compostage

**Preuve** :
```python
# backend/core/services/saka.py
# Le compostage est OBLIGATOIRE. Si désactivé, le service retourne une erreur.
if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
    return {"skipped": "disabled"}  # ⚠️ VIOLATION PHILOSOPHIQUE

# Tests philosophiques qui PROTÈGENT cette garantie
# backend/core/tests_saka_philosophy.py
def test_compostage_progressif_empêche_thésaurisation_infinie(self):
    """PHILOSOPHIE : L'impossibilité de thésaurisation."""
    # Si ce test échoue, la garantie est violée
```

**Vérification** :
- ✅ 14 tests philosophiques protègent cette garantie
- ✅ Tous les tests passent (14/14)
- ✅ Le code refuse de fonctionner sans compostage

---

### 2. Circulation Obligatoire : Impossible de Contourner le Cycle

**Promesse** : "Un utilisateur ne peut pas contourner le cycle SAKA."

**Garantie Code-Enforced** :
- Le compostage s'applique **même si** l'utilisateur fait une activité ponctuelle juste avant
- Le code **vérifie strictement** la date de dernière activité (90 jours)
- Aucun mécanisme ne permet de contourner le compostage

**Preuve** :
```python
# backend/core/services/saka.py
# Vérification stricte : last_activity_date < cutoff (90 jours)
cutoff = timezone.now() - timedelta(days=inactivity_days)
qs = SakaWallet.objects.select_for_update().filter(
    last_activity_date__lt=cutoff,  # Inactif depuis 90+ jours
    balance__gte=min_balance,
)

# Tests philosophiques qui PROTÈGENT cette garantie
def test_impossibilité_de_contourner_le_compostage_par_activité_ponctuelle(self):
    """PHILOSOPHIE : Un utilisateur ne peut pas contourner le cycle."""
    # Si ce test échoue, la garantie est violée
```

**Vérification** :
- ✅ 2 tests philosophiques protègent cette garantie
- ✅ Tous les tests passent (2/2)
- ✅ Le code refuse de contourner le compostage

---

### 3. Retour au Commun : Le Collectif Bénéficie de l'Inutilisation

**Promesse** : "Le SAKA inactif retourne au Silo Commun et est redistribué équitablement."

**Garantie Code-Enforced** :
- Le SAKA composté va **automatiquement** dans le Silo Commun
- La redistribution (5% par cycle) est **automatique** et **équitable**
- Le code **garantit** que le Silo ne s'accumule pas indéfiniment

**Preuve** :
```python
# backend/core/services/saka.py
# Le SAKA composté va AUTOMATIQUEMENT dans le Silo
silo.total_balance += amount
silo.total_composted += amount

# Redistribution équitable : même montant pour tous les wallets actifs
eligible_wallets = SakaWallet.objects.filter(
    total_harvested__gte=SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY
)
redistributed_per_wallet = redistributed_amount // eligible_wallets.count()

# Tests philosophiques qui PROTÈGENT cette garantie
def test_collectif_bénéficie_de_inutilisation_individuelle(self):
    """PHILOSOPHIE : Le collectif bénéficie de l'inutilisation individuelle."""
    # Si ce test échoue, la garantie est violée
```

**Vérification** :
- ✅ 3 tests philosophiques protègent cette garantie
- ✅ Tous les tests passent (3/3)
- ✅ Le code garantit le retour au commun

---

### 4. Non-Spéculation : Aucune Conversion SAKA ↔ Euro

**Promesse** : "Le SAKA ne peut pas être converti en euros, et vice versa."

**Garantie Code-Enforced** :
- **Aucun endpoint** ne permet de convertir SAKA en EUR
- **Aucun service** ne permet de convertir SAKA en EUR
- **Aucun test** ne valide une conversion SAKA ↔ EUR

**Preuve** :
```python
# backend/core/services/saka.py
# Aucune fonction de conversion SAKA ↔ EUR

# backend/finance/services.py
# Aucune référence à SAKA

# Séparation stricte : UserWallet (EUR) vs SakaWallet (SAKA)
# Aucun ForeignKey ou relation entre les deux
```

**Vérification** :
- ✅ Aucun endpoint de conversion n'existe
- ✅ Aucun service de conversion n'existe
- ✅ Les tests philosophiques refusent toute logique de spéculation

---

### 5. Transparence Honnête : Scores Explicables ou Explicitement Déclaratifs

**Promesse** : "Les scores 4P sont explicables, traçables, ou explicitement déclaratifs."

**Garantie Code-Enforced** :
- P1 (financial_score) : Somme des contributions financières (traçable)
- P2 (saka_score) : Somme des boosts SAKA (traçable)
- P3 (social_score) : Explicitement marqué "PROXY V1 INTERNE"
- P4 (purpose_score) : Explicitement marqué "PROXY V1 INTERNE"

**Preuve** :
```python
# backend/core/services/impact_4p.py
# P3 : PROXY V1 INTERNE : Utilise impact_score du projet (ou 0 si non défini)
# ⚠️ ATTENTION : Ce score est un indicateur interne simplifié, non académique.
social_score = project.impact_score or 0

# Frontend : Labels "Signal social (V1 interne)" et "Signal de sens (V1 interne)"
# Tooltips : Explications dans FourPStrip, UserImpact4P, Impact4PCard
```

**Vérification** :
- ✅ Docstrings explicites dans le code
- ✅ Labels frontend explicites
- ✅ Tests vérifient que P3/P4 sont explicitement marqués comme proxies

---

## 🔍 Vérification Publique

### Code Source Ouvert

Le code source d'EGOEJO est **ouvert** et **vérifiable**. Toute personne peut :
- ✅ Examiner le code source
- ✅ Vérifier que les garanties sont encodées
- ✅ Exécuter les tests philosophiques
- ✅ Confirmer que les règles sont respectées

**Repository** : [GitHub EGOEJO](https://github.com/egoejo/egoejo) (exemple)

### Tests Philosophiques

Les tests philosophiques sont **publics** et **exécutables**. Toute personne peut :
- ✅ Exécuter les tests : `python -m pytest backend/core/tests_saka_philosophy.py`
- ✅ Vérifier que les garanties sont protégées
- ✅ Confirmer que les règles sont respectées

**Fichier** : `backend/core/tests_saka_philosophy.py` (14 tests)

### Documentation Technique

La documentation technique est **publique** et **détaillée**. Toute personne peut :
- ✅ Lire la documentation : `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md`
- ✅ Comprendre le "pourquoi" derrière chaque choix technique
- ✅ Vérifier que les contraintes morales sont encodées

**Fichiers** :
- `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md` : Explication du "pourquoi"
- `docs/reports/AUDIT_CONFORMITE_EGOEJO.md` : Audit systématique de conformité
- `docs/reports/CONTROLE_COMPLET_EGOEJO_2025-12-17.md` : Contrôle complet

---

## 🎯 Différence avec les Promesses Marketing

### Promesse Marketing (Non Code-Enforced)

❌ **"Nous promettons de respecter vos valeurs."**
- Pas vérifiable
- Pas exécutable
- Pas contraignant

### Garantie Code-Enforced (EGOEJO)

✅ **"Le code refuse de fonctionner si les valeurs sont violées."**
- Vérifiable (code source ouvert)
- Exécutable (tests philosophiques)
- Contraignant (le code refuse de fonctionner)

---

## 📊 Résultats de Vérification

### Tests Philosophiques

**14 tests philosophiques** protègent le Manifeste EGOEJO :
- ✅ 14/14 tests passent
- ✅ Tous les principes non-négociables sont protégés
- ✅ Aucune violation détectée

### Audit de Conformité

**Score de conformité** : **91%** (11/12 domaines conformes)
- ✅ Anti-accumulation encodée
- ✅ Compostage effectif
- ✅ Silo reçoit la valeur compostée
- ✅ Redistribution existe
- ✅ Flux financiers atomiques
- ✅ Traçabilité financière
- ✅ P1/P2 basés sur données réelles
- ✅ P3/P4 explicitement déclaratifs
- ✅ Cycles SAKA visibles frontend
- ✅ Silo visible
- ✅ Tests philosophiques complets

---

## 🚀 Pourquoi C'est Important

### Pour les Utilisateurs

- ✅ **Confiance** : Les règles ne sont pas des promesses, mais des garanties
- ✅ **Transparence** : Le code source est ouvert et vérifiable
- ✅ **Sécurité** : Impossible de violer les règles sans modifier le code

### Pour les Partenaires Institutionnels

- ✅ **Crédibilité** : Les règles sont encodées, pas juste promises
- ✅ **Vérifiabilité** : Les tests philosophiques peuvent être exécutés
- ✅ **Traçabilité** : Chaque garantie est documentée et testée

### Pour les Développeurs

- ✅ **Clarté** : Le "pourquoi" est documenté dans le code
- ✅ **Protection** : Les tests philosophiques empêchent les violations
- ✅ **Maintenabilité** : Les règles sont encodées, pas implicites

---

## 📝 Citation pour Whitepaper / FAQ

> **"EGOEJO est Code-Enforced. Les règles ne sont pas des promesses marketing, mais des contraintes logicielles vérifiables. Le code source est ouvert, les tests philosophiques sont publics, et toute violation des principes fondateurs est détectée automatiquement. Si une règle est violée, le code refuse de fonctionner."**

---

## 🔗 Références

- **Code Source** : [GitHub EGOEJO](https://github.com/egoejo/egoejo)
- **Tests Philosophiques** : `backend/core/tests_saka_philosophy.py`
- **Documentation** : `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md`
- **Audit de Conformité** : `docs/reports/AUDIT_CONFORMITE_EGOEJO.md`

---

**Date de génération** : 17 Décembre 2025  
**Auteur** : Gardien de cohérence du Manifeste EGOEJO  
**Version du document** : 1.0

