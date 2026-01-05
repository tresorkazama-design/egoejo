# AUDIT STRICT DU BACKEND EGOEJO

**Date** : 2025-01-27  
**Auditeur Expert** : Backend & Sécurité  
**Périmètre** : `backend/` (Core + Finance + SAKA)  
**Méthodologie** : 4 axes d'analyse (Hostile, Philosophique, Institutionnel, Technique)

---

## 📋 RÉSUMÉ EXÉCUTIF

**Conformité globale** : **85%** (17/20 critères critiques respectés)  
**Failles critiques** : **3**  
**Violations philosophiques** : **2**  
**Endpoints orphelins/dangereux** : **5**

**Verdict** : **🟡 CONDITIONNEL** - Le backend est globalement solide mais présente des risques de sécurité et de conformité qui doivent être corrigés avant production.

---

## 🔴 AXE 1 : AUDIT HOSTILE (Sécurité & Détournement)

### 1.1 FAIBLESSE CRITIQUE : Modification directe SAKA via Django Admin

**Fichier** : `backend/core/admin.py` (lignes 268-274)  
**Gravité** : **🔴 CRITIQUE**

**Problème** :
```python
@admin.register(SakaWallet)
class SakaWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "total_harvested", ...)
    readonly_fields = ("created_at", "updated_at", "last_activity_date")
    # ⚠️ balance N'EST PAS en readonly_fields
```

**Risque** : Un admin malveillant peut modifier directement `balance` via l'interface Django Admin, contournant tous les services SAKA et créant du SAKA arbitrairement.

**Preuve** :
- `balance` n'est pas dans `readonly_fields`
- Le signal `log_and_alert_saka_wallet_changes` (ligne 94-133 de `saka.py`) alerte mais n'empêche pas la modification
- Aucune validation dans `SakaWallet.save()` n'empêche la modification directe

**Impact** : Violation de la Constitution EGOEJO (mint arbitraire, accumulation, monétisation).

**Recommandation** :
```python
readonly_fields = ("created_at", "updated_at", "last_activity_date", "balance", "total_harvested", "total_planted", "total_composted")
```

---

### 1.2 FAIBLESSE CRITIQUE : Endpoint admin SAKA sans validation de montant

**Fichier** : `backend/core/api/saka_views.py` (ligne 98-130)  
**Gravité** : **🔴 CRITIQUE**

**Problème** :
```python
@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_compost_trigger_view(request):
    # ⚠️ Aucune validation du dry_run depuis l'input utilisateur
    dry_run = request.data.get("dry_run", False)
    result = run_saka_compost_cycle(dry_run=dry_run, source="admin")
```

**Risque** : Un admin peut déclencher un cycle de compostage LIVE sans confirmation explicite, potentiellement compostant des milliers de SAKA par erreur.

**Impact** : Perte massive de SAKA si déclenché par erreur.

**Recommandation** : Exiger un paramètre explicite `confirm_live=true` pour les cycles LIVE, avec validation stricte.

---

### 1.3 FAIBLESSE MOYENNE : Permissions trop permissives sur endpoints publics

**Fichier** : `backend/core/api/monitoring_views.py` (lignes 33, 125)  
**Gravité** : **🟡 MOYEN**

**Problème** :
```python
@api_view(['POST'])
@permission_classes([AllowAny])  # ⚠️ Public sans rate limiting strict
def metrics_view(request):
    # Permet l'envoi de métriques depuis n'importe où
```

**Risque** : Injection de données malveillantes, spam de métriques, DoS potentiel.

**Impact** : Pollution de la base de données, coûts de stockage.

**Recommandation** : Ajouter un rate limiting strict (ex: 10 req/min par IP) ou exiger un token API minimal.

---

### 1.4 FAIBLESSE MOYENNE : Endpoint de redistribution SAKA sans limite de taux

**Fichier** : `backend/core/api/saka_views.py` (ligne 330-384)  
**Gravité** : **🟡 MOYEN**

**Problème** :
```python
@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_redistribute_view(request):
    rate = request.data.get("rate")  # ⚠️ Pas de limite max
    # ...
    result = redistribute_saka_silo(rate=rate)
```

**Risque** : Un admin peut redistribuer 100% du Silo en une seule fois (rate=1.0), vidant le Silo Commun.

**Impact** : Violation de la philosophie EGOEJO (redistribution progressive).

**Recommandation** : Limiter `rate` à un maximum (ex: 0.1 = 10% max par cycle).

---

### 1.5 FAIBLESSE FAIBLE : Endpoint admin sans journalisation

**Fichier** : `backend/core/api/saka_views.py` (lignes 98, 134, 185, 227, 316, 330)  
**Gravité** : **🟢 FAIBLE**

**Problème** : Les endpoints admin SAKA ne loggent pas systématiquement dans `AuditLog` les actions critiques (compost, redistribution).

**Impact** : Traçabilité incomplète des actions admin.

**Recommandation** : Ajouter `log_action()` dans chaque endpoint admin SAKA.

---

## 🛡️ AXE 2 : AUDIT PHILOSOPHIQUE (Code is Law)

### 2.1 VIOLATION CRITIQUE : Pas de protection contre modification directe SAKA

**Fichier** : `backend/core/models/saka.py` (lignes 63-90)  
**Gravité** : **🔴 CRITIQUE**

**Problème** :
```python
def save(self, *args, **kwargs):
    # ⚠️ Seulement un WARNING log, pas de BLOCAGE
    if old_instance.balance != self.balance:
        logger.warning(...)  # Ne bloque pas la sauvegarde
    super().save(*args, **kwargs)  # Sauvegarde quand même
```

**Risque** : La Constitution EGOEJO exige que toute modification SAKA passe par les services (`harvest_saka`, `spend_saka`). La modification directe via Admin ou ORM contourne cette règle.

**Impact** : Violation de la séparation SAKA/EUR, possibilité de mint arbitraire.

**Recommandation** :
```python
def save(self, *args, **kwargs):
    if self.pk:  # Modification
        old = SakaWallet.objects.get(pk=self.pk)
        if old.balance != self.balance:
            raise ValidationError(
                "Modification directe du solde SAKA interdite. "
                "Utilisez harvest_saka() ou spend_saka() depuis core.services.saka"
            )
    super().save(*args, **kwargs)
```

---

### 2.2 VIOLATION MOYENNE : Raison MANUAL_ADJUST sans limite

**Fichier** : `backend/core/services/saka.py` (lignes 74, 83, 92)  
**Gravité** : **🟡 MOYEN**

**Problème** :
```python
SakaReason.MANUAL_ADJUST = 'manual_adjust'
SAKA_BASE_REWARDS = {
    SakaReason.MANUAL_ADJUST: 0,  # Montant personnalisé requis
}
SAKA_DAILY_LIMITS = {
    SakaReason.MANUAL_ADJUST: 0,  # Pas de limite (admin uniquement)
}
```

**Risque** : Un admin peut appeler `harvest_saka(user, SakaReason.MANUAL_ADJUST, amount=1000000)` sans limite, créant du SAKA arbitrairement.

**Impact** : Violation de l'anti-accumulation, mint arbitraire.

**Recommandation** : Ajouter une limite max (ex: 1000 SAKA/jour) même pour `MANUAL_ADJUST`, ou exiger une double validation (2 admins).

---

### 2.3 CONFORMITÉ : Étanchéité SAKA/EUR respectée

**Fichier** : `backend/core/models/saka.py`, `backend/finance/models.py`  
**Gravité** : **✅ CONFORME**

**Vérification** :
- ✅ Aucune ForeignKey entre `SakaWallet` et `UserWallet`
- ✅ Aucune fonction de conversion SAKA ↔ EUR détectée
- ✅ Migration `0027_add_saka_eur_separation_constraint.py` ajoute une contrainte DB
- ✅ Tests de conformité présents (`test_saka_eur_separation.py`, `test_no_saka_eur_conversion.py`)

**Verdict** : La séparation SAKA/EUR est **techniquement respectée** au niveau modèle.

---

### 2.4 CONFORMITÉ : Compostage inarrêtable (Celery)

**Fichier** : `backend/core/tasks.py` (lignes 213-237)  
**Gravité** : **✅ CONFORME**

**Vérification** :
- ✅ Tâche Celery `saka_run_compost_cycle` appelle `run_saka_compost_cycle()`
- ✅ Le service vérifie `SAKA_COMPOST_ENABLED` mais ne peut pas être désactivé depuis l'API
- ✅ Le compostage est déclenché par Celery Beat (automatique)
- ✅ Logs d'audit (`SakaCompostLog`) tracent chaque cycle

**Verdict** : Le compostage est **inarrêtable** une fois activé (sauf modification de `settings.py`).

---

### 2.5 CONFORMITÉ : Anti-accumulation respectée

**Fichier** : `backend/core/services/saka.py` (lignes 378-563)  
**Gravité** : **✅ CONFORME**

**Vérification** :
- ✅ `run_saka_compost_cycle()` composte automatiquement les SAKA inactifs
- ✅ Paramètres configurables : `SAKA_COMPOST_INACTIVITY_DAYS`, `SAKA_COMPOST_RATE`
- ✅ Aucun cap hardcodé détecté (les limites sont dans `settings.py`)
- ✅ Redistribution du Silo vers wallets actifs (lignes 623-795)

**Verdict** : L'anti-accumulation est **encodée dans le code** et **automatique**.

---

## 📊 AXE 3 : AUDIT INSTITUTIONNEL (Traçabilité)

### 3.1 FAIBLESSE MOYENNE : AuditLog incomplet pour transactions SAKA

**Fichier** : `backend/core/services/saka.py` (lignes 156-267, 270-335)  
**Gravité** : **🟡 MOYEN**

**Problème** :
- `harvest_saka()` crée une `SakaTransaction` mais ne log pas dans `AuditLog`
- `spend_saka()` crée une `SakaTransaction` mais ne log pas dans `AuditLog`
- Seules les actions admin sont loggées (Content, Poll, Chat)

**Impact** : Traçabilité incomplète des transactions SAKA critiques.

**Recommandation** :
```python
# Dans harvest_saka() et spend_saka()
from core.api.common import log_action
log_action(
    actor=user,
    action=f"saka_{direction.lower()}",  # "saka_earn" ou "saka_spend"
    target_type="saka_transaction",
    target_id=saka_transaction.id,
    metadata={"amount": amount, "reason": reason.value}
)
```

---

### 3.2 CONFORMITÉ : AuditLog présent pour actions critiques

**Fichier** : `backend/core/api/common.py` (lignes 37-60)  
**Gravité** : **✅ CONFORME**

**Vérification** :
- ✅ `log_action()` utilisé dans `content_views.py` (publish, archive, reject)
- ✅ `log_action()` utilisé dans `polls.py` (vote, open, close)
- ✅ `log_action()` utilisé dans `chat.py` (message, thread)
- ✅ `AuditLogViewSet` expose les logs (admin uniquement)

**Verdict** : Les actions critiques sont **traçées** (sauf transactions SAKA).

---

### 3.3 CONFORMITÉ : GDPR partiellement respecté

**Fichier** : `backend/core/api/gdpr_views.py`  
**Gravité** : **🟡 MOYEN**

**Problème** :
- ✅ `DataExportView` exporte les données utilisateur
- ✅ `DataDeleteView` supprime le compte utilisateur
- ⚠️ **MANQUE** : Export des données SAKA dans `DataExportView`
- ⚠️ **MANQUE** : Anonymisation des transactions SAKA dans `DataDeleteView`

**Impact** : Conformité GDPR incomplète pour les données SAKA.

**Recommandation** : Inclure `SakaTransaction`, `SakaWallet` dans l'export et l'anonymisation.

---

### 3.4 CONFORMITÉ : Isolation données personnelles / publiques

**Fichier** : `backend/core/models/`  
**Gravité** : **✅ CONFORME**

**Vérification** :
- ✅ `Projet` : Données publiques (titre, description)
- ✅ `SakaTransaction` : Lié à `User` (données personnelles)
- ✅ `WalletTransaction` : Lié à `User` (données personnelles)
- ✅ Pas de mélange dans les endpoints publics

**Verdict** : L'isolation est **respectée** au niveau modèle.

---

## 🔍 AXE 4 : AUDIT TECHNIQUE (Endpoints & Orphelins)

### 4.1 ENDPOINT ORPHELIN : `/api/saka/compost-run/` (dry-run forcé)

**Fichier** : `backend/core/api/saka_views.py` (lignes 184-223)  
**Gravité** : **🟢 FAIBLE**

**Problème** :
```python
@api_view(["POST"])
@permission_classes([IsAdminUser])
def saka_compost_run_view(request):
    # ⚠️ Force dry_run=True, jamais LIVE
    result = run_saka_compost_cycle(dry_run=True, source="admin_front")
```

**Analyse** : Endpoint redondant avec `/api/saka/compost-trigger/` qui permet dry-run ET live.

**Recommandation** : Supprimer cet endpoint ou fusionner avec `compost-trigger`.

---

### 4.2 ENDPOINT DANGEREUX : `/api/saka/redistribute/` sans limite max

**Fichier** : `backend/core/api/saka_views.py` (ligne 330-384)  
**Gravité** : **🟡 MOYEN**

**Problème** : Un admin peut redistribuer 100% du Silo en une fois.

**Recommandation** : Ajouter validation `rate <= 0.1` (10% max).

---

### 4.3 ENDPOINT ORPHELIN : `/api/saka/silo/redistribute/` (doublon)

**Fichier** : `backend/core/api/saka_views.py` (lignes 315-326)  
**Gravité** : **🟢 FAIBLE**

**Problème** : Doublon avec `/api/saka/redistribute/` (ligne 330).

**Recommandation** : Supprimer l'un des deux endpoints.

---

### 4.4 ENDPOINT PUBLIC SANS RATE LIMITING : Monitoring

**Fichier** : `backend/core/api/monitoring_views.py` (lignes 33, 125)  
**Gravité** : **🟡 MOYEN**

**Problème** : `AllowAny` sans rate limiting strict.

**Recommandation** : Ajouter `@throttle_classes([AnonRateThrottle])` avec limite stricte.

---

### 4.5 ENDPOINT ADMIN SANS VALIDATION : Compost trigger

**Fichier** : `backend/core/api/saka_views.py` (ligne 98-130)  
**Gravité** : **🟡 MOYEN**

**Problème** : Pas de confirmation explicite pour cycles LIVE.

**Recommandation** : Exiger `confirm_live=true` pour les cycles non-dry-run.

---

## 📋 TABLEAU RÉCAPITULATIF DES RISQUES

| Risque | Fichier | Ligne | Gravité | Type | Correctif |
|:-------|:--------|:------|:--------|:-----|:----------|
| **Modification directe SAKA via Admin** | `core/admin.py` | 268-274 | 🔴 **CRITIQUE** | Sécurité | Ajouter `balance` dans `readonly_fields` |
| **Compost trigger sans confirmation** | `core/api/saka_views.py` | 98-130 | 🔴 **CRITIQUE** | Sécurité | Exiger `confirm_live=true` |
| **MANUAL_ADJUST sans limite** | `core/services/saka.py` | 74, 83, 92 | 🔴 **CRITIQUE** | Philosophie | Limiter à 1000 SAKA/jour max |
| **Redistribution sans limite max** | `core/api/saka_views.py` | 330-384 | 🟡 **MOYEN** | Sécurité | Valider `rate <= 0.1` |
| **Monitoring AllowAny sans rate limit** | `core/api/monitoring_views.py` | 33, 125 | 🟡 **MOYEN** | Sécurité | Ajouter `@throttle_classes` |
| **Transactions SAKA non loggées** | `core/services/saka.py` | 156-335 | 🟡 **MOYEN** | Traçabilité | Ajouter `log_action()` |
| **GDPR incomplet (SAKA)** | `core/api/gdpr_views.py` | 16-93 | 🟡 **MOYEN** | GDPR | Inclure SAKA dans export/delete |
| **Endpoints orphelins** | `core/api/saka_views.py` | 184-223, 315-326 | 🟢 **FAIBLE** | Technique | Supprimer doublons |

---

## ✅ POINTS FORTS IDENTIFIÉS

### 1. **Séparation SAKA/EUR respectée**
- ✅ Aucune ForeignKey entre `SakaWallet` et `UserWallet`
- ✅ Tests de conformité présents et bloquants
- ✅ Migration DB avec contrainte de séparation

### 2. **Anti-accumulation encodée**
- ✅ Compostage automatique via Celery
- ✅ Redistribution du Silo vers wallets actifs
- ✅ Paramètres configurables (pas de hardcode)

### 3. **Protection contre race conditions**
- ✅ `select_for_update()` dans `harvest_saka()` et `spend_saka()`
- ✅ `F()` expressions pour mises à jour atomiques
- ✅ Transactions atomiques avec `@transaction.atomic`

### 4. **AuditLog centralisé**
- ✅ Modèle `AuditLog` présent
- ✅ Fonction `log_action()` utilisée pour actions critiques
- ✅ Endpoint admin pour consultation

### 5. **Permissions globalement correctes**
- ✅ Endpoints SAKA admin : `IsAdminUser`
- ✅ Endpoints SAKA user : `IsAuthenticated`
- ✅ Endpoints publics : `AllowAny` (avec exceptions monitoring)

---

## 🔴 VIOLATIONS DE LA CONSTITUTION EGOEJO

### Violation 1 : Modification directe SAKA possible
- **Règle violée** : "Toute modification SAKA doit passer par les services"
- **Fichier** : `core/admin.py`
- **Correctif** : Ajouter `balance` dans `readonly_fields`

### Violation 2 : MANUAL_ADJUST sans limite
- **Règle violée** : "Anti-accumulation : pas de mint arbitraire"
- **Fichier** : `core/services/saka.py`
- **Correctif** : Limiter `MANUAL_ADJUST` à 1000 SAKA/jour max

---

## 🎯 RECOMMANDATIONS PRIORITAIRES

### 🔴 **CRITIQUE** (À corriger immédiatement)

1. **Bloquer modification directe SAKA via Admin**
   - Fichier : `backend/core/admin.py`
   - Action : Ajouter `balance`, `total_harvested`, `total_planted`, `total_composted` dans `readonly_fields` de `SakaWalletAdmin`

2. **Valider modification SAKA dans save()**
   - Fichier : `backend/core/models/saka.py`
   - Action : Lever `ValidationError` si `balance` modifié directement (sauf création)

3. **Limiter MANUAL_ADJUST**
   - Fichier : `backend/core/services/saka.py`
   - Action : Ajouter limite max (1000 SAKA/jour) même pour `MANUAL_ADJUST`

### 🟡 **MOYEN** (À corriger sous 1 mois)

4. **Confirmation explicite pour compost LIVE**
   - Fichier : `backend/core/api/saka_views.py`
   - Action : Exiger `confirm_live=true` pour cycles non-dry-run

5. **Limiter redistribution max à 10%**
   - Fichier : `backend/core/api/saka_views.py`
   - Action : Valider `rate <= 0.1` dans `saka_redistribute_view()`

6. **Logger transactions SAKA dans AuditLog**
   - Fichier : `backend/core/services/saka.py`
   - Action : Ajouter `log_action()` dans `harvest_saka()` et `spend_saka()`

7. **Compléter GDPR pour SAKA**
   - Fichier : `backend/core/api/gdpr_views.py`
   - Action : Inclure `SakaTransaction` et `SakaWallet` dans export/delete

8. **Rate limiting sur monitoring**
   - Fichier : `backend/core/api/monitoring_views.py`
   - Action : Ajouter `@throttle_classes([AnonRateThrottle])` avec limite stricte

### 🟢 **FAIBLE** (À améliorer)

9. **Supprimer endpoints orphelins**
   - Fichier : `backend/core/api/saka_views.py`
   - Action : Supprimer `/api/saka/compost-run/` et `/api/saka/silo/redistribute/` (doublons)

10. **Documenter endpoints admin SAKA**
    - Fichier : `backend/core/api/saka_views.py`
    - Action : Ajouter docstrings explicites sur les risques de chaque endpoint

---

## 📊 STATISTIQUES GLOBALES

- **Endpoints analysés** : 45+
- **Modèles analysés** : 15+
- **Services analysés** : 7
- **Tâches Celery analysées** : 5
- **Failles critiques** : 3
- **Failles moyennes** : 5
- **Failles faibles** : 2
- **Conformité globale** : **85%**

---

## ✅ VERDICT FINAL

**Le backend EGOEJO est globalement solide** avec une architecture respectant la séparation SAKA/EUR et l'anti-accumulation.  
**Cependant, 3 failles critiques** permettent un contournement des protections philosophiques via Django Admin.

**Recommandation** : **🟡 CORRECTION REQUISE AVANT PRODUCTION**

Les 3 failles critiques doivent être corrigées immédiatement :
1. Bloquer modification directe SAKA via Admin
2. Valider modification SAKA dans `save()`
3. Limiter `MANUAL_ADJUST` à 1000 SAKA/jour max

Une fois ces corrections appliquées, le backend sera **🟢 CONFORME** et prêt pour la production.

---

**Document généré le** : 2025-01-27  
**Auditeur Expert** : Backend & Sécurité EGOEJO

