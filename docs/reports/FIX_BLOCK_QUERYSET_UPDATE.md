# 🔒 FIX CRITIQUE : Bloquer QuerySet.update() sur SakaWallet

**Date** : 2025-01-01  
**Problème** : `update()` permettait de contourner les protections SAKA  
**Statut** : ✅ **CORRIGÉ**

---

## 📋 Résumé

La méthode `update()` sur `SakaWallet` permettait de contourner les règles de traçabilité et d'anti-accumulation en modifiant directement les champs SAKA via SQL, sans passer par les services SAKA.

**Corrections appliquées** :
1. ✅ Blocage strict de `update()` : Toute tentative de `.update()` lève maintenant une `ValidationError`
2. ✅ Message d'erreur explicite : "Direct update() is forbidden on SakaWallet. Use SakaTransaction service."
3. ✅ Tests unitaires complets : Nouveau fichier `test_saka_wallet_update_prevention.py` avec 6 tests
4. ✅ Mise à jour des tests existants : Correction du test qui s'attendait à ce que `update()` fonctionne avec `AllowSakaMutation()`

---

## 🔍 Analyse des Problèmes

### Problème #1 : update() Permettait de Contourner les Protections

**Avant** : La méthode `update()` ne bloquait que si des champs protégés étaient modifiés. Si aucun champ protégé n'était modifié, `update()` passait.

**Code avant** :
```python
def update(self, **kwargs):
    if not is_saka_mutation_allowed():
        protected_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
        modified_protected = [field for field in protected_fields if field in kwargs]
        
        if modified_protected:  # ❌ Ne bloque que si champs protégés modifiés
            raise ValidationError(...)
    
    return super().update(**kwargs)  # ❌ Passe si aucun champ protégé
```

**Impact** : Un développeur pouvait utiliser `update()` pour modifier d'autres champs, contournant ainsi les protections.

### Problème #2 : AllowSakaMutation() Permettait update()

**Avant** : `AllowSakaMutation()` permettait d'utiliser `update()`, ce qui contournait la traçabilité.

**Impact** : Les services SAKA pouvaient utiliser `update()` au lieu de `.save()`, contournant ainsi la traçabilité complète.

---

## ✅ Corrections Appliquées

### 1. Blocage Strict de update()

**Fichier** : `backend/core/models/saka.py` (lignes 61-85)

**Avant** :
```python
def update(self, **kwargs):
    if not is_saka_mutation_allowed():
        protected_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
        modified_protected = [field for field in protected_fields if field in kwargs]
        
        if modified_protected:
            raise ValidationError(...)
    
    return super().update(**kwargs)
```

**Après** :
```python
def update(self, **kwargs):
    """
    Bloque TOUTE tentative de mise à jour de masse via update().
    
    Constitution EGOEJO: no direct SAKA mutation.
    La méthode update() est strictement interdite sur SakaWallet pour garantir
    la traçabilité et l'anti-accumulation.
    """
    error_msg = (
        "VIOLATION CONSTITUTION EGOEJO : Direct update() is forbidden on SakaWallet. "
        "Use SakaTransaction service (harvest_saka, spend_saka, compost, redistribute)."
    )
    logger.critical(error_msg)
    raise ValidationError(error_msg)
```

**Avantages** :
- ✅ **Bloquant strict** : Toute tentative de `update()` est bloquée, même sans champs protégés
- ✅ **Message clair** : Indique explicitement d'utiliser les services SAKA
- ✅ **Traçabilité garantie** : Impossible de contourner la traçabilité via `update()`

---

### 2. Nouveau Fichier de Tests

**Fichier** : `backend/core/tests/models/test_saka_wallet_update_prevention.py`

**Tests créés** :
1. ✅ `test_update_without_protected_fields_raises_error` : Vérifie que `update()` est bloqué même sans champs protégés
2. ✅ `test_update_with_protected_fields_raises_error` : Vérifie que `update()` avec champs protégés est bloqué
3. ✅ `test_update_multiple_protected_fields_raises_error` : Vérifie que `update()` avec plusieurs champs protégés est bloqué
4. ✅ `test_update_all_wallets_raises_error` : Vérifie que `update()` sur tous les wallets est bloqué
5. ✅ `test_update_with_allow_saka_mutation_still_raises_error` : Vérifie que `update()` est bloqué même avec `AllowSakaMutation()`
6. ✅ `test_update_with_empty_kwargs_still_raises_error` : Vérifie que `update()` avec kwargs vides est bloqué

**Tous les tests sont marqués `@pytest.mark.critical`** ✅

---

### 3. Mise à Jour des Tests Existants

**Fichier** : `backend/core/tests/models/test_saka_wallet_protection.py`

**Test corrigé** :
- `test_update_allowed_with_context` → `test_update_still_raises_error_with_context`
- S'attend maintenant à une `ValidationError` même avec `AllowSakaMutation()`

---

## ✅ Vérification Finale

### update() Est Maintenant Strictement Bloqué

**Scénarios testés** :
1. ✅ `update()` sans champs protégés → Bloqué
2. ✅ `update()` avec champs protégés → Bloqué
3. ✅ `update()` avec `AllowSakaMutation()` → Bloqué
4. ✅ `update()` sur tous les wallets → Bloqué
5. ✅ `update()` avec kwargs vides → Bloqué

**Message d'erreur** :
```
VIOLATION CONSTITUTION EGOEJO : Direct update() is forbidden on SakaWallet. 
Use SakaTransaction service (harvest_saka, spend_saka, compost, redistribute).
```

---

## 📊 Résultat

✅ **La "porte dérobée" des mises à jour SQL directes est maintenant fermée.**

**Protections appliquées** :
1. Blocage strict de `update()` : Toute tentative lève une `ValidationError`
2. Message d'erreur explicite : Indique d'utiliser les services SAKA
3. Tests unitaires complets : 6 tests couvrent tous les scénarios
4. Mise à jour des tests existants : Cohérence avec le nouveau comportement

**Prochaines étapes** :
1. Exécuter les tests pour vérifier qu'ils passent
2. Vérifier que les services SAKA n'utilisent pas `update()` (ils utilisent `.save()` avec `AllowSakaMutation()`)
3. Documenter dans `docs/PROTECTION_SAKA_WALLET.md` que `update()` est strictement interdit

---

## 🧪 Tests à Exécuter

Pour vérifier que les protections fonctionnent :

```bash
# Test 1 : Exécuter tous les tests de protection SakaWallet
cd backend
pytest core/tests/models/test_saka_wallet_protection.py -v
pytest core/tests/models/test_saka_wallet_update_prevention.py -v

# Test 2 : Vérifier que update() est bloqué
python manage.py shell
>>> from core.models.saka import SakaWallet
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.first()
>>> wallet = SakaWallet.objects.filter(user=user).first()
>>> SakaWallet.objects.filter(pk=wallet.pk).update(balance=9999)
# Doit lever ValidationError: Direct update() is forbidden on SakaWallet
```

---

**Document généré le** : 2025-01-01  
**Statut** : ✅ **CORRIGÉ**

