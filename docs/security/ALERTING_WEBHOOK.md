# 🔔 SYSTÈME D'ALERTE WEBHOOK EGOEJO

**Date** : 2025-01-03  
**Version** : 1.0  
**Objectif** : Support webhook optionnel pour les alertes critiques (generic, Slack)

---

## 🎯 Vue d'Ensemble

Le système d'alerte webhook EGOEJO permet d'envoyer automatiquement des notifications via webhook (generic ou Slack) en complément des alertes email. Les webhooks sont **optionnels** et **non-bloquants** : toute erreur réseau ne bloque pas le flux principal.

**Caractéristiques** :
- ✅ Support webhook generic (JSON brut)
- ✅ Support webhook Slack (format blocks avec JSON en pièce jointe)
- ✅ Fail-safe : erreurs réseau ne bloquent pas le flux
- ✅ Configuration via variables d'environnement
- ✅ Intégration automatique avec `send_critical_alert()`

---

## 📁 Architecture

### Fichiers Principaux

- **`backend/core/utils/alerts.py`** : Module central d'alerte
  - Fonction `send_webhook_alert()` : Envoie une alerte via webhook
  - Fonction `_build_slack_payload()` : Construit un payload Slack formaté
  - Intégration avec `send_critical_alert()` (appel automatique)

- **`backend/config/settings.py`** : Configuration
  - `ALERT_WEBHOOK_ENABLED` : Activer/désactiver les webhooks
  - `ALERT_WEBHOOK_URL` : URL du webhook
  - `ALERT_WEBHOOK_TYPE` : Type de webhook (`generic` ou `slack`)
  - `ALERT_WEBHOOK_TIMEOUT_SECONDS` : Timeout pour les requêtes HTTP

---

## 🔧 Configuration

### Variables d'Environnement Requises

```bash
# Activer les webhooks (optionnel, par défaut: False)
ALERT_WEBHOOK_ENABLED=True

# URL du webhook (obligatoire si ALERT_WEBHOOK_ENABLED=True)
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Type de webhook : 'generic' ou 'slack' (par défaut: 'generic')
ALERT_WEBHOOK_TYPE=slack

# Timeout pour les requêtes HTTP en secondes (par défaut: 5)
ALERT_WEBHOOK_TIMEOUT_SECONDS=5
```

### Configuration Django Settings

Les variables d'environnement sont automatiquement chargées dans `backend/config/settings.py` :

```python
# ALERTES WEBHOOK (Optionnel)
ALERT_WEBHOOK_ENABLED = os.environ.get('ALERT_WEBHOOK_ENABLED', 'False').lower() == 'true'
ALERT_WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK_URL', '')
ALERT_WEBHOOK_TYPE = os.environ.get('ALERT_WEBHOOK_TYPE', 'generic').lower()  # 'generic' ou 'slack'
ALERT_WEBHOOK_TIMEOUT_SECONDS = int(os.environ.get('ALERT_WEBHOOK_TIMEOUT_SECONDS', '5'))
```

---

## 📖 Utilisation

### Intégration Automatique

Le webhook est **automatiquement appelé** par `send_critical_alert()` si activé :

```python
from core.utils.alerts import send_critical_alert

# L'email ET le webhook sont envoyés automatiquement (si activés)
send_critical_alert(
    title="INTEGRITY BREACH DETECTED",
    payload={
        "violation_type": "saka_wallet_bypass",
        "user_id": 123,
        "username": "testuser",
        "old_balance": 1000,
        "new_balance": 2000,
        "delta": 1000
    },
    dedupe_key="saka_wallet:123"
)
```

### Appel Direct (Optionnel)

Vous pouvez aussi appeler `send_webhook_alert()` directement :

```python
from core.utils.alerts import send_webhook_alert

send_webhook_alert(
    title="TEST ALERT",
    payload={"test": "data"},
    dedupe_key="test:123"
)
```

---

## 🔔 Formats de Webhook

### Format Generic

Le format generic envoie un payload JSON brut avec métadonnées :

```json
{
  "title": "INTEGRITY BREACH DETECTED",
  "payload": {
    "violation_type": "saka_wallet_bypass",
    "user_id": 123,
    "username": "testuser",
    "old_balance": 1000,
    "new_balance": 2000,
    "delta": 1000
  },
  "timestamp": "2025-01-03T10:00:00Z",
  "dedupe_key": "saka_wallet:123",
  "source": "egoejo_critical_alert"
}
```

### Format Slack

Le format Slack envoie un payload avec blocks formatés et le JSON original en pièce jointe :

```json
{
  "text": "🚨 *INTEGRITY BREACH DETECTED*\n\n",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚨 INTEGRITY BREACH DETECTED",
        "emoji": true
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*user_id:* 123"
        },
        {
          "type": "mrkdwn",
          "text": "*username:* testuser"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Payload JSON complet:*"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "```{\n  \"violation_type\": \"saka_wallet_bypass\",\n  \"user_id\": 123,\n  ...\n}```"
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "Timestamp: 2025-01-03T10:00:00Z | Dedupe Key: saka_wallet:123"
        }
      ]
    }
  ]
}
```

---

## 🛡️ Fail-Safe et Gestion d'Erreurs

### Principe

Le système webhook est **non-bloquant** : toute erreur réseau ne bloque pas le flux principal de l'application.

### Types d'Erreurs Gérées

1. **Timeout** : Si la requête HTTP dépasse le timeout configuré
   - Log : `WARNING` avec détails (URL, timeout, type d'erreur)
   - Action : Retourne `False`, ne bloque pas le flux

2. **Erreur Réseau** : Si la connexion échoue (ConnectionError, etc.)
   - Log : `WARNING` avec détails (URL, type d'erreur, message)
   - Action : Retourne `False`, ne bloque pas le flux

3. **Erreur HTTP** : Si le serveur retourne un code d'erreur (4xx, 5xx)
   - Log : `WARNING` avec détails (URL, status code, réponse)
   - Action : Retourne `False`, ne bloque pas le flux

4. **Erreur Inattendue** : Toute autre exception
   - Log : `WARNING` avec stack trace
   - Action : Retourne `False`, ne bloque pas le flux

### Exemple de Log

```
WARNING core.utils.alerts: Webhook alerte timeout: INTEGRITY BREACH DETECTED (timeout: 5s)
    extra={
        'webhook_url': 'https://hooks.slack.com/services/XXX',
        'webhook_type': 'slack',
        'timeout': 5,
        'error_type': 'timeout'
    }
```

---

## 🧪 Tests

### Tests Unitaires

Les tests sont disponibles dans `backend/core/tests/utils/test_alerts.py` :

- ✅ Test de désactivation des webhooks
- ✅ Test d'absence d'URL configurée
- ✅ Test d'envoi webhook generic avec succès
- ✅ Test d'envoi webhook Slack avec succès
- ✅ Test de gestion des timeouts
- ✅ Test de gestion des erreurs réseau
- ✅ Test de gestion des erreurs HTTP
- ✅ Test de type invalide (fallback vers generic)
- ✅ Test d'intégration avec `send_critical_alert()`

### Exécution des Tests

```bash
# Tous les tests d'alerte (email + webhook)
pytest backend/core/tests/utils/test_alerts.py -v

# Tests spécifiques webhook
pytest backend/core/tests/utils/test_alerts.py::TestSendWebhookAlert -v
```

### Test Manuel en Développement

```python
# Dans un shell Django
from core.utils.alerts import send_webhook_alert

send_webhook_alert(
    title="TEST ALERT",
    payload={"test": "data", "user_id": 123},
    dedupe_key="test:123"
)

# Vérifier les logs ou le webhook (selon configuration)
```

---

## ⚠️ Limitations et Notes Importantes

### 1. Dépendance `requests`

Le module `requests` est **requis** pour le support webhook. Si `requests` n'est pas installé :
- Le système log un `WARNING` au démarrage
- Les webhooks sont automatiquement désactivés
- Les alertes email continuent de fonctionner normalement

**Installation** :
```bash
pip install requests>=2.31.0
```

### 2. Performance

L'envoi de webhook est **synchrone** par défaut. Pour un envoi asynchrone, utiliser Celery ou un backend asynchrone.

**Impact** : Les appels à `send_critical_alert()` peuvent être ralentis si le webhook prend du temps.

**Recommandation** : Utiliser un timeout court (5s par défaut) et un webhook rapide en production.

### 3. Dédoublonnage

Le dédoublonnage via cache s'applique uniquement aux **emails**, pas aux webhooks. Chaque appel à `send_critical_alert()` envoie un webhook (si activé), même si l'email a été dédupliqué.

**Raison** : Les webhooks peuvent avoir besoin de recevoir toutes les alertes pour leur propre logique de dédoublonnage.

---

## 📊 Monitoring et Logs

### Logs Django

Les webhooks génèrent des logs dans le logger `core.utils.alerts` :

- **INFO** : Webhook envoyé avec succès
- **DEBUG** : Webhook désactivé ou ignoré
- **WARNING** : Erreur réseau/timeout/HTTP (avec détails structurés)

### Exemple de Logs

```
INFO core.utils.alerts: Webhook alerte envoyé avec succès: INTEGRITY BREACH DETECTED (status: 200, type: slack)
WARNING core.utils.alerts: Webhook alerte timeout: INTEGRITY BREACH DETECTED (timeout: 5s)
WARNING core.utils.alerts: Webhook alerte erreur réseau: INTEGRITY BREACH DETECTED (erreur: Connection failed)
```

---

## 🔐 Sécurité

### Protection contre le Spam

- **Pas de dédoublonnage** : Les webhooks reçoivent toutes les alertes (pour leur propre logique)
- **Timeout** : Limite le temps d'attente (5s par défaut)
- **Fail-fast** : Les erreurs ne bloquent pas le flux

### Confidentialité

- Les webhooks contiennent des informations sensibles (user_id, balances SAKA, etc.)
- **Recommandation** : Utiliser HTTPS pour les webhooks et limiter l'accès aux webhooks

---

## 📚 Références

- **Code Source** : `backend/core/utils/alerts.py`
- **Configuration** : `backend/config/settings.py` (lignes 475-479)
- **Tests** : `backend/core/tests/utils/test_alerts.py` (classe `TestSendWebhookAlert`)
- **Documentation Email** : `docs/security/ALERTING_EMAIL.md`

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-03

