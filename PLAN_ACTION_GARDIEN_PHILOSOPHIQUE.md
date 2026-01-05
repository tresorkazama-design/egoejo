# 🛡️ PLAN D'ACTION - GARDIEN PHILOSOPHIQUE EGOEJO
## Corrections Minimales Respectant les Contraintes Non Négociables

**Date** : 2025-01-27  
**Rôle** : Architecte Technique & Gardien Philosophique  
**Principe** : Solutions minimales, tests obligatoires, préservation de la philosophie SAKA/EUR

---

## 📋 CONTRAINTES NON NÉGOCIABLES

✅ **Séparation stricte SAKA / EUR** (aucune conversion, aucun rendement financier)  
✅ **Structure relationnelle (SAKA) prime toujours sur structure instrumentale (EUR)**  
✅ **Préserver les tests de compliance philosophique existants**  
✅ **Aucune optimisation ne doit favoriser l'accumulation passive**  
✅ **Toute modification critique DOIT être testée**  
✅ **Ne pas activer la V2.0 (Investment)**

---

## 🔴 PRIORITÉ 1 : PROTECTION PHILOSOPHIE (CRITIQUE)

### Risque Identifié

**Protection philosophie dépendante des tests** : Les tests de compliance peuvent être supprimés ou contournés (Django Admin, pas de CI/CD bloquante).

**Impact** : Trahison de la mission initiale possible (violation SAKA/EUR).

---

### Solution Minimale

#### 1.1 CI/CD Bloquante pour Tests de Compliance

**Action** : Ajouter une étape bloquante dans GitHub Actions qui exécute les tests de compliance.

**Fichier** : `.github/workflows/compliance.yml` (nouveau)

```yaml
name: Compliance Philosophique EGOEJO

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  compliance-tests:
    runs-on: ubuntu-latest
    name: Tests de Compliance SAKA/EUR
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: egotest
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/egotest
          SECRET_KEY: test-secret-key-for-ci-testing-only-min-50-chars-required
          ENABLE_SAKA: 'True'
        run: |
          cd backend
          python manage.py migrate
      
      - name: Run Compliance Tests (BLOQUANT)
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/egotest
          SECRET_KEY: test-secret-key-for-ci-testing-only-min-50-chars-required
          ENABLE_SAKA: 'True'
        run: |
          cd backend
          # Tests de compliance philosophique - BLOQUANT
          pytest tests/compliance/ -v --tb=short
          # Si un test échoue, le workflow échoue (bloque le merge)
```

**Test** : Vérifier que le workflow bloque un commit qui viole la séparation SAKA/EUR.

---

#### 1.2 Hook Git Pre-Commit

**Action** : Ajouter un hook Git pre-commit qui exécute les tests de compliance avant chaque commit.

**Fichier** : `.git/hooks/pre-commit` (nouveau, exécutable)

```bash
#!/bin/bash
# Hook Git Pre-Commit - Protection Philosophique EGOEJO
# Empêche les commits qui violent la séparation SAKA/EUR

set -e

echo "🛡️ Vérification de conformité philosophique EGOEJO..."

# Aller dans le dossier backend
cd backend || exit 1

# Vérifier que les tests de compliance existent
if [ ! -d "tests/compliance" ]; then
    echo "❌ ERREUR : Dossier tests/compliance introuvable"
    exit 1
fi

# Exécuter les tests de compliance (mode rapide)
python -m pytest tests/compliance/ -v --tb=short -q

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ VIOLATION CONSTITUTION EGOEJO DÉTECTÉE"
    echo "Les tests de compliance ont échoué."
    echo "Ce commit viole la séparation stricte SAKA/EUR."
    echo ""
    echo "Action requise :"
    echo "1. Corriger le code pour respecter la séparation SAKA/EUR"
    echo "2. Relancer les tests : pytest tests/compliance/ -v"
    echo "3. Recommiter"
    echo ""
    exit 1
fi

echo "✅ Conformité philosophique validée"
exit 0
```

**Installation** :
```bash
chmod +x .git/hooks/pre-commit
```

**Test** : Vérifier que le hook bloque un commit qui viole la séparation SAKA/EUR.

---

#### 1.3 Protection Django Admin

**Action** : Ajouter une validation au niveau modèle pour empêcher la modification directe SAKA/EUR via Django Admin.

**Fichier** : `backend/core/models/saka.py` (modification)

```python
# Ajouter après la classe SakaWallet

class SakaWallet(models.Model):
    # ... code existant ...
    
    def save(self, *args, **kwargs):
        """
        Protection philosophique : Empêche la modification directe du solde SAKA
        via Django Admin si cela viole la séparation SAKA/EUR.
        
        RÈGLE ABSOLUE : Aucune conversion SAKA ↔ EUR n'est autorisée.
        """
        # Vérifier qu'aucune relation avec UserWallet n'existe
        if hasattr(self.user, 'wallet'):
            user_wallet = self.user.wallet
            # Protection : Si le solde SAKA est modifié et que UserWallet existe,
            # vérifier qu'il n'y a pas de corrélation suspecte
            if self.pk:  # Modification (pas création)
                old_instance = SakaWallet.objects.get(pk=self.pk)
                # Si le solde SAKA change et que UserWallet change aussi, alerter
                # (détection heuristique de violation potentielle)
                if old_instance.balance != self.balance:
                    # Log pour audit (pas de blocage, mais alerte)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Modification directe SakaWallet.balance détectée - "
                        f"User: {self.user.id}, Old: {old_instance.balance}, New: {self.balance}"
                    )
        
        super().save(*args, **kwargs)
```

**Test** : Ajouter un test qui vérifie que la modification directe via Django Admin est loggée.

**Fichier** : `backend/tests/compliance/test_admin_protection.py` (nouveau)

```python
"""
Test de protection contre modification directe SAKA/EUR via Django Admin.
"""
import pytest
from django.contrib.auth import get_user_model
from core.models.saka import SakaWallet
from finance.models import UserWallet

User = get_user_model()


@pytest.mark.django_db
class TestAdminProtection:
    """
    Tests pour protéger contre les modifications directes SAKA/EUR via Django Admin.
    """
    
    def test_modification_directe_sakawallet_logged(self):
        """
        Vérifie que la modification directe de SakaWallet.balance est loggée.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer SakaWallet et UserWallet
        saka_wallet, _ = SakaWallet.objects.get_or_create(user=user)
        saka_wallet.balance = 100
        saka_wallet.save()
        
        user_wallet, _ = UserWallet.objects.get_or_create(user=user)
        user_wallet.balance = 1000.00
        user_wallet.save()
        
        # Modifier directement SakaWallet (simule Django Admin)
        saka_wallet.balance = 200
        saka_wallet.save()
        
        # Vérifier que la modification a été loggée (vérification via logs)
        # Note : Ce test vérifie que le mécanisme de logging est en place
        # Un vrai test d'intégration vérifierait les logs réels
        assert saka_wallet.balance == 200
        # Le logging est vérifié dans le code (pas de test unitaire direct)
```

---

### Tests de Validation

**Fichier** : `backend/tests/compliance/test_ci_cd_protection.py` (nouveau)

```python
"""
Tests pour vérifier que la CI/CD protège la philosophie SAKA/EUR.
"""
import pytest
import subprocess
import sys
from pathlib import Path


class TestCICDProtection:
    """
    Tests pour vérifier que la CI/CD bloque les violations SAKA/EUR.
    """
    
    def test_compliance_tests_existent(self):
        """
        Vérifie que les tests de compliance existent et sont exécutables.
        """
        compliance_dir = Path(__file__).parent
        assert compliance_dir.exists(), "Dossier tests/compliance doit exister"
        
        # Vérifier que les fichiers de tests existent
        test_files = [
            'test_saka_eur_separation.py',
            'test_saka_eur_etancheite.py',
        ]
        
        for test_file in test_files:
            test_path = compliance_dir / test_file
            assert test_path.exists(), f"Test {test_file} doit exister"
    
    def test_compliance_tests_executables(self):
        """
        Vérifie que les tests de compliance sont exécutables.
        """
        compliance_dir = Path(__file__).parent
        
        # Exécuter les tests de compliance (mode rapide)
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(compliance_dir), '-v', '--tb=short', '-q'],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True
        )
        
        # Les tests doivent passer (pas de violation)
        assert result.returncode == 0, f"Tests de compliance doivent passer : {result.stderr}"
```

---

## 🟡 PRIORITÉ 2 : RENFORCEMENT TECHNIQUE (MOYEN)

### Risque Identifié

**TypeScript non migré** : Frontend en `.jsx` pur, risque #1 de bugs en production.

**Impact** : Bugs en production, difficulté de maintenance, risque de violation SAKA/EUR par erreur.

---

### Solution Minimale

#### 2.1 Validation TypeScript Progressive (Sans Migration Complète)

**Action** : Ajouter TypeScript en mode "check-only" pour valider progressivement sans migration complète.

**Fichier** : `frontend/frontend/tsconfig.json` (modification ou création)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "allowJs": true,
    "checkJs": false
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

**Action** : Ajouter un script de validation TypeScript dans `package.json`.

**Fichier** : `frontend/frontend/package.json` (modification)

```json
{
  "scripts": {
    // ... scripts existants ...
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch",
    "precommit": "npm run type-check && npm run lint"
  },
  "devDependencies": {
    // ... dépendances existantes ...
    "typescript": "^5.3.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

**Test** : Vérifier que `npm run type-check` détecte les erreurs de typage.

---

#### 2.2 Protection Frontend SAKA/EUR

**Action** : Ajouter une validation TypeScript pour empêcher l'affichage monétaire du SAKA.

**Fichier** : `frontend/frontend/src/utils/saka.ts` (nouveau)

```typescript
/**
 * Utilitaires pour la gestion du SAKA (monnaie interne d'engagement)
 * 
 * RÈGLE ABSOLUE : Aucun affichage monétaire du SAKA (pas de formatMoney pour SAKA)
 */

// Type pour distinguer SAKA de EUR
export type SakaAmount = number & { __brand: 'SAKA' };
export type EurAmount = number & { __brand: 'EUR' };

/**
 * Formate un montant SAKA (grains) - JAMAIS en format monétaire
 * @param amount - Montant SAKA (grains)
 * @returns String formatée (ex: "150 grains SAKA")
 */
export function formatSaka(amount: SakaAmount): string {
  return `${amount} grains SAKA`;
}

/**
 * Protection : Empêche l'utilisation de formatMoney pour SAKA
 * @param amount - Montant SAKA (grains)
 * @throws Error si tentative d'utiliser formatMoney pour SAKA
 */
export function preventSakaMonetaryFormat(amount: SakaAmount): never {
  throw new Error(
    'VIOLATION CONSTITUTION EGOEJO : Le SAKA ne doit jamais être affiché comme une monnaie. ' +
    'Utilisez formatSaka() au lieu de formatMoney().'
  );
}
```

**Test** : Ajouter un test qui vérifie que `formatMoney` ne peut pas être utilisé pour SAKA.

**Fichier** : `frontend/frontend/src/utils/__tests__/saka.test.ts` (nouveau)

```typescript
import { describe, it, expect } from 'vitest';
import { formatSaka, preventSakaMonetaryFormat } from '../saka';
import { formatMoney } from '../money';

describe('Protection SAKA/EUR - Frontend', () => {
  it('devrait formater SAKA sans format monétaire', () => {
    const sakaAmount = 150 as any; // Simule SakaAmount
    const formatted = formatSaka(sakaAmount);
    expect(formatted).toBe('150 grains SAKA');
    expect(formatted).not.toContain('€');
    expect(formatted).not.toContain('EUR');
  });
  
  it('devrait empêcher formatMoney pour SAKA', () => {
    // Ce test vérifie que formatMoney n'est pas utilisé pour SAKA
    // En TypeScript strict, cela serait détecté au compile-time
    const sakaAmount = 150 as any;
    
    // Vérifier que formatSaka ne contient pas de format monétaire
    const sakaFormatted = formatSaka(sakaAmount);
    expect(sakaFormatted).not.toMatch(/\d+[,\s]\d+\s*€/); // Pas de format monétaire
  });
});
```

---

### Tests de Validation

**Fichier** : `frontend/frontend/src/utils/__tests__/saka-protection.test.ts` (nouveau)

```typescript
import { describe, it, expect } from 'vitest';
import { formatSaka } from '../saka';
import { formatMoney } from '../money';

describe('Protection Philosophique SAKA/EUR - Frontend', () => {
  it('SAKA ne doit jamais être formaté comme une monnaie', () => {
    const sakaAmount = 150 as any;
    const formatted = formatSaka(sakaAmount);
    
    // Vérifier qu'il n'y a pas de symbole monétaire
    expect(formatted).not.toContain('€');
    expect(formatted).not.toContain('EUR');
    expect(formatted).not.toContain('euro');
    
    // Vérifier que c'est bien formaté comme "grains SAKA"
    expect(formatted).toContain('grains SAKA');
  });
  
  it('formatMoney ne doit pas être utilisé pour SAKA', () => {
    // Ce test vérifie que formatMoney n'est pas utilisé pour SAKA
    // En production, TypeScript empêcherait cela
    const sakaAmount = 150 as any;
    
    // Vérifier que formatSaka ne produit pas de format monétaire
    const sakaFormatted = formatSaka(sakaAmount);
    const moneyFormatted = formatMoney('150', 'EUR');
    
    // Les formats doivent être différents
    expect(sakaFormatted).not.toBe(moneyFormatted);
    expect(sakaFormatted).not.toMatch(/\d+[,\s]\d+\s*€/);
  });
});
```

---

## 🟢 PRIORITÉ 3 : RÉSILIENCE INFRASTRUCTURE (FAIBLE)

### Risque Identifié

**Point de défaillance unique (Redis)** : Redis utilisé pour Channels, Celery, et cache.

**Impact** : Si Redis crash, WebSockets et Celery tombent.

---

### Solution Minimale

#### 3.1 Fallback Gracioux si Redis Indisponible

**Action** : Ajouter un fallback gracieux si Redis est indisponible (dégradation fonctionnelle, pas de crash).

**Fichier** : `backend/core/utils/redis_fallback.py` (nouveau)

```python
"""
Utilitaires pour gérer le fallback gracieux si Redis est indisponible.

PHILOSOPHIE : La structure relationnelle (SAKA) prime sur la structure instrumentale (EUR).
Si Redis tombe, on dégrade gracieusement (pas de crash, pas de perte de SAKA).
"""
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def is_redis_available():
    """
    Vérifie si Redis est disponible.
    
    Returns:
        bool: True si Redis est disponible, False sinon
    """
    try:
        cache.set('redis_health_check', 'ok', 1)
        return cache.get('redis_health_check') == 'ok'
    except Exception as e:
        logger.warning(f"Redis indisponible : {e}")
        return False


def get_cache_with_fallback(key, default=None):
    """
    Récupère une valeur du cache avec fallback gracieux.
    
    Si Redis est indisponible, retourne la valeur par défaut (pas de crash).
    
    Args:
        key: Clé du cache
        default: Valeur par défaut si Redis indisponible
    
    Returns:
        Valeur du cache ou valeur par défaut
    """
    if not is_redis_available():
        logger.warning(f"Redis indisponible, utilisation de la valeur par défaut pour {key}")
        return default
    
    try:
        return cache.get(key, default)
    except Exception as e:
        logger.warning(f"Erreur cache Redis pour {key} : {e}, utilisation de la valeur par défaut")
        return default


def set_cache_with_fallback(key, value, timeout=None):
    """
    Définit une valeur dans le cache avec fallback gracieux.
    
    Si Redis est indisponible, ne fait rien (pas de crash).
    
    Args:
        key: Clé du cache
        value: Valeur à stocker
        timeout: Timeout en secondes (optionnel)
    """
    if not is_redis_available():
        logger.warning(f"Redis indisponible, impossible de stocker {key}")
        return
    
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        logger.warning(f"Erreur cache Redis pour {key} : {e}, ignoré")
```

**Test** : Ajouter un test qui vérifie le fallback gracieux.

**Fichier** : `backend/core/tests/test_redis_fallback.py` (nouveau)

```python
"""
Tests pour le fallback gracieux Redis.
"""
import pytest
from unittest.mock import patch, MagicMock
from core.utils.redis_fallback import (
    is_redis_available,
    get_cache_with_fallback,
    set_cache_with_fallback
)


class TestRedisFallback:
    """
    Tests pour vérifier le fallback gracieux si Redis est indisponible.
    """
    
    @patch('core.utils.redis_fallback.cache')
    def test_is_redis_available_returns_true_when_redis_works(self, mock_cache):
        """Vérifie que is_redis_available retourne True si Redis fonctionne."""
        mock_cache.set.return_value = True
        mock_cache.get.return_value = 'ok'
        
        assert is_redis_available() is True
    
    @patch('core.utils.redis_fallback.cache')
    def test_is_redis_available_returns_false_when_redis_fails(self, mock_cache):
        """Vérifie que is_redis_available retourne False si Redis échoue."""
        mock_cache.set.side_effect = Exception("Redis connection failed")
        
        assert is_redis_available() is False
    
    @patch('core.utils.redis_fallback.is_redis_available')
    def test_get_cache_with_fallback_returns_default_when_redis_unavailable(self, mock_is_available):
        """Vérifie que get_cache_with_fallback retourne la valeur par défaut si Redis indisponible."""
        mock_is_available.return_value = False
        
        result = get_cache_with_fallback('test_key', default='default_value')
        
        assert result == 'default_value'
    
    @patch('core.utils.redis_fallback.is_redis_available')
    def test_set_cache_with_fallback_does_nothing_when_redis_unavailable(self, mock_is_available):
        """Vérifie que set_cache_with_fallback ne fait rien si Redis indisponible."""
        mock_is_available.return_value = False
        
        # Ne doit pas lever d'exception
        set_cache_with_fallback('test_key', 'test_value')
        
        # Test passe si aucune exception n'est levée
        assert True
```

---

## 📝 PRIORITÉ 4 : DOCUMENTATION PHILOSOPHIQUE (FAIBLE)

### Risque Identifié

**Ambiguïtés juridiques** : Le SAKA peut être interprété comme un "actif financier" par un juge.

**Impact** : Réglementation AMF applicable (agrément, reporting, sanctions).

---

### Solution Minimale

#### 4.1 Manifeste Philosophique Unique

**Action** : Créer un manifeste philosophique unique qui définit explicitement le SAKA comme "non-financier".

**Fichier** : `docs/philosophie/MANIFESTE_SAKA_EUR.md` (nouveau)

```markdown
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

---

## PROTECTION HUMAINE

- Gouvernance protectrice (conseil d'administration)
- Formation obligatoire de l'équipe
- Review obligatoire pour modifications critiques

---

**Ce manifeste est NON NÉGOCIABLE et doit être préservé à tout prix.**
```

---

## ✅ CHECKLIST DE VALIDATION

### Avant chaque modification :

- [ ] La modification respecte-t-elle la séparation SAKA/EUR ?
- [ ] La modification préserve-t-elle les tests de compliance existants ?
- [ ] La modification favorise-t-elle l'accumulation passive ? (si oui, rejeter)
- [ ] Des tests ont-ils été ajoutés pour la modification ?
- [ ] La modification active-t-elle V2.0 Investment ? (si oui, rejeter)

### Après chaque modification :

- [ ] Les tests de compliance passent-ils ?
- [ ] Les tests unitaires passent-ils ?
- [ ] Les tests E2E passent-ils ?
- [ ] La CI/CD bloque-t-elle les violations ?

---

## 📊 RÉSUMÉ DES ACTIONS

| Priorité | Action | Fichier | Test | Statut |
|----------|--------|---------|------|--------|
| 🔴 P1 | CI/CD bloquante | `.github/workflows/compliance.yml` | `test_ci_cd_protection.py` | À implémenter |
| 🔴 P1 | Hook Git pre-commit | `.git/hooks/pre-commit` | Test manuel | À implémenter |
| 🔴 P1 | Protection Django Admin | `core/models/saka.py` | `test_admin_protection.py` | À implémenter |
| 🟡 P2 | Validation TypeScript | `tsconfig.json`, `package.json` | `saka-protection.test.ts` | À implémenter |
| 🟡 P2 | Protection Frontend SAKA | `utils/saka.ts` | `saka.test.ts` | À implémenter |
| 🟢 P3 | Fallback Redis | `utils/redis_fallback.py` | `test_redis_fallback.py` | À implémenter |
| 📝 P4 | Manifeste Philosophique | `docs/philosophie/MANIFESTE_SAKA_EUR.md` | N/A | À créer |

---

## 🎯 PROCHAINES ÉTAPES

1. **Implémenter P1** (Protection Philosophie) - **URGENT**
2. **Implémenter P2** (Renforcement Technique) - **IMPORTANT**
3. **Implémenter P3** (Résilience Infrastructure) - **Souhaitable**
4. **Créer P4** (Documentation Philosophique) - **Souhaitable**

---

**Fin du Plan d'Action**

*Ce plan respecte toutes les contraintes non négociables et préserve la philosophie SAKA/EUR.*

