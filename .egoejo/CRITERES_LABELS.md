# Critères de Labels Automatiques EGOEJO

## 🟢 COMPATIBLE EGOEJO

**Critères EXACTS (tous doivent être vrais) :**

1. ✅ **Aucune violation critique détectée**
   - Aucun pattern de conversion SAKA ↔ EUR
   - Aucun pattern de rendement financier basé sur SAKA
   - Aucun pattern de désactivation/contournement du compostage
   - Aucune référence EUR dans services/modèles SAKA
   - Aucune référence SAKA dans services/modèles EUR

2. ✅ **Aucune violation importante détectée**
   - Aucun affichage monétaire du SAKA (€, euro, currency)
   - Aucun champ de rendement dans modèles SAKA

3. ✅ **Tests présents pour changements SAKA**
   - Si fichiers SAKA modifiés → fichiers de test correspondants modifiés OU existent déjà

4. ✅ **Feature flags respectés**
   - Si fichiers EUR modifiés → vérification de `ENABLE_INVESTMENT_FEATURES` présente

**Résultat :** PR approuvée automatiquement

---

## 🟡 COMPATIBLE SOUS CONDITIONS

**Critères EXACTS (au moins un doit être vrai, mais AUCUNE violation critique) :**

1. ⚠️ **Violations importantes détectées (mais pas critiques)**
   - Affichage monétaire du SAKA détecté
   - Champ de rendement dans modèles SAKA détecté
   - Mais AUCUNE violation critique

2. ⚠️ **Tests manquants pour changements SAKA**
   - Fichiers SAKA modifiés SANS fichiers de test correspondants
   - Mais AUCUNE violation critique

3. ⚠️ **Feature flags non vérifiés**
   - Fichiers EUR modifiés SANS vérification explicite de `ENABLE_INVESTMENT_FEATURES`
   - Mais AUCUNE violation critique

4. ⚠️ **Documentation manquante**
   - Changements SAKA importants SANS docstrings/comments explicites
   - Mais AUCUNE violation critique

**Résultat :** PR nécessite des ajustements avant approbation

---

## 🔴 NON COMPATIBLE EGOEJO

**Critères EXACTS (au moins un doit être vrai) :**

1. ❌ **Violation critique : Conversion SAKA ↔ EUR**
   - Pattern détecté : `convert.*saka.*eur|convert.*eur.*saka`
   - Pattern détecté : `saka.*=.*eur|eur.*=.*saka`
   - Pattern détecté : `saka.*\*.*eur|eur.*\*.*saka` (taux de change)
   - Pattern détecté : `price.*saka|saka.*price`
   - Pattern détecté : `exchange.*saka|saka.*exchange`

2. ❌ **Violation critique : Rendement financier basé sur SAKA**
   - Pattern détecté : `saka.*interest.*rate|interest.*rate.*saka`
   - Pattern détecté : `saka.*dividend.*payment|dividend.*payment.*saka`
   - Pattern détecté : `saka.*yield.*calculation|yield.*calculation.*saka`
   - Pattern détecté : `saka.*roi|roi.*saka`
   - Pattern détecté : `calculate.*saka.*interest|calculate.*interest.*saka`

3. ❌ **Violation critique : Désactivation/contournement du compostage**
   - Pattern détecté : `disable.*compost|compost.*disable`
   - Pattern détecté : `skip.*compost|compost.*skip`
   - Pattern détecté : `bypass.*compost|compost.*bypass`
   - Pattern détecté : `remove.*compost|compost.*remove`
   - Pattern détecté : `compost.*=.*False|compost.*=.*None`

4. ❌ **Violation critique : Référence EUR dans SAKA**
   - Import détecté : `from.*finance.*import` dans services SAKA
   - Import détecté : `from.*investment.*import` dans services SAKA
   - Référence détectée : `ForeignKey.*finance|ForeignKey.*investment` dans modèles SAKA

5. ❌ **Violation critique : Référence SAKA dans EUR**
   - Import détecté : `from.*saka.*import` dans services Finance/Investment
   - Référence détectée : `SakaWallet|SakaTransaction` dans services Finance/Investment

**Résultat :** PR bloquée immédiatement

---

## Règles de Priorité

1. **Toute violation critique = 🔴 immédiat** (même si d'autres critères sont OK)
2. **Violations importantes uniquement = 🟡** (si aucune violation critique)
3. **Tout OK = 🟢**

---

## Exemples de Sortie

### 🟢 COMPATIBLE EGOEJO

```
🟢 COMPATIBLE EGOEJO

✅ Aucune violation détectée
✅ Tests présents pour changements SAKA
✅ Feature flags respectés

Cette PR respecte la constitution EGOEJO.
```

### 🟡 COMPATIBLE SOUS CONDITIONS

```
🟡 COMPATIBLE SOUS CONDITIONS

⚠️ Tests manquants : backend/core/services/saka.py modifié sans tests
⚠️ Documentation manquante : Changements SAKA sans docstrings

ACTION REQUISE :
- Ajouter des tests pour backend/core/services/saka.py
- Ajouter des docstrings explicites pour les changements SAKA
```

### 🔴 NON COMPATIBLE EGOEJO

```
🔴 NON COMPATIBLE EGOEJO

❌ VIOLATION CRITIQUE : Conversion SAKA ↔ EUR détectée
   Fichier: backend/core/services/saka.py, Ligne 42
   Pattern: convert_saka_to_eur(saka_amount)

❌ VIOLATION CRITIQUE : Désactivation du compostage détectée
   Fichier: backend/core/services/saka.py, Ligne 318
   Pattern: if not compost_enabled: skip_compost = True

ACTION REQUISE :
- SUPPRIMER toute logique de conversion SAKA ↔ EUR
- RESTAURER le compostage obligatoire (cycle SAKA non négociable)
```

