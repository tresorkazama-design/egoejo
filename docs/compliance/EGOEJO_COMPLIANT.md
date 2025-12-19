# Badge EGOEJO Compliant

## Définition

Le badge **EGOEJO Compliant** atteste que le code respecte la constitution EGOEJO, telle que vérifiée automatiquement par le bot de conformité.

## Critères exacts

Pour obtenir le badge **EGOEJO Compliant**, le code doit satisfaire **toutes** les conditions suivantes :

### 1. Aucune conversion SAKA ↔ EUR

- Aucun pattern de conversion détecté : `convert.*saka.*eur`, `saka_to_eur`, `exchange_rate`, etc.
- Aucune fonction de conversion entre SAKA et EUR
- Aucun calcul de prix SAKA en EUR

**Vérification** : `.egoejo/guardian.py` - Règle `no_conversion` (CRITICAL)

### 2. Aucun rendement financier basé sur SAKA

- Aucun pattern de rendement détecté : `saka.*interest`, `saka.*yield`, `saka.*profit`, etc.
- Aucun calcul d'intérêt, dividende ou ROI basé sur SAKA
- Aucun champ de rendement dans les modèles SAKA

**Vérification** : `.egoejo/guardian.py` - Règle `no_financial_return` (CRITICAL)

### 3. Aucun affichage monétaire du SAKA

- Aucun pattern d'affichage monétaire détecté : `saka.*€`, `saka.*euro`, `saka.*currency`, etc.
- Le SAKA n'est jamais affiché avec un symbole monétaire
- Aucune conversion implicite SAKA → EUR dans l'UI

**Vérification** : `.egoejo/guardian.py` - Règle `no_monetary_display` (HIGH)

### 4. Tests obligatoires pour modifications SAKA

- Si un fichier SAKA est modifié, au moins un fichier de test SAKA doit également être modifié
- Les tests SAKA doivent être présents dans `backend/tests/compliance/test_saka*.py` ou équivalent

**Vérification** : `.egoejo/guardian.py` - Règle `saka_tests_required` (HIGH)

### 5. Cycle SAKA non négociable

- Le compostage SAKA ne peut pas être désactivé ou contourné
- Le Silo doit être alimenté après compost
- Aucune étape du cycle ne peut être supprimée

**Vérification** : `backend/tests/compliance/test_saka_cycle_incompressible.py`

### 6. Séparation stricte SAKA / EUR

- Les modules finance/investment n'importent pas SAKA
- Les modules SAKA n'importent pas finance/investment
- Aucune dépendance croisée entre les deux structures

**Vérification** : `backend/tests/compliance/test_banque_dormante_ne_touche_pas_saka.py`

## Vérification automatique

Le badge est basé sur l'exécution automatique du bot de conformité :

- **Script** : `.egoejo/guardian.py`
- **CI/CD** : `.github/workflows/egoejo-guardian.yml`
- **Tests** : `backend/tests/compliance/`

Le badge est **vert** si :
- Tous les tests de conformité passent
- Le PR bot ne détecte aucune violation critique
- Les tests SAKA sont présents pour les modifications SAKA

Le badge est **rouge** si :
- Au moins un test de conformité échoue
- Le PR bot détecte une violation critique
- Des tests SAKA sont manquants pour les modifications SAKA

## Ce que le badge GARANTIT

Le badge **EGOEJO Compliant** garantit que :

1. ✅ **Aucune conversion SAKA ↔ EUR** n'existe dans le code
2. ✅ **Aucun rendement financier** n'est basé sur SAKA
3. ✅ **Aucun affichage monétaire** du SAKA n'est présent
4. ✅ **Le cycle SAKA** est complet et non négociable
5. ✅ **La séparation SAKA / EUR** est strictement respectée
6. ✅ **Les tests de conformité** sont présents et passent

Ces garanties sont **vérifiables** par :
- Lecture du code source (`.egoejo/guardian.py`)
- Exécution des tests de conformité (`backend/tests/compliance/`)
- Consultation des logs CI/CD (GitHub Actions)

## Ce que le badge NE GARANTIT PAS

Le badge **EGOEJO Compliant** **N'ATTESTE PAS** :

1. ❌ **D'un rendement financier** : Le badge ne garantit aucun rendement, intérêt ou profit
2. ❌ **D'une performance économique** : Le badge ne garantit aucune performance financière ou économique
3. ❌ **D'une valeur monétaire du SAKA** : Le badge ne garantit aucune valeur en EUR ou autre devise
4. ❌ **D'une garantie d'investissement** : Le badge ne garantit aucun retour sur investissement
5. ❌ **D'une stabilité de prix** : Le badge ne garantit aucune stabilité ou convertibilité du SAKA
6. ❌ **D'une conformité réglementaire** : Le badge ne garantit aucune conformité aux réglementations financières

**Phrase obligatoire** :

> **Ce badge atteste du respect des règles EGOEJO. Il n'atteste ni d'un rendement financier, ni d'une performance économique.**

## Vérification manuelle

Pour vérifier manuellement le statut du badge :

```bash
# Exécuter le bot de conformité localement
python .egoejo/guardian.py

# Exécuter les tests de conformité
python -m pytest backend/tests/compliance/ -v
```

## Références

- **Constitution EGOEJO** : `docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md`
- **Bot de conformité** : `.egoejo/guardian.py`
- **Tests de conformité** : `backend/tests/compliance/`
- **Workflow CI/CD** : `.github/workflows/egoejo-guardian.yml`

## Historique

- **Version 1.0** : 2025-12-18 - Création du badge basé sur le PR bot

---

**Dernière mise à jour** : 2025-12-18

