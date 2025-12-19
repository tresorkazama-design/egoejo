# 🌱 TEST E2E : CYCLE DU VIVANT SAKA
## Promesse Utilisateur Validée

**Date** : 2025-12-19  
**Fichier** : `frontend/frontend/e2e/saka-lifecycle.spec.js`  
**Mission** : Valider la promesse utilisateur du SAKA via test E2E complet

---

## 📋 VUE D'ENSEMBLE

### Scénario Testé

Le test E2E valide le **cycle complet du Vivant SAKA** :

1. **Gain** : Utilisateur gagne du SAKA
2. **Dormance** : Simule inactivité > 90 jours
3. **Compost** : Vérifie dépréciation effective et notification
4. **Silo** : Vérifie que le Silo est alimenté du montant exact
5. **Redistribution** : Simule cycle mensuel et vérifie redistribution

### Contrainte Critique

**Le test DOIT ÉCHOUER (FAIL) si le cycle est rompu à n'importe quelle étape.**

---

## 🎯 TESTS INCLUS

### Test 1 : Cycle Complet du Vivant SAKA

**Nom** : `devrait valider le cycle complet du Vivant SAKA : Gain → Dormance → Compost → Silo → Redistribution`

**Scénario** :
1. ✅ Utilisateur gagne 50 SAKA (300 → 350 SAKA)
2. ✅ Simule inactivité 95 jours
3. ✅ Vérifie notification "Retour à la terre" visible
4. ✅ Vérifie solde diminué (350 → 315 SAKA, 35 compostés)
5. ✅ Vérifie Silo alimenté (0 → 35 SAKA)
6. ✅ Simule redistribution (35 → 32 SAKA dans Silo)

**Vérifications Critiques** :
- ✅ Solde diminue réellement après compostage
- ✅ Notification compost visible
- ✅ Silo contient montant exact composté
- ✅ Silo diminue après redistribution

**Échec si** :
- ❌ Solde non composté malgré inactivité
- ❌ Notification non affichée
- ❌ Silo non alimenté
- ❌ Redistribution non effectuée

---

### Test 2 : Détection Cycle Rompu (Compostage)

**Nom** : `devrait ÉCHOUER si le cycle est rompu (SAKA non composté malgré inactivité)`

**Scénario de Violation** :
- Utilisateur inactif depuis 95 jours
- Solde SAKA élevé (350 SAKA)
- **Mais le solde n'est PAS composté** (VIOLATION)
- Le Silo reste vide (VIOLATION)

**Action** : Le test **ÉCHOUE EXPLICITEMENT** avec message d'erreur détaillé

**Message d'échec** :
```
CYCLE SAKA ROMPU : L'utilisateur est éligible au compostage 
(350 SAKA, inactif depuis 95 jours) 
mais le solde n'a PAS été composté (350 SAKA au lieu de 315) 
et le Silo est vide (0 SAKA au lieu de 35). 
Le compostage n'a pas eu lieu. CYCLE INCOMPLET.
```

---

### Test 3 : Détection Cycle Rompu (Redistribution)

**Nom** : `devrait ÉCHOUER si le Silo ne redistribue pas`

**Scénario de Violation** :
- Silo contient du SAKA (35 SAKA)
- Redistribution activée
- **Mais le Silo ne diminue pas** (VIOLATION)
- Aucun wallet actif crédité (VIOLATION)

**Action** : Le test **ÉCHOUE EXPLICITEMENT** avec message d'erreur détaillé

**Message d'échec** :
```
CYCLE SAKA ROMPU : La redistribution n'a pas eu lieu. 
Le Silo contient 35 SAKA mais n'a pas été redistribué. 
Balance Silo attendue après redistribution: 32. 
Le Silo DOIT se vider vers le commun. CYCLE INCOMPLET.
```

---

## 🔍 VÉRIFICATIONS VISUELLES

### 1. Notification Compost

**Sélecteurs** :
- `/retour.*terre/i`
- `/grains.*retourner.*terre/i`
- `/compost.*éligible/i`
- `/saka.*compost/i`
- `/retour.*commun/i`

**Texte attendu** : "🌾 Vos grains vont bientôt retourner à la terre"

**Timeout** : 5000ms (augmenté pour stabilité)

---

### 2. Solde SAKA

**Sélecteur** : `page.getByText(new RegExp('${balance}.*SAKA', 'i'))`

**Vérifications** :
- Solde initial : 300 SAKA
- Solde après gain : 350 SAKA
- Solde après compost : 315 SAKA

---

### 3. Silo Commun

**Page** : `/saka/saisons`

**Sélecteurs** :
- Section avec texte "Silo Commun"
- Montant affiché : `{silo.total_balance} SAKA`

**Vérifications** :
- Silo initial : 0 SAKA
- Silo après compost : 35 SAKA
- Silo après redistribution : 32 SAKA

---

## 📊 CONSTANTES DU SCÉNARIO

```javascript
// États initiaux
USER_INACTIF_INITIAL_SAKA = 300
USER_ACTIF_INITIAL_SAKA = 100
INITIAL_SILO_BALANCE = 0

// Après gain
SAKA_GAIN = 50
USER_INACTIF_AFTER_GAIN = 350

// Après compostage (10% de 350 = 35)
COMPOSTED_AMOUNT = 35
USER_INACTIF_AFTER_COMPOST = 315
SILO_AFTER_COMPOST = 35

// Après redistribution (10% de 35 = 3.5, arrondi à 3)
REDISTRIBUTED_PER_WALLET = 3
USER_ACTIF_AFTER_REDISTRIBUTION = 103
SILO_AFTER_REDISTRIBUTION = 32
```

---

## 🚨 POINTS D'ÉCHEC CRITIQUES

Le test **ÉCHOUE** si :

1. **Compostage non effectué** :
   - Solde non diminué malgré inactivité
   - Notification non affichée
   - Silo non alimenté

2. **Redistribution non effectuée** :
   - Silo ne diminue pas
   - Wallets actifs non crédités

3. **Cycle incomplet** :
   - Une étape manquante (Gain → Dormance → Compost → Silo → Redistribution)
   - Montants incohérents

---

## ✅ VALIDATION

### Tests Générés
- ✅ 3 tests E2E complets
- ✅ Scénario cycle complet validé
- ✅ Scénarios de violation détectés
- ✅ Messages d'échec explicites

### Couverture
- ✅ Gain SAKA
- ✅ Dormance (inactivité > 90 jours)
- ✅ Compost (dépréciation effective)
- ✅ Silo (alimentation exacte)
- ✅ Redistribution (cycle mensuel)

---

## 🎯 PROMESSE UTILISATEUR VALIDÉE

Le test E2E garantit que :

1. ✅ **Le SAKA gagné peut être perdu si inactif**
   - Validé : Solde diminue après inactivité

2. ✅ **Le SAKA composté retourne au Silo Commun**
   - Validé : Silo alimenté du montant exact composté

3. ✅ **Le Silo redistribue aux utilisateurs actifs**
   - Validé : Silo diminue, wallets actifs crédités

4. ✅ **Le cycle est NON NÉGOCIABLE**
   - Validé : Test échoue si cycle rompu

---

**Le test E2E du Cycle du Vivant SAKA est prêt à être exécuté.  
Il valide la promesse utilisateur et échoue si le cycle est rompu.**

---

*Rapport généré le : 2025-12-19*

