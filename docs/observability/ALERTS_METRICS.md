# 📊 MÉTRIQUES ET OBSERVABILITÉ DES ALERTES CRITIQUES EGOEJO

**Date** : 2025-01-03  
**Version** : 1.0  
**Objectif** : Traçabilité et métriques des alertes critiques pour observabilité

---

## 🎯 Vue d'Ensemble

Le système de métriques d'alertes EGOEJO permet de :
- Enregistrer tous les événements d'alerte critique réellement émis
- Analyser les tendances par type d'événement et canal
- Générer des rapports mensuels
- Surveiller l'évolution des alertes dans le temps

**Principe Fondamental** : Un événement est enregistré **uniquement** si l'alerte est réellement émise (après dédoublonnage). Les alertes dédoublonnées ne créent pas d'événement.

---

## 📁 Architecture

### Modèle de Données

**Fichier** : `backend/core/models/alerts.py`

**Modèle** : `CriticalAlertEvent`

**Champs** :
- `created_at` : Date/heure de création (timezone-aware, UTC)
- `severity` : Sévérité (`critical`, `high`, `medium`, `low`)
- `event_type` : Type d'événement (ex: `INTEGRITY BREACH DETECTED`)
- `channel` : Canal d'envoi (`email`, `webhook`, `both`)
- `fingerprint` : Empreinte unique pour dédoublonnage
- `payload_excerpt` : Extrait du payload (champs principaux pour recherche rapide)

**Indexes** :
- `created_at` (descendant)
- `event_type`, `created_at`
- `channel`, `created_at`
- `severity`, `created_at`

---

## 🔧 Utilisation

### Enregistrement Automatique

Les événements sont **automatiquement enregistrés** par `send_critical_alert()` lorsqu'une alerte est réellement émise (après dédoublonnage).

**Fichier** : `backend/core/utils/alerts.py`

**Lignes 141-165** : Enregistrement automatique après envoi email/webhook réussi

```python
# Enregistrer l'événement d'alerte critique (uniquement si réellement émis)
# Déterminer le canal d'envoi
if webhook_sent:
    channel = 'both'  # Email + Webhook
else:
    channel = 'email'  # Email uniquement

# Générer un fingerprint si non fourni
event_fingerprint = dedupe_key or f"{title}:{timezone.now().isoformat()}"

# Enregistrer l'événement (non-bloquant, ne doit pas casser le flux)
try:
    from core.models.alerts import CriticalAlertEvent
    CriticalAlertEvent.create_from_alert(
        title=title,
        payload=payload,
        channel=channel,
        fingerprint=event_fingerprint,
        severity='critical'
    )
except Exception as e:
    # Logger l'erreur mais ne pas bloquer le flux
    logger.warning(
        f"Échec enregistrement CriticalAlertEvent pour '{title}': {e}",
        exc_info=True
    )
```

### Dédoublonnage

**Règle** : Si `send_critical_alert()` retourne `True` mais que l'email/webhook n'a pas été envoyé (dédoublonné), **aucun événement n'est créé**.

**Exemple** :
```python
# Premier appel : Email envoyé + Événement créé
send_critical_alert("ALERT", payload, dedupe_key="test:123")
# → Événement créé

# Deuxième appel (dans les 5 minutes) : Dédoublonné, pas d'email, pas d'événement
send_critical_alert("ALERT", payload, dedupe_key="test:123")
# → Aucun événement créé
```

---

## 📊 Requêtes et Agrégations

### Comptage par Mois

**Méthode** : `CriticalAlertEvent.count_critical_alerts_for_month(year, month)`

**Alias** : `CriticalAlertEvent.count_for_month(year, month)`

**Exemple** :
```python
from core.models.alerts import CriticalAlertEvent

# Compter les alertes de janvier 2025
count = CriticalAlertEvent.count_critical_alerts_for_month(2025, 1)
print(f"Alertes en janvier 2025: {count}")
```

**Gestion Timezone** : Utilise UTC pour les calculs de date (timezone-aware).

### Comptage par Type d'Événement

**Méthode** : `CriticalAlertEvent.count_by_event_type_for_month(year, month)`

**Retourne** : `dict` avec `{event_type: count}`

**Exemple** :
```python
by_type = CriticalAlertEvent.count_by_event_type_for_month(2025, 1)
# {
#     'INTEGRITY BREACH DETECTED': 5,
#     'SAKA WALLET INCONSISTENCY': 2,
#     'MASSIVE MODIFICATION': 1
# }
```

### Comptage par Canal

**Méthode** : `CriticalAlertEvent.count_by_channel_for_month(year, month)`

**Retourne** : `dict` avec `{channel: count}`

**Exemple** :
```python
by_channel = CriticalAlertEvent.count_by_channel_for_month(2025, 1)
# {
#     'email': 3,
#     'webhook': 1,
#     'both': 4
# }
```

---

## 🖥️ Commande Management

### Génération de Rapport Mensuel

**Commande** : `python manage.py alerts_report --month YYYY-MM`

**Exemple** :
```bash
# Rapport pour janvier 2025
python manage.py alerts_report --month 2025-01

# Rapport pour décembre 2024
python manage.py alerts_report --month 2024-12
```

**Sortie** :
```
📊 RAPPORT ALERTES CRITIQUES - 2025-01
================================================================================

📈 Total d'alertes: 8

📋 Par type d'événement:
  - INTEGRITY BREACH DETECTED: 5
  - SAKA WALLET INCONSISTENCY: 2
  - MASSIVE MODIFICATION: 1

📧 Par canal:
  - Email + Webhook: 4
  - Email uniquement: 3
  - Webhook uniquement: 1

⏰ Période:
  - Première alerte: 2025-01-05 10:30:00 UTC
  - Dernière alerte: 2025-01-28 15:45:00 UTC

================================================================================
✅ Rapport généré avec succès
```

---

## 🧪 Tests

### Tests Unitaires

**Fichier** : `backend/core/tests/models/test_critical_alert_event.py`

**Tests Inclus** :
- ✅ Création d'événement (`test_create_from_alert`)
- ✅ Création avec webhook (`test_create_from_alert_with_webhook`)
- ✅ Comptage par mois (`test_count_for_month_with_events`)
- ✅ Gestion timezone/UTC (`test_count_for_month_timezone_utc`)
- ✅ Comptage par type (`test_count_by_event_type_for_month`)
- ✅ Comptage par canal (`test_count_by_channel_for_month`)
- ✅ Alias `count_critical_alerts_for_month` (`test_count_critical_alerts_for_month_alias`)
- ✅ Dédoublonnage n'incrémente pas (`test_deduplication_does_not_create_event`)
- ✅ Sans dedupe_key crée plusieurs événements (`test_no_dedupe_key_creates_multiple_events`)

### Exécution des Tests

```bash
# Tous les tests d'alertes
pytest backend/core/tests/models/test_critical_alert_event.py -v

# Tests spécifiques
pytest backend/core/tests/models/test_critical_alert_event.py::TestCriticalAlertEventDeduplication -v
```

---

## ⚠️ Limitations et Notes Importantes

### 1. Enregistrement Non-Bloquant

L'enregistrement d'un événement est **non-bloquant** : si l'enregistrement échoue, l'erreur est loggée mais le flux principal continue.

**Impact** : Certaines alertes peuvent ne pas être enregistrées si la base de données est indisponible.

**Recommandation** : Surveiller les logs pour détecter les échecs d'enregistrement.

### 2. Dédoublonnage

Les événements sont enregistrés **uniquement** si l'alerte est réellement émise. Les alertes dédoublonnées (via cache) ne créent pas d'événement.

**Raison** : Éviter la duplication dans les métriques.

**Impact** : Les métriques reflètent les alertes réellement envoyées, pas les tentatives.

### 3. Timezone

Tous les calculs de date utilisent **UTC** (timezone-aware).

**Impact** : Les rapports mensuels sont basés sur UTC, pas sur le fuseau horaire local.

**Recommandation** : Utiliser UTC pour tous les calculs de date.

### 4. Performance

Les requêtes d'agrégation utilisent des **indexes** pour optimiser les performances.

**Impact** : Les requêtes sont rapides même avec des millions d'événements.

**Recommandation** : Surveiller les performances des requêtes si le volume d'événements devient très élevé.

---

## 📊 Exemples d'Utilisation

### Dashboard de Monitoring

```python
from core.models.alerts import CriticalAlertEvent
from django.utils import timezone

# Alertes du mois en cours
now = timezone.now()
current_month_count = CriticalAlertEvent.count_critical_alerts_for_month(
    now.year, now.month
)

# Top 5 types d'événements ce mois
by_type = CriticalAlertEvent.count_by_event_type_for_month(now.year, now.month)
top_5 = sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:5]

# Répartition par canal
by_channel = CriticalAlertEvent.count_by_channel_for_month(now.year, now.month)
```

### Alertes Récentes

```python
from core.models.alerts import CriticalAlertEvent

# 10 dernières alertes
recent_alerts = CriticalAlertEvent.objects.all()[:10]

for alert in recent_alerts:
    print(f"{alert.created_at} - {alert.event_type} ({alert.channel})")
```

### Tendances Mensuelles

```python
from core.models.alerts import CriticalAlertEvent
from django.utils import timezone

# Comparer les 3 derniers mois
now = timezone.now()
for i in range(3):
    month = now.month - i
    year = now.year
    if month <= 0:
        month += 12
        year -= 1
    
    count = CriticalAlertEvent.count_critical_alerts_for_month(year, month)
    print(f"{year}-{month:02d}: {count} alertes")
```

---

## 📚 Références

- **Modèle** : `backend/core/models/alerts.py`
- **Intégration** : `backend/core/utils/alerts.py` (lignes 141-165)
- **Commande Management** : `backend/core/management/commands/alerts_report.py`
- **Tests** : `backend/core/tests/models/test_critical_alert_event.py`
- **Documentation Alertes** : `docs/security/ALERTING_EMAIL.md`, `docs/security/ALERTING_WEBHOOK.md`

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-03

