# 🚨 SYSTÈME D'ALERTE EMAIL CRITIQUE EGOEJO

**Date** : 2025-01-03  
**Version** : 1.0  
**Objectif** : Tolérance zéro pour les violations d'intégrité SAKA et autres événements critiques

---

## 🎯 Vue d'Ensemble

Le système d'alerte email critique EGOEJO permet d'envoyer automatiquement des notifications par email aux administrateurs en cas d'événements critiques (violations d'intégrité SAKA, modifications suspectes, etc.).

**Caractéristiques** :
- ✅ Dédoublonnage via cache (5 minutes) pour éviter le spam
- ✅ Payload structuré JSON pour faciliter le traitement automatique
- ✅ Gestion robuste des erreurs SMTP (ne bloque pas l'application)
- ✅ Configuration via variables d'environnement
- ✅ Intégration avec le signal `post_save` de `SakaWallet`

---

## 📁 Architecture

### Fichiers Principaux

- **`backend/core/utils/alerts.py`** : Module central d'alerte
  - Fonction `send_critical_alert()` : Envoie une alerte critique par email
  - Dédoublonnage via cache Django
  - Formatage structuré du message

- **`backend/core/models/saka.py`** : Intégration avec le signal SAKA
  - Signal `log_and_alert_saka_wallet_changes` : Détecte les modifications suspectes
  - Appelle `send_critical_alert()` en cas de violation détectée

- **`backend/config/settings.py`** : Configuration
  - `ALERT_EMAIL_ENABLED` : Activer/désactiver les alertes
  - `ALERT_EMAIL_SUBJECT_PREFIX` : Préfixe du sujet email
  - `ADMINS` : Liste des administrateurs destinataires

---

## 🔧 Configuration

### Variables d'Environnement Requises

```bash
# Configuration SMTP (obligatoire)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=1

# Liste des administrateurs (obligatoire)
# Format JSON : [["Nom", "email@example.com"], ["Nom2", "email2@example.com"]]
ADMINS='[["Admin Name", "admin@example.com"], ["Security Team", "security@example.com"]]'

# Ou format simple : "Nom,email@example.com;Nom2,email2@example.com"
ADMINS="Admin Name,admin@example.com;Security Team,security@example.com"

# Configuration des alertes (optionnel)
ALERT_EMAIL_ENABLED=True  # Par défaut : True
ALERT_EMAIL_SUBJECT_PREFIX="[URGENT] EGOEJO"  # Par défaut : "[URGENT] EGOEJO"
```

### Configuration Django Settings

Les variables d'environnement sont automatiquement chargées dans `backend/config/settings.py` :

```python
# ADMINS : Liste des administrateurs qui recevront les alertes critiques
ADMINS = []  # Configuré via variable d'environnement ADMINS

# ALERTES EMAIL CRITIQUES
ALERT_EMAIL_ENABLED = os.environ.get('ALERT_EMAIL_ENABLED', 'True').lower() == 'true'
ALERT_EMAIL_SUBJECT_PREFIX = os.environ.get('ALERT_EMAIL_SUBJECT_PREFIX', '[URGENT] EGOEJO')
```

---

## 📖 Utilisation

### Fonction `send_critical_alert()`

```python
from core.utils.alerts import send_critical_alert

# Exemple : Alerte de violation d'intégrité SAKA
send_critical_alert(
    title="INTEGRITY BREACH DETECTED",
    payload={
        "violation_type": "saka_wallet_bypass",
        "user_id": 123,
        "username": "testuser",
        "email": "testuser@example.com",
        "old_balance": 1000,
        "new_balance": 2000,
        "delta": 1000,
        "detection_method": "post_save_signal",
        "detection_details": "Aucune SakaTransaction correspondante trouvée",
        "likely_cause": "raw() SQL, update(), ou autre contournement",
        "constitution_violation": "no direct SAKA mutation",
        "action_required": "Vérifier immédiatement l'intégrité des données SAKA"
    },
    dedupe_key="saka_wallet_bypass:123:456"  # Optionnel : dédoublonnage
)
```

### Paramètres

- **`title`** (str, obligatoire) : Titre de l'alerte (utilisé dans le sujet de l'email)
- **`payload`** (dict, obligatoire) : Dictionnaire contenant les données structurées de l'alerte
- **`dedupe_key`** (str, optionnel) : Clé de dédoublonnage. Si fournie, l'alerte ne sera envoyée qu'une fois toutes les 5 minutes pour cette clé
- **`subject_prefix`** (str, optionnel) : Préfixe du sujet. Par défaut : `[URGENT] EGOEJO`

### Retour

- **`True`** : Email envoyé avec succès (ou déjà envoyé récemment si `dedupe_key` fournie)
- **`False`** : Échec d'envoi ou alertes désactivées

---

## 🔍 Détection Automatique des Violations SAKA

Le système d'alerte est automatiquement branché sur le signal `post_save` de `SakaWallet` via la fonction `log_and_alert_saka_wallet_changes()`.

### Scénarios Détectés

1. **Contournement Détecté** (ligne 308 de `saka.py`)
   - **Condition** : Modification du solde SAKA sans `SakaTransaction` correspondante dans les 5 dernières minutes
   - **Cause Probable** : `raw()` SQL, `update()`, ou autre contournement
   - **Alerte** : `INTEGRITY BREACH DETECTED`
   - **Dedupe Key** : `saka_wallet_bypass:{user_id}:{wallet_id}`

2. **Modification Massive** (ligne 339 de `saka.py`)
   - **Condition** : Modification du solde SAKA > 10000 SAKA (seuil critique)
   - **Cause Probable** : Violation de la philosophie EGOEJO (monétisation SAKA, accumulation)
   - **Alerte** : `INTEGRITY BREACH DETECTED (MASSIVE MODIFICATION)`
   - **Dedupe Key** : `saka_wallet_massive:{user_id}:{wallet_id}`

### Format de l'Email

```
[URGENT] EGOEJO INTEGRITY BREACH DETECTED

INTEGRITY BREACH DETECTED
================================================================================

PAYLOAD STRUCTURÉ (JSON):
{
  "violation_type": "saka_wallet_bypass",
  "user_id": 123,
  "username": "testuser",
  "email": "testuser@example.com",
  "old_balance": 1000,
  "new_balance": 2000,
  "delta": 1000,
  "detection_method": "post_save_signal",
  "detection_details": "Aucune SakaTransaction correspondante trouvée dans les 5 dernières minutes",
  "likely_cause": "raw() SQL, update(), ou autre contournement",
  "constitution_violation": "no direct SAKA mutation",
  "action_required": "Vérifier immédiatement l'intégrité des données SAKA et identifier la source de la violation"
}

================================================================================

DÉTAILS LISIBLES:
violation_type: saka_wallet_bypass
user_id: 123
username: testuser
email: testuser@example.com
old_balance: 1000
new_balance: 2000
delta: 1000
detection_method: post_save_signal
detection_details: Aucune SakaTransaction correspondante trouvée dans les 5 dernières minutes
likely_cause: raw() SQL, update(), ou autre contournement
constitution_violation: no direct SAKA mutation
action_required: Vérifier immédiatement l'intégrité des données SAKA et identifier la source de la violation

================================================================================
Timestamp: 2025-01-03T10:00:00Z
Dedupe Key: saka_wallet_bypass:123:456
```

---

## 🧪 Tests

### Tests Unitaires

Les tests sont disponibles dans `backend/core/tests/utils/test_alerts.py` :

- ✅ Test d'envoi d'email réussi
- ✅ Test de désactivation des alertes
- ✅ Test d'absence d'admins configurés
- ✅ Test de dédoublonnage via cache
- ✅ Test de clés de dédoublonnage différentes
- ✅ Test sans clé de dédoublonnage
- ✅ Test de préfixe de sujet personnalisé
- ✅ Test de structure du payload JSON
- ✅ Test de gestion des erreurs SMTP
- ✅ Test de mise en cache

### Exécution des Tests

```bash
# Tous les tests d'alerte
pytest backend/core/tests/utils/test_alerts.py -v

# Tests spécifiques
pytest backend/core/tests/utils/test_alerts.py::TestSendCriticalAlert::test_send_critical_alert_success -v
```

### Test Manuel en Développement

```python
# Dans un shell Django
from core.utils.alerts import send_critical_alert

send_critical_alert(
    title="TEST ALERT",
    payload={"test": "data", "user_id": 123},
    dedupe_key="test:123"
)
```

---

## ⚠️ Limitations et Notes Importantes

### 1. Signal `post_save` Limitation

Le signal `post_save` est appelé **APRÈS** le `save()`, donc la récupération de l'instance originale avec `sender.objects.get(pk=instance.pk)` peut ne pas fonctionner correctement si l'instance a déjà été mise à jour dans la base de données.

**Solution Actuelle** : Le signal compare `original.balance` avec `instance.balance` en récupérant l'instance depuis la DB avant la comparaison.

**Amélioration Future** : Utiliser un signal `pre_save` pour capturer l'ancienne valeur avant le `save()`.

### 2. Détection `raw()` SQL

Le signal `post_save` **ne peut pas détecter** les modifications via `raw()` SQL car ces modifications ne déclenchent pas le signal.

**Solution Actuelle** : Détection indirecte via incohérence avec les `SakaTransaction` (si modification sans transaction correspondante).

**Amélioration Future** : Trigger SQL au niveau de la base de données pour détecter toutes les modifications.

### 3. Gestion d'Erreurs SMTP

Si l'envoi d'email échoue, l'erreur est loggée mais **ne bloque pas l'application** (`fail_silently=False` avec gestion d'exception dans un `try-except`).

**Impact** : Les violations peuvent être détectées mais l'alerte email peut échouer silencieusement si la configuration SMTP est incorrecte.

**Recommandation** : Vérifier régulièrement les logs Django pour détecter les échecs d'envoi d'email.

### 4. Performance

L'envoi d'email est **synchrone** par défaut (selon la configuration `EMAIL_BACKEND`). Pour un envoi asynchrone, utiliser Celery ou un backend email asynchrone.

**Impact** : Les `save()` de `SakaWallet` peuvent être ralentis si l'envoi d'email prend du temps.

**Recommandation** : Utiliser un backend email asynchrone en production (ex: `django.core.mail.backends.smtp.EmailBackend` avec Celery).

---

## 📊 Monitoring et Logs

### Logs Django

Les alertes génèrent des logs dans le logger `core.utils.alerts` :

- **INFO** : Alerte envoyée avec succès
- **DEBUG** : Alerte ignorée (dédoublonnage ou désactivée)
- **WARNING** : Aucun admin configuré
- **ERROR** : Échec d'envoi d'email

### Exemple de Logs

```
INFO core.utils.alerts: Alerte critique envoyée: INTEGRITY BREACH DETECTED (dedupe_key: saka_wallet_bypass:123:456)
DEBUG core.utils.alerts: Alerte 'INTEGRITY BREACH DETECTED' (dedupe_key: saka_wallet_bypass:123:456) déjà envoyée récemment. Ignorée pour éviter le spam.
ERROR core.utils.alerts: Échec envoi email alerte critique 'INTEGRITY BREACH DETECTED': SMTP connection failed
```

---

## 🔐 Sécurité

### Protection contre le Spam

- **Dédoublonnage** : Les alertes avec la même `dedupe_key` ne sont envoyées qu'une fois toutes les 5 minutes
- **Cache TTL** : 5 minutes (configurable via `DEDUPE_CACHE_TTL`)

### Confidentialité

- Les emails contiennent des informations sensibles (user_id, balances SAKA, etc.)
- **Recommandation** : Utiliser un canal sécurisé (SMTP avec TLS) et limiter l'accès aux boîtes email des admins

---

## 📚 Références

- **Code Source** : `backend/core/utils/alerts.py`
- **Intégration SAKA** : `backend/core/models/saka.py` (lignes 245-363)
- **Configuration** : `backend/config/settings.py` (lignes 450-473)
- **Tests** : `backend/core/tests/utils/test_alerts.py`
- **Documentation Webhook** : `docs/security/ALERTING_WEBHOOK.md` (webhooks optionnels)
- **Documentation Ancienne** : `docs/reports/IMPLEMENTATION_ACTIVE_ALERTING.md` (à mettre à jour)

---

## 🔔 Support Webhook (Optionnel)

Le système d'alerte supporte également les webhooks (generic, Slack) en complément des emails.

**Voir** : `docs/security/ALERTING_WEBHOOK.md` pour la documentation complète.

**Configuration Rapide** :
```bash
ALERT_WEBHOOK_ENABLED=True
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_WEBHOOK_TYPE=slack
```

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-03

