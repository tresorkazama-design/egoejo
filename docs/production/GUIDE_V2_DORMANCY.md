# 💤 GUIDE : DORMANCE V2.0
## Code Dormant Testable mais Inactif

**Document** : Guide pour gérer le code V2.0 dormant  
**Date** : 2025-12-19  
**Version** : 1.0  
**Audience** : Développeurs EGOEJO

---

## 🎯 PRINCIPE FONDAMENTAL

**Le code V2.0 (Investissement) doit rester testable mais inactif par défaut.**

- ✅ Code présent dans le repository
- ✅ Tests fonctionnent avec `ENABLE_INVESTMENT_FEATURES=True`
- ✅ Code ne s'exécute JAMAIS si `ENABLE_INVESTMENT_FEATURES=False`
- ✅ Activation nécessite conditions strictes (Action G, vote conforme)

---

## 🎛️ LE KILL SWITCH

### Variable d'Environnement

```bash
# Production (V1.6 - Dons uniquement)
ENABLE_INVESTMENT_FEATURES=False

# Tests V2.0 (local uniquement)
ENABLE_INVESTMENT_FEATURES=True
```

### Configuration Django

```python
# backend/config/settings.py
ENABLE_INVESTMENT_FEATURES = os.environ.get('ENABLE_INVESTMENT_FEATURES', 'False').lower() == 'true'
```

**Défaut** : `False` (V1.6 actif, V2.0 dormant)

---

## ✅ PATTERNS AUTORISÉS

### 1. Protection par Feature Flag

**✅ AUTORISÉ** : Vérifier le flag avant exécution

```python
# ✅ AUTORISÉ : Protection explicite
from django.conf import settings

def pledge_funds(user, project, amount, pledge_type='DONATION'):
    # Protection V2.0
    if pledge_type == 'EQUITY' and not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError("L'investissement n'est pas encore ouvert.")
    
    # Logique commune V1.6/V2.0
    wallet = user.wallet
    wallet.balance -= amount
    # ...
```

---

### 2. Endpoints Protégés

**✅ AUTORISÉ** : Permission basée sur feature flag

```python
# ✅ AUTORISÉ : Permission personnalisée
from rest_framework.permissions import BasePermission

class IsInvestmentFeatureEnabled(BasePermission):
    def has_permission(self, request, view):
        return settings.ENABLE_INVESTMENT_FEATURES

# Utilisation
class ShareholderRegisterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsInvestmentFeatureEnabled]
    # Si flag désactivé, retourne 403 automatiquement
```

---

### 3. Tests avec Flag Activé

**✅ AUTORISÉ** : Tests V2.0 avec flag activé

```python
# ✅ AUTORISÉ : Test V2.0 avec flag activé
from django.test import override_settings

@override_settings(ENABLE_INVESTMENT_FEATURES=True)
def test_equity_pledge_when_enabled():
    # Test que le code V2.0 fonctionne si activé
    result = pledge_funds(user, project, 100, pledge_type='EQUITY')
    assert result is not None
```

---

### 4. Tests de Dormance

**✅ AUTORISÉ** : Tests vérifiant que V2.0 est dormant

```python
# ✅ AUTORISÉ : Test de dormance
@override_settings(ENABLE_INVESTMENT_FEATURES=False)
def test_equity_pledge_when_disabled():
    # Test que le code V2.0 ne s'exécute pas si désactivé
    with pytest.raises(ValidationError):
        pledge_funds(user, project, 100, pledge_type='EQUITY')
```

---

## 🚫 INTERDICTIONS

### 1. Code V2.0 Sans Protection

**❌ INTERDIT** : Code V2.0 sans vérification de flag

```python
# ❌ INTERDIT : Code V2.0 sans protection
def create_shareholder(user, project, amount):
    # ❌ S'exécute même si ENABLE_INVESTMENT_FEATURES=False
    ShareholderRegister.objects.create(
        investor=user,
        project=project,
        amount_invested=amount
    )
```

**✅ CORRIGÉ** :
```python
# ✅ CORRIGÉ : Protection explicite
def create_shareholder(user, project, amount):
    if not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError("L'investissement n'est pas encore ouvert.")
    
    ShareholderRegister.objects.create(
        investor=user,
        project=project,
        amount_invested=amount
    )
```

---

### 2. Activation Accidentelle

**❌ INTERDIT** : Activation V2.0 sans conditions

```python
# ❌ INTERDIT : Activation automatique
if user.is_premium:
    ENABLE_INVESTMENT_FEATURES = True  # ❌ INTERDIT
```

**✅ CORRIGÉ** :
```python
# ✅ CORRIGÉ : Flag global uniquement (pas de modification dynamique)
# Le flag est défini dans settings.py uniquement
# Pas de modification dans le code
```

---

### 3. Dépendance SAKA → V2.0

**❌ INTERDIT** : SAKA dépendant de V2.0

```python
# ❌ INTERDIT : SAKA conditionné par V2.0
if settings.ENABLE_INVESTMENT_FEATURES:
    harvest_saka(user, SakaReason.INVEST_BONUS, amount=100)
```

**✅ CORRIGÉ** :
```python
# ✅ CORRIGÉ : SAKA indépendant de V2.0
# SAKA fonctionne toujours, même si V2.0 désactivé
harvest_saka(user, SakaReason.CONTENT_READ, amount=10)
```

---

## 🧪 TESTS D'ISOLATION

### Suite de Tests Complète

**Fichier** : `backend/tests/compliance/test_v2_dormancy.py`

**Tests à inclure** :
1. Test : V2.0 ne s'exécute jamais si `ENABLE_INVESTMENT_FEATURES=False`
2. Test : Tous les endpoints V2.0 retournent 403 si flag désactivé
3. Test : Code V2.0 testable avec flag activé
4. Test : SAKA fonctionne indépendamment de V2.0
5. Test : Activation V2.0 nécessite conditions (Action G, vote conforme)

---

### Exemple de Test

```python
import pytest
from django.test import override_settings
from django.conf import settings

class TestV2Dormancy:
    """Tests de dormance V2.0"""
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_equity_endpoints_return_403_when_disabled(self):
        """Vérifie que les endpoints V2.0 retournent 403 si désactivé"""
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        # Endpoint V2.0
        response = client.get('/api/investment/shareholders/')
        assert response.status_code == 403
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_equity_pledge_raises_error_when_disabled(self):
        """Vérifie que pledge EQUITY échoue si V2.0 désactivé"""
        from finance.services import pledge_funds
        from django.core.exceptions import ValidationError
        
        with pytest.raises(ValidationError, match="n'est pas encore ouvert"):
            pledge_funds(
                self.user,
                self.project,
                100,
                pledge_type='EQUITY'
            )
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=True)
    def test_equity_pledge_works_when_enabled(self):
        """Vérifie que pledge EQUITY fonctionne si V2.0 activé"""
        from finance.services import pledge_funds
        
        # Test que le code V2.0 fonctionne si activé
        result = pledge_funds(
            self.user,
            self.project,
            100,
            pledge_type='EQUITY'
        )
        assert result is not None
    
    @override_settings(ENABLE_INVESTMENT_FEATURES=False)
    def test_saka_works_independently_of_v2(self):
        """Vérifie que SAKA fonctionne même si V2.0 désactivé"""
        from core.services.saka import harvest_saka, SakaReason
        
        # SAKA doit fonctionner indépendamment de V2.0
        result = harvest_saka(self.user, SakaReason.CONTENT_READ, amount=10)
        assert result is not None
```

---

## 🔍 VÉRIFICATIONS

### Checklist Développeur

Avant de commiter du code V2.0 :

- [ ] Tous les accès V2.0 protégés par `ENABLE_INVESTMENT_FEATURES`
- [ ] Tests de dormance présents (flag désactivé)
- [ ] Tests fonctionnels présents (flag activé)
- [ ] SAKA indépendant de V2.0
- [ ] Aucune activation automatique de V2.0

---

### Commandes de Vérification

```bash
# Tests de dormance
python -m pytest backend/tests/compliance/test_bank_dormant.py -v

# Tests d'isolation V2.0
python -m pytest backend/core/tests_investment_isolation.py -v

# Vérifier que le flag est False par défaut
python -c "from django.conf import settings; print(settings.ENABLE_INVESTMENT_FEATURES)"
# Doit afficher : False
```

---

## 🚨 MONITORING DORMANCE

### Endpoint de Monitoring

**Endpoint** : `/api/monitoring/v2-dormancy/`

**Response** :
```json
{
  "v2_enabled": false,
  "dormancy_status": "dormant",
  "last_check": "2025-12-19T10:00:00Z",
  "checks": {
    "feature_flag": {
      "status": "ok",
      "value": false,
      "message": "ENABLE_INVESTMENT_FEATURES=False (dormant)"
    },
    "endpoints": {
      "status": "ok",
      "blocked_endpoints": 3,
      "message": "Tous les endpoints V2.0 retournent 403"
    },
    "database": {
      "status": "ok",
      "shareholders_count": 0,
      "message": "Aucun shareholder enregistré (dormant)"
    }
  }
}
```

---

### Alertes Automatiques

**Si V2.0 activé accidentellement** :
- Email aux admins
- Sentry alert (critique)
- Dashboard notification

**Si tentative d'accès V2.0** :
- Log de sécurité
- Notification (non critique)

---

## 📋 PROCÉDURE D'ACTIVATION V2.0

### Conditions Requises

1. **Agrément AMF** : Obtenu
2. **Vote Conforme** : Majorité qualifiée + Action G
3. **KYC Configuré** : Service tiers opérationnel
4. **Signature Électronique** : Service configuré

### Étapes d'Activation

1. **Vérifier conditions** : Checklist complète
2. **Modifier variable d'environnement** : `ENABLE_INVESTMENT_FEATURES=True`
3. **Déployer** : Via Railway (variable d'env)
4. **Vérifier** : Tests V2.0 passent
5. **Monitorer** : Vérifier fonctionnement

---

## 📚 RÉFÉRENCES

- **Architecture Sleeping Giant** : `docs/architecture/ARCHITECTURE_SLEEPING_GIANT_V1.6_V2.0.md`
- **Tests Isolation** : `backend/core/tests_investment_isolation.py`
- **Tests Dormance** : `backend/tests/compliance/test_bank_dormant.py`
- **Settings** : `backend/config/settings.py` (ligne 470)

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Guide développeur**

