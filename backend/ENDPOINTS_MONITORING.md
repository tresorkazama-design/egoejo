# Endpoints API de Monitoring

## 📋 Endpoints créés

### 1. POST /api/analytics/metrics/

Endpoint pour recevoir les métriques de performance depuis le frontend.

**Permissions**: Aucune (AllowAny) - Permet l'envoi depuis le frontend sans authentification

**Body**:
```json
{
  "metric": "LCP",
  "value": 1234.5,
  "metadata": {
    "endpoint": "/api/projets/"
  },
  "timestamp": "2025-01-27T10:00:00Z",
  "url": "https://egoejo.org/projets"
}
```

**Réponse**:
```json
{
  "id": 1,
  "status": "created"
}
```

**Métriques supportées**:
- `LCP` - Largest Contentful Paint
- `FID` - First Input Delay
- `CLS` - Cumulative Layout Shift
- `TTFB` - Time to First Byte
- `FCP` - First Contentful Paint
- `PageLoad` - Page Load Time
- `DOMContentLoaded` - DOM Content Loaded
- `API_Duration` - API Request Duration
- `Custom` - Métrique personnalisée

---

### 2. POST /api/monitoring/alerts/

Endpoint pour recevoir les alertes depuis le frontend.

**Permissions**: Aucune (AllowAny) - Permet l'envoi depuis le frontend sans authentification

**Body**:
```json
{
  "level": "warning",
  "message": "LCP lent: 3000ms (objectif: <2500ms)",
  "metadata": {
    "context": "homepage"
  },
  "timestamp": "2025-01-27T10:00:00Z",
  "url": "https://egoejo.org/"
}
```

**Niveaux d'alerte**:
- `critical` - Critique
- `error` - Erreur
- `warning` - Avertissement
- `info` - Information
- `performance` - Performance
- `api` - API

**Réponse**:
```json
{
  "id": 1,
  "status": "created"
}
```

---

### 3. GET /api/monitoring/metrics/stats/

Endpoint pour consulter les statistiques des métriques (admin uniquement).

**Permissions**: IsAdminUser

**Query Parameters**:
- `hours` (optionnel, défaut: 24) - Nombre d'heures à analyser
- `metric_type` (optionnel) - Filtrer par type de métrique

**Exemple**:
```
GET /api/monitoring/metrics/stats/?hours=48&metric_type=LCP
```

**Réponse**:
```json
{
  "period_hours": 48,
  "since": "2025-01-25T10:00:00Z",
  "stats": {
    "LCP": {
      "name": "Largest Contentful Paint",
      "count": 150,
      "avg": 1850.5,
      "min": 800.0,
      "max": 3200.0
    },
    "FID": {
      "name": "First Input Delay",
      "count": 120,
      "avg": 45.2,
      "min": 10.0,
      "max": 150.0
    }
  }
}
```

---

### 4. GET /api/monitoring/alerts/list/

Endpoint pour lister les alertes non résolues (admin uniquement).

**Permissions**: IsAdminUser

**Query Parameters**:
- `level` (optionnel) - Filtrer par niveau d'alerte
- `resolved` (optionnel, défaut: false) - Inclure les alertes résolues
- `hours` (optionnel, défaut: 168) - Nombre d'heures à analyser (défaut: 7 jours)

**Exemple**:
```
GET /api/monitoring/alerts/list/?level=critical&hours=24
```

**Réponse**:
```json
{
  "count": 5,
  "alerts": [
    {
      "id": 1,
      "level": "critical",
      "message": "Application React non montée",
      "url": "https://egoejo.org/",
      "timestamp": "2025-01-27T10:00:00Z",
      "resolved": false,
      "metadata": {}
    }
  ]
}
```

---

### 5. PATCH /api/monitoring/alerts/{id}/

Endpoint pour marquer une alerte comme résolue (admin uniquement).

**Permissions**: IsAdminUser

**Exemple**:
```
PATCH /api/monitoring/alerts/1/
```

**Réponse**:
```json
{
  "status": "resolved"
}
```

---

## 🗄️ Modèles de données

### PerformanceMetric

Stocke les métriques de performance.

**Champs**:
- `metric_type` - Type de métrique (LCP, FID, CLS, etc.)
- `value` - Valeur de la métrique
- `url` - URL de la page
- `user` - Utilisateur (si authentifié)
- `metadata` - Métadonnées supplémentaires (JSON)
- `timestamp` - Date et heure
- `user_agent` - User-Agent du navigateur
- `ip_address` - Adresse IP

**Index**:
- `timestamp` (descendant)
- `metric_type` + `timestamp`

### MonitoringAlert

Stocke les alertes de monitoring.

**Champs**:
- `level` - Niveau d'alerte (critical, error, warning, etc.)
- `message` - Message d'alerte
- `url` - URL de la page
- `user` - Utilisateur (si authentifié)
- `metadata` - Métadonnées supplémentaires (JSON)
- `timestamp` - Date et heure
- `resolved` - Alerte résolue (booléen)
- `resolved_at` - Date de résolution
- `user_agent` - User-Agent du navigateur
- `ip_address` - Adresse IP

**Index**:
- `timestamp` (descendant)
- `level` + `resolved` + `timestamp`

---

## 🔧 Utilisation

### Depuis le frontend

Le monitoring est automatiquement configuré dans `src/utils/monitoring.js` et envoie les données à ces endpoints.

### Depuis l'admin Django

Les modèles sont disponibles dans l'admin Django. Pour les activer, ajouter dans `backend/core/admin.py`:

```python
from core.models.monitoring import PerformanceMetric, MonitoringAlert

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'url', 'timestamp']
    list_filter = ['metric_type', 'timestamp']
    search_fields = ['url', 'user_agent']

@admin.register(MonitoringAlert)
class MonitoringAlertAdmin(admin.ModelAdmin):
    list_display = ['level', 'message', 'url', 'resolved', 'timestamp']
    list_filter = ['level', 'resolved', 'timestamp']
    search_fields = ['message', 'url']
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        for alert in queryset:
            alert.resolve()
    mark_resolved.short_description = "Marquer comme résolu"
```

---

## 📊 Statistiques et analyses

### Requêtes SQL utiles

**Moyenne LCP sur les 24 dernières heures**:
```sql
SELECT AVG(value) 
FROM monitoring_performance_metric 
WHERE metric_type = 'LCP' 
AND timestamp >= NOW() - INTERVAL '24 hours';
```

**Alertes critiques non résolues**:
```sql
SELECT * 
FROM monitoring_alert 
WHERE level = 'critical' 
AND resolved = false 
ORDER BY timestamp DESC;
```

---

## 🚀 Déploiement

### Migrations

Les migrations ont été créées automatiquement. Pour les appliquer en production:

```bash
python manage.py migrate core
```

### Vérification

Tester les endpoints après déploiement:

```bash
# Tester l'envoi d'une métrique
curl -X POST https://egoejo-production.up.railway.app/api/analytics/metrics/ \
  -H "Content-Type: application/json" \
  -d '{"metric": "LCP", "value": 1500, "url": "https://egoejo.org/"}'

# Tester l'envoi d'une alerte
curl -X POST https://egoejo-production.up.railway.app/api/monitoring/alerts/ \
  -H "Content-Type: application/json" \
  -d '{"level": "info", "message": "Test alert", "url": "https://egoejo.org/"}'
```

---

## 🔒 Sécurité

- Les endpoints POST (`/api/analytics/metrics/` et `/api/monitoring/alerts/`) sont publics pour permettre l'envoi depuis le frontend
- Les endpoints GET sont protégés par `IsAdminUser`
- Les IP et User-Agent sont enregistrés pour le debugging
- Les données sensibles ne doivent pas être envoyées dans les métadonnées

---

## 📝 Notes

- Les métriques sont stockées indéfiniment (penser à un nettoyage périodique si nécessaire)
- Les alertes peuvent être marquées comme résolues manuellement
- Les statistiques sont calculées en temps réel à chaque requête
- Les index sont optimisés pour les requêtes fréquentes

