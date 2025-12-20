# 🛡️ GUIDE : SÉPARATION SAKA/EUR
## Patterns Autorisés et Interdits

**Document** : Guide développeur pour garantir la séparation SAKA/EUR  
**Date** : 2025-12-19  
**Version** : 1.0  
**Audience** : Développeurs EGOEJO

---

## 🚫 INTERDICTIONS ABSOLUES

### 1. Jointures SQL SAKA/EUR

**❌ INTERDIT** :
```python
# ❌ INTERDIT : Jointure entre SakaWallet et UserWallet
from core.models.saka import SakaWallet
from finance.models import UserWallet

# ❌ INTERDIT
SakaWallet.objects.filter(user__wallet__balance__gt=100)

# ❌ INTERDIT
UserWallet.objects.filter(user__saka_wallet__balance__gt=50)

# ❌ INTERDIT : Requête SQL brute
cursor.execute("""
    SELECT sw.*, uw.*
    FROM core_sakawallet sw
    JOIN finance_userwallet uw ON sw.user_id = uw.user_id
""")
```

**✅ AUTORISÉ** :
```python
# ✅ AUTORISÉ : Requêtes séparées
saka_wallets = SakaWallet.objects.filter(balance__gt=100)
user_wallets = UserWallet.objects.filter(balance__gt=100)

# ✅ AUTORISÉ : Via user (mais pas de fusion de données)
user = User.objects.get(id=1)
saka_balance = user.saka_wallet.balance  # OK
eur_balance = user.wallet.balance  # OK
# Mais JAMAIS de calcul combiné ou de fusion
```

---

### 2. Serializers Fusionnant SAKA/EUR

**❌ INTERDIT** :
```python
# ❌ INTERDIT : Serializer fusionnant SAKA et EUR
class UserBalanceSerializer(serializers.Serializer):
    saka_balance = serializers.IntegerField(source='saka_wallet.balance')
    eur_balance = serializers.DecimalField(source='wallet.balance')
    total_balance = serializers.SerializerMethodField()  # ❌ INTERDIT
    
    def get_total_balance(self, obj):
        # ❌ INTERDIT : Calcul combiné
        return obj.saka_wallet.balance + obj.wallet.balance
```

**✅ AUTORISÉ** :
```python
# ✅ AUTORISÉ : Serializers séparés
class SakaBalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField()
    total_harvested = serializers.IntegerField()
    total_planted = serializers.IntegerField()
    # Pas de référence à EUR

class EurBalanceSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    # Pas de référence à SAKA
```

---

### 3. Vues API Fusionnant SAKA/EUR

**❌ INTERDIT** :
```python
# ❌ INTERDIT : Endpoint fusionnant SAKA et EUR
class CombinedBalanceView(APIView):
    def get(self, request):
        user = request.user
        # ❌ INTERDIT : Fusion de données
        return Response({
            'saka': user.saka_wallet.balance,
            'eur': user.wallet.balance,
            'total': user.saka_wallet.balance + user.wallet.balance  # ❌
        })
```

**✅ AUTORISÉ** :
```python
# ✅ AUTORISÉ : Endpoints séparés
class SakaBalanceView(APIView):
    def get(self, request):
        wallet = request.user.saka_wallet
        return Response({
            'balance': wallet.balance,
            'total_harvested': wallet.total_harvested,
            # Pas de référence à EUR
        })

class EurBalanceView(APIView):
    def get(self, request):
        wallet = request.user.wallet
        return Response({
            'balance': wallet.balance,
            # Pas de référence à SAKA
        })
```

---

### 4. Conversion SAKA ↔ EUR

**❌ INTERDIT** :
```python
# ❌ INTERDIT : Toute fonction de conversion
def convert_saka_to_eur(saka_amount):
    rate = 0.01  # ❌ INTERDIT
    return saka_amount * rate

def convert_eur_to_saka(eur_amount):
    rate = 100  # ❌ INTERDIT
    return eur_amount * rate
```

**✅ AUTORISÉ** :
```python
# ✅ AUTORISÉ : Fonctions séparées
def get_saka_balance(user):
    return user.saka_wallet.balance  # Pas de conversion

def get_eur_balance(user):
    return user.wallet.balance  # Pas de conversion
```

---

### 5. Affichage Monétaire du SAKA

**❌ INTERDIT** :
```python
# ❌ INTERDIT : Affichage avec symbole monétaire
f"{saka_balance} €"  # ❌
f"${saka_balance}"  # ❌
f"{saka_balance} euros"  # ❌
```

**✅ AUTORISÉ** :
```python
# ✅ AUTORISÉ : Affichage en grains
f"{saka_balance} grains SAKA"  # ✅
f"{saka_balance} 🌾"  # ✅
```

---

### 6. Calculs de Rendement Financier sur SAKA

**❌ INTERDIT** :
```python
# ❌ INTERDIT : ROI, yield, intérêt sur SAKA
def calculate_saka_roi(saka_balance, days):
    interest_rate = 0.05  # ❌
    return saka_balance * (interest_rate / 365) * days

def calculate_saka_yield(saka_balance):
    yield_rate = 0.03  # ❌
    return saka_balance * yield_rate
```

**✅ AUTORISÉ** :
```python
# ✅ AUTORISÉ : Calculs de cycle SAKA (non financiers)
def calculate_compost_amount(saka_balance, inactivity_days):
    if inactivity_days > 90:
        return int(saka_balance * 0.1)  # 10% compostage
    return 0
```

---

## ✅ PATTERNS AUTORISÉS

### 1. Accès Séparés

```python
# ✅ AUTORISÉ : Accès séparés via user
user = request.user
saka_balance = user.saka_wallet.balance
eur_balance = user.wallet.balance

# ✅ AUTORISÉ : Utilisation séparée
if saka_balance > 100:
    spend_saka(user, 50, "project_boost")

if eur_balance > 100:
    pledge_funds(user, project, 50, pledge_type='DONATION')
```

---

### 2. Serializers Séparés

```python
# ✅ AUTORISÉ : Serializers complètement séparés
class SakaWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = SakaWallet
        fields = ['balance', 'total_harvested', 'total_planted']
        # Pas de référence à UserWallet

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ['balance']
        # Pas de référence à SakaWallet
```

---

### 3. Endpoints API Séparés

```python
# ✅ AUTORISÉ : Endpoints séparés
urlpatterns = [
    path('saka/balance/', SakaBalanceView.as_view()),  # SAKA uniquement
    path('finance/wallet/', EurBalanceView.as_view()),  # EUR uniquement
    # Pas d'endpoint combiné
]
```

---

### 4. Services Séparés

```python
# ✅ AUTORISÉ : Services dans modules séparés
# core/services/saka.py
def harvest_saka(user, reason, amount):
    # Logique SAKA uniquement
    pass

# finance/services.py
def pledge_funds(user, project, amount, pledge_type):
    # Logique EUR uniquement
    pass
```

---

## 🔍 VÉRIFICATIONS AVANT COMMIT

### Checklist Développeur

Avant de commiter du code, vérifier :

- [ ] Aucune jointure SQL entre `SakaWallet` et `UserWallet`
- [ ] Aucun serializer fusionnant SAKA et EUR
- [ ] Aucun endpoint API combinant SAKA et EUR
- [ ] Aucune fonction de conversion SAKA ↔ EUR
- [ ] Aucun affichage monétaire du SAKA (€, $)
- [ ] Aucun calcul de rendement financier sur SAKA
- [ ] Tests compliance passent (53/53)

---

### Commandes de Vérification

```bash
# Audit automatique
python tools/audit_saka_eur_separation.py

# Tests compliance
python -m pytest backend/tests/compliance/ -v

# Guardian CI/CD
python .egoejo/guardian.py
```

---

## 🚨 EN CAS DE VIOLATION

### Procédure

1. **Détection** : Guardian CI/CD bloque automatiquement
2. **Correction** : Séparer le code SAKA et EUR
3. **Vérification** : Relancer les tests compliance
4. **Commit** : Une fois tous les tests passent

---

## 📚 RÉFÉRENCES

- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Tests Compliance** : `backend/tests/compliance/`
- **Guardian Script** : `.egoejo/guardian.py`
- **Migration 0027** : `backend/core/migrations/0027_add_saka_eur_separation_constraint.py`

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Guide développeur**

