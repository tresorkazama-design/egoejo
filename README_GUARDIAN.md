# 🛡️ EGOEJO Guardian - Protection Automatique

## 🏛️ Mission

Le **Guardian EGOEJO** est un système de protection automatique qui **rend la trahison du projet techniquement impossible**.

Il agit comme un **PR Bot + Auditeur** qui vérifie automatiquement chaque modification de code pour s'assurer qu'elle respecte la **Constitution EGOEJO**.

---

## 🚫 Règles Absolues Protégées

### 1. Aucune Conversion SAKA ↔ EUR
- ❌ Bloque toute fonction de conversion
- ❌ Bloque tout calcul de taux de change
- ❌ Bloque tout affichage d'équivalent monétaire

### 2. Aucun Rendement Financier sur SAKA
- ❌ Bloque tout calcul de ROI
- ❌ Bloque tout calcul de yield
- ❌ Bloque tout mécanisme d'intérêt/dividendes

### 3. Priorité Structure Relationnelle (SAKA)
- ❌ Bloque toute désactivation de SAKA
- ❌ Bloque toute subordination de SAKA à EUR
- ❌ Bloque tout feature flag SAKA désactivé

### 4. Anti-Accumulation Absolue
- ❌ Bloque toute désactivation du compostage
- ❌ Bloque tout contournement du cycle
- ❌ Bloque toute accumulation infinie

### 5. Cycle SAKA Incompressible
- ❌ Bloque tout contournement du cycle
- ❌ Bloque tout raccourci sans compostage
- ❌ Bloque tout compostage sans Silo

---

## 🛡️ Composants

### 1. PR Bot GitHub Actions
**Fichier** : `.github/workflows/pr-bot-egoejo-guardian.yml`

- ✅ Vérifie automatiquement chaque Pull Request
- ✅ Bloque la PR si violations détectées
- ✅ Commentaire détaillé sur chaque violation

### 2. Pre-commit Hook
**Fichier** : `.git/hooks/pre-commit`

- ✅ Vérifie chaque commit local
- ✅ Bloque le commit si violations détectées
- ✅ Message d'erreur détaillé

### 3. Constitution EGOEJO
**Fichier** : `docs/architecture/CONSTITUTION_EGOEJO.md`

- ✅ Documentation complète des règles
- ✅ Exemples de violations
- ✅ Exemples conformes

---

## 🚀 Installation

### Linux / macOS
```bash
./scripts/install-guardian-hooks.sh
```

### Windows
```powershell
Copy-Item .git/hooks/pre-commit-egoejo-guardian .git/hooks/pre-commit
```

---

## 📊 Exemple de Blocage

### Tentative de Violation

```python
# ❌ Ce code sera BLOQUÉ par le Guardian
def convert_saka_to_eur(saka_amount):
    rate = 0.01  # 1 SAKA = 0.01 EUR
    return saka_amount * rate
```

### Résultat

```
🚫 COMMIT BLOQUÉ : 1 violation(s) de la Constitution EGOEJO détectée(s)

❌ VIOLATION CRITIQUE : Conversion SAKA ↔ EUR détectée
🚫 La structure relationnelle (SAKA) et la structure instrumentale (EUR) 
   sont strictement séparées.

Consultez docs/architecture/CONSTITUTION_EGOEJO.md pour plus d'informations
```

---

## ✅ Code Conforme

```python
# ✅ Ce code est CONFORME
def get_saka_balance(user):
    wallet = get_wallet(user)
    return {
        'balance': wallet.balance,
        'total_harvested': wallet.total_harvested,
        'total_planted': wallet.total_planted
    }
    # Pas d'équivalent EUR, pas de conversion
```

---

## 📚 Documentation

- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Installation** : `docs/architecture/GUARDIAN_EGOEJO_INSTALLATION.md`
- **Audit Tests** : `docs/reports/AUDIT_COMPLET_TESTS_EGOEJO_2025-12-19.md`

---

## 🏛️ Constitution EGOEJO

**Double Structure Économique Non-Négociable** :

1. **Structure Relationnelle (Souveraine, Prioritaire)**
   - SAKA : Engagement, don, réputation
   - Cycle : Récolte → Usage → Compost → Silo → Redistribution
   - Règle : Anti-accumulation absolue

2. **Structure Instrumentale (Subordonnée, Dormante par défaut)**
   - EUR : Finance, paiement, conformité
   - Règle : Peut exister mais ne doit JAMAIS contraindre ou corrompre le SAKA

---

**Le Guardian EGOEJO est ACTIF et ENFORCÉ.  
Aucune exception n'est autorisée.  
La trahison du projet est techniquement impossible.**

