# 🔔 SYSTÈME D'ALERTE SLACK/WEBHOOK CRITIQUE EGOEJO

**Date** : 2025-01-05  
**Version** : 1.0  
**Objectif** : Canal Slack/Webhook en complément de l'email pour les alertes critiques EGOEJO

---

## 🎯 Vue d'Ensemble

Le système d'alerte Slack/Webhook EGOEJO permet d'envoyer automatiquement des notifications via webhook (Slack Incoming Webhook ou webhook générique) en complément des alertes email. Ce canal est **optionnel** et ne remplace pas l'email, mais le complète pour une réactivité accrue.

**Caractéristiques** :
- ✅ Support Slack Incoming Webhook (format blocks)
- ✅ Support webhook générique (POST JSON)
- ✅ Non-bloquant : les erreurs Slack ne cassent jamais le flux email
- ✅ Réutilise le système de dédoublonnage existant (5 minutes)
- ✅ Configuration via variables d'environnement
- ✅ Gestion robuste des erreurs réseau (timeout, connexion, HTTP)

---

## 📁 Architecture

### Fichiers Principaux

- **`backend/core/utils/alerts.py`** : Module central d'alerte
  - Fonction `send_webhook_alert()` : Envoie une alerte via webhook (ligne 188)
  - Fonction `_build_slack_payload()` : Construit le payload Slack formaté (ligne 326)
  - Intégration dans `send_critical_alert()` : Appel automatique si activé (ligne 144)

- **`backend/config/settings.py`** : Configuration
  - `ALERT_WEBHOOK_ENABLED` : Activer/désactiver les webhooks
  - `ALERT_WEBHOOK_URL` : URL du webhook (Slack ou générique)
  - `ALERT_WEBHOOK_TYPE` : Type de webhook (`slack` ou `generic`)
  - `ALERT_WEBHOOK_TIMEOUT_SECONDS` : Timeout HTTP (défaut : 5s)

---

## 🔧 Configuration

### Variables d'Environnement Requises

```bash
# Activer les webhooks
ALERT_WEBHOOK_ENABLED=True

# URL du webhook (Slack Incoming Webhook ou webhook générique)
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Type de webhook : 'slack' ou 'generic'
ALERT_WEBHOOK_TYPE=slack

# Timeout HTTP (optionnel, défaut : 5 secondes)
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

Le système Slack/Webhook est **automatiquement appelé** par `send_critical_alert()` si `ALERT_WEBHOOK_ENABLED=True`. Aucun code supplémentaire n'est nécessaire.

**Ordre d'exécution** :
1. Email (toujours envoyé si activé)
2. Webhook/Slack (si activé et si email réussi ou échoué)

**Important** : Le webhook est **non-bloquant**. Si le webhook échoue, l'email continue de fonctionner normalement.

### Exemple d'Utilisation

```python
from core.utils.alerts import send_critical_alert

# L'alerte sera envoyée par email ET par Slack (si activé)
send_critical_alert(
    title="INTEGRITY BREACH DETECTED",
    payload={
        "violation_type": "saka_wallet_bypass",
        "user_id": 123,
        "username": "testuser",
        "old_balance": 1000,
        "new_balance": 2000,
        "delta": 1000,
        "detection_method": "post_save_signal"
    },
    dedupe_key="saka_wallet_bypass:123:456"
)
```

---

## 🔗 Configuration Slack Incoming Webhook

### 1. Créer un Webhook Slack

1. Aller sur https://api.slack.com/apps
2. Créer une nouvelle app ou sélectionner une app existante
3. Aller dans **Incoming Webhooks**
4. Activer **Activate Incoming Webhooks**
5. Cliquer sur **Add New Webhook to Workspace**
6. Sélectionner le canal Slack où recevoir les alertes
7. Copier l'URL du webhook (format : `https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN`)

### 2. Configurer EGOEJO

```bash
ALERT_WEBHOOK_ENABLED=True
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_WEBHOOK_TYPE=slack
```

### 3. Format Slack

Le système génère automatiquement un message Slack avec :
- **Header** : Titre de l'alerte avec emoji 🚨
- **Fields** : Détails principaux (user_id, username, balances, etc.)
- **JSON complet** : Payload JSON formaté dans un bloc de code
- **Footer** : Timestamp et clé de dédoublonnage

**Exemple de message Slack** :

```
🚨 INTEGRITY BREACH DETECTED
─────────────────────────────
*user_id:* 123
*username:* testuser
*old_balance:* 1000
*new_balance:* 2000
*delta:* 1000

*Payload JSON complet:*
```json
{
  "violation_type": "saka_wallet_bypass",
  "user_id": 123,
  "username": "testuser",
  ...
}
```

Timestamp: 2025-01-05T10:00:00Z | Dedupe Key: saka_wallet_bypass:123:456
```

---

## 🌐 Configuration Webhook Générique

Pour utiliser un webhook générique (non-Slack), configurez :

```bash
ALERT_WEBHOOK_ENABLED=True
ALERT_WEBHOOK_URL=https://your-webhook-service.com/api/alerts
ALERT_WEBHOOK_TYPE=generic
```

### Format Generic

Le payload envoyé est un JSON structuré :

```json
{
  "title": "INTEGRITY BREACH DETECTED",
  "payload": {
    "violation_type": "saka_wallet_bypass",
    "user_id": 123,
    "username": "testuser",
    ...
  },
  "timestamp": "2025-01-05T10:00:00Z",
  "dedupe_key": "saka_wallet_bypass:123:456",
  "source": "egoejo_critical_alert"
}
```

---

## 🧪 Tests

### Tests Unitaires

Les tests sont disponibles dans `backend/core/tests/utils/test_alerts.py` (classe `TestSendWebhookAlert`) :

- ✅ Test de désactivation des webhooks
- ✅ Test d'absence d'URL configurée
- ✅ Test d'envoi webhook generic avec succès
- ✅ Test d'envoi webhook Slack avec succès
- ✅ Test de gestion des timeouts
- ✅ Test de gestion des erreurs réseau
- ✅ Test de gestion des erreurs HTTP (status != 2xx)
- ✅ Test de type invalide (fallback sur generic)
- ✅ Test d'intégration avec `send_critical_alert()`

### Exécution des Tests

```bash
# Tous les tests d'alerte (email + webhook)
pytest backend/core/tests/utils/test_alerts.py -v

# Tests webhook uniquement
pytest backend/core/tests/utils/test_alerts.py::TestSendWebhookAlert -v
```

### Test Manuel en Développement

```python
# Dans un shell Django
from core.utils.alerts import send_critical_alert

# Activer les webhooks dans settings.py ou via override_settings
send_critical_alert(
    title="TEST ALERT",
    payload={"test": "data", "user_id": 123},
    dedupe_key="test:123"
)
```

---

## ⚠️ Limitations et Notes Importantes

### 1. Dépendance `requests`

Le système nécessite le module Python `requests` pour envoyer les webhooks. Si `requests` n'est pas disponible, le système log un warning et continue sans bloquer.

**Vérification** :
```bash
pip install requests
```

### 2. Non-Bloquant

Le webhook est **toujours non-bloquant**. Si le webhook échoue (timeout, erreur réseau, HTTP error), l'erreur est loggée mais **ne bloque jamais le flux email**.

**Impact** : Les alertes email continuent de fonctionner même si Slack est indisponible.

### 3. Dédoublonnage

Le système de dédoublonnage (5 minutes) s'applique **uniquement à l'email**. Le webhook est envoyé à chaque appel de `send_critical_alert()`, même si l'email a été dédupliqué.

**Raison** : Le webhook peut avoir besoin de recevoir toutes les alertes pour un monitoring en temps réel.

**Amélioration Future** : Ajouter un dédoublonnage optionnel pour le webhook si nécessaire.

### 4. Performance

L'envoi de webhook est **synchrone** par défaut. Pour un envoi asynchrone, utiliser Celery ou un backend asynchrone.

**Impact** : Les appels à `send_critical_alert()` peuvent être ralentis si le webhook prend du temps (timeout : 5s par défaut).

**Recommandation** : Utiliser un timeout court (5s) et un backend asynchrone en production si nécessaire.

### 5. Sécurité

**⚠️ IMPORTANT** : Les webhooks contiennent des informations sensibles (user_id, balances SAKA, etc.).

**Bonnes Pratiques** :
- Utiliser HTTPS uniquement pour les webhooks
- Ne jamais exposer l'URL du webhook publiquement
- Utiliser des webhooks Slack privés (canal dédié aux alertes)
- Limiter l'accès au canal Slack aux administrateurs uniquement
- Ne pas logger l'URL complète du webhook dans les logs (seulement le domaine)

---

## 📊 Monitoring et Logs

### Logs Django

Les alertes webhook génèrent des logs dans le logger `core.utils.alerts` :

- **INFO** : Webhook envoyé avec succès
- **DEBUG** : Webhook désactivé ou ignoré
- **WARNING** : Échec d'envoi webhook (timeout, erreur réseau, HTTP error)

### Exemple de Logs

```
INFO core.utils.alerts: Webhook alerte envoyé avec succès: INTEGRITY BREACH DETECTED (status: 200, type: slack)
WARNING core.utils.alerts: Webhook alerte timeout: INTEGRITY BREACH DETECTED (timeout: 5s)
WARNING core.utils.alerts: Webhook alerte erreur réseau: INTEGRITY BREACH DETECTED (erreur: Connection refused)
WARNING core.utils.alerts: Webhook alerte échoué: INTEGRITY BREACH DETECTED (status: 500, response: Internal Server Error)
```

---

## 🔐 Sécurité

### Protection contre le Spam

- **Dédoublonnage Email** : Les alertes email avec la même `dedupe_key` ne sont envoyées qu'une fois toutes les 5 minutes
- **Webhook** : Pas de dédoublonnage (toutes les alertes sont envoyées pour un monitoring en temps réel)

### Confidentialité

- Les webhooks contiennent des informations sensibles (user_id, balances SAKA, etc.)
- **Recommandation** : Utiliser un canal Slack privé et limiter l'accès aux administrateurs uniquement

### Validation de l'URL

- Le système ne valide pas l'URL du webhook (format, domaine, etc.)
- **Recommandation** : Vérifier manuellement que l'URL est correcte avant de l'activer en production

---

## 📚 Références

- **Code Source** : `backend/core/utils/alerts.py`
  - Fonction `send_webhook_alert()` : ligne 188
  - Fonction `_build_slack_payload()` : ligne 326
  - Intégration dans `send_critical_alert()` : ligne 144

- **Configuration** : `backend/config/settings.py` (lignes 475-480)
- **Tests** : `backend/core/tests/utils/test_alerts.py` (classe `TestSendWebhookAlert`)
- **Documentation Email** : `docs/security/ALERTING_EMAIL.md`
- **Documentation Webhook Générique** : `docs/security/ALERTING_WEBHOOK.md` (si existe)

---

## 🔔 Canaux Multiples

Le système EGOEJO supporte **plusieurs canaux d'alerte** :

1. **Email** : Canal principal (toujours activé si `ALERT_EMAIL_ENABLED=True`)
2. **Slack/Webhook** : Canal complémentaire (optionnel, si `ALERT_WEBHOOK_ENABLED=True`)

**Ordre d'exécution** :
1. Email (toujours envoyé en premier)
2. Webhook/Slack (si activé, après l'email)

**Important** : Les deux canaux sont **indépendants**. Si l'email échoue, le webhook est quand même envoyé. Si le webhook échoue, l'email continue de fonctionner.

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-05

