# 📊 MÉTRIQUES D'ALERTES CRITIQUES EGOEJO

**Date** : 2025-01-05  
**Version** : 1.0  
**Objectif** : Observabilité et transparence institutionnelle des mécanismes anti-dérive

---

## 🎯 Vue d'Ensemble

Le système de métriques d'alertes critiques EGOEJO permet d'observer et de rendre opposable institutionnellement le fonctionnement des mécanismes de surveillance automatisés. Ces métriques sont **publiques** et **auditables**, garantissant la transparence sans exposer de données personnelles.

**Caractéristiques** :
- ✅ Comptage mensuel des alertes critiques
- ✅ Total cumulé depuis le début
- ✅ Date de la dernière alerte
- ✅ Aucune donnée personnelle exposée
- ✅ Endpoint public (lecture seule)
- ✅ Cache contrôlé (5 minutes)

---

## 📁 Architecture

### Fichiers Principaux

- **`backend/core/api/compliance_views.py`** : Endpoint API
  - Fonction `critical_alert_metrics()` : Expose les métriques publiquement

- **`backend/core/models/alerts.py`** : Modèle de données
  - Modèle `CriticalAlertEvent` : Enregistre chaque alerte critique
  - Méthode `count_for_month()` : Compte les alertes par mois

- **`backend/core/utils/alerts.py`** : Système d'alerte
  - Fonction `send_critical_alert()` : Envoie les alertes et enregistre les événements

---

## 🔧 Configuration

### Endpoint API

**URL** : `GET /api/compliance/alerts/metrics/`

**Permissions** : Aucune (public, lecture seule)

**Cache** : 5 minutes (300 secondes)

**Format de réponse** :
```json
{
  "total_alerts": 42,
  "alerts_by_month": [
    {"month": "2025-01", "count": 5},
    {"month": "2024-12", "count": 8},
    {"month": "2024-11", "count": 3},
    ...
  ],
  "last_alert_at": "2025-01-05T10:30:00Z"
}
```

### Champs de Réponse

- **`total_alerts`** (int) : Nombre total d'alertes critiques depuis le début
- **`alerts_by_month`** (array) : Liste des 12 derniers mois avec le nombre d'alertes
  - **`month`** (string) : Format YYYY-MM
  - **`count`** (int) : Nombre d'alertes pour ce mois
- **`last_alert_at`** (string | null) : Date ISO-8601 de la dernière alerte, ou `null` si aucune alerte

---

## 📖 Utilisation

### Accès Public

L'endpoint est accessible publiquement sans authentification :

```bash
curl https://egoejo.org/api/compliance/alerts/metrics/
```

### Exemple de Réponse

```json
{
  "total_alerts": 42,
  "alerts_by_month": [
    {"month": "2025-01", "count": 5},
    {"month": "2024-12", "count": 8},
    {"month": "2024-11", "count": 3},
    {"month": "2024-10", "count": 2},
    {"month": "2024-09", "count": 4},
    {"month": "2024-08", "count": 6},
    {"month": "2024-07", "count": 3},
    {"month": "2024-06", "count": 2},
    {"month": "2024-05", "count": 1},
    {"month": "2024-04", "count": 2},
    {"month": "2024-03", "count": 3},
    {"month": "2024-02", "count": 3}
  ],
  "last_alert_at": "2025-01-05T10:30:00Z"
}
```

---

## 🔍 Interprétation des Métriques

### ⚠️ Important : Ce que les métriques NE sont PAS

Les métriques d'alertes critiques **ne sont pas un indicateur d'échec** ou de dysfonctionnement. Au contraire :

- **Alertes élevées** : Indiquent que le système de surveillance fonctionne correctement et détecte les anomalies
- **Alertes faibles** : Peuvent indiquer soit une période calme, soit un problème dans le système de détection
- **Aucune alerte** : Peut indiquer soit une période sans anomalie, soit un dysfonctionnement du système de surveillance

### ✅ Ce que les métriques SONT

Les métriques sont un **indicateur de transparence** et de **vigilance active** :

1. **Transparence** : Preuve que le système surveille activement les violations potentielles
2. **Auditabilité** : Permet aux auditeurs externes de vérifier que les mécanismes fonctionnent
3. **Traçabilité** : Historique mensuel des événements critiques détectés
4. **Opposabilité institutionnelle** : Preuve que les garanties anti-dérive sont actives

### 📊 Interprétation Correcte

**Scénario 1 : Alertes régulières (5-10/mois)**
- ✅ Système de surveillance actif
- ✅ Détection proactive des anomalies
- ✅ Mécanismes anti-dérive fonctionnels

**Scénario 2 : Pic d'alertes (20+/mois)**
- ⚠️ Période d'activité suspecte détectée
- ✅ Système de surveillance réactif
- 🔍 Nécessite investigation approfondie

**Scénario 3 : Aucune alerte (0/mois)**
- ✅ Soit période calme sans anomalie
- ⚠️ Soit problème dans le système de détection
- 🔍 Vérifier que le système de surveillance est actif

---

## 🧪 Tests

### Tests Unitaires

Les tests sont disponibles dans `backend/core/tests/api/test_critical_alert_metrics.py` :

- ✅ Test de structure de réponse
- ✅ Test d'absence de données personnelles
- ✅ Test d'incrémentation des métriques
- ✅ Test de non-incrémentation si alertes désactivées
- ✅ Test de structure `alerts_by_month`
- ✅ Test d'accessibilité publique
- ✅ Test de fonctionnement du cache
- ✅ Test de `last_alert_at`

### Exécution des Tests

```bash
# Tous les tests de métriques
pytest backend/core/tests/api/test_critical_alert_metrics.py -v

# Test spécifique
pytest backend/core/tests/api/test_critical_alert_metrics.py::TestCriticalAlertMetrics::test_metrics_no_personal_data_leak -v
```

---

## ⚠️ Limitations et Notes Importantes

### 1. Pas de Détails d'Alerte

L'endpoint expose uniquement des **métriques agrégées**, pas les détails des alertes individuelles. Cela garantit :
- ✅ Aucune donnée personnelle exposée
- ✅ Protection de la vie privée
- ✅ Sécurité des informations sensibles

### 2. Cache de 5 Minutes

Les métriques sont mises en cache pendant 5 minutes pour optimiser les performances. Cela signifie :
- ⚠️ Les nouvelles alertes peuvent ne pas apparaître immédiatement
- ✅ Les requêtes fréquentes ne surchargent pas la base de données
- ✅ Performance optimale pour les audits externes

### 3. Période d'Historique

L'endpoint expose uniquement les **12 derniers mois**. Pour un historique plus long :
- Utiliser l'admin Django (accès restreint)
- Exporter les données depuis `CriticalAlertEvent`

### 4. Pas de Filtrage

L'endpoint ne permet pas de filtrer par type d'alerte ou par canal. Pour des analyses plus détaillées :
- Utiliser l'admin Django
- Développer un endpoint admin dédié (si nécessaire)

---

## 📊 Monitoring et Logs

### Logs Django

L'endpoint génère des logs dans le logger Django standard :

- **INFO** : Requêtes réussies
- **WARNING** : Erreurs de cache ou de calcul

### Métriques de Performance

L'endpoint est optimisé pour les performances :
- **Cache** : 5 minutes (réduit les requêtes DB)
- **Agrégation** : Calculs optimisés par mois
- **Index** : Index sur `created_at` pour requêtes rapides

---

## 🔐 Sécurité

### Protection des Données Personnelles

- ✅ **Aucune donnée personnelle** : Pas de `user_id`, `username`, `email`, etc.
- ✅ **Agrégation uniquement** : Seules les métriques agrégées sont exposées
- ✅ **Pas de payload** : Le contenu des alertes n'est pas exposé

### Accessibilité

- ✅ **Public** : Accessible sans authentification (transparence)
- ✅ **Lecture seule** : GET uniquement (pas de modification)
- ✅ **Cache contrôlé** : Cache de 5 minutes (performance)

---

## 📚 Références

- **Code Source** : 
  - `backend/core/api/compliance_views.py` (fonction `critical_alert_metrics()`)
  - `backend/core/models/alerts.py` (modèle `CriticalAlertEvent`)
  - `backend/core/utils/alerts.py` (fonction `send_critical_alert()`)

- **Tests** : `backend/core/tests/api/test_critical_alert_metrics.py`
- **Documentation Alertes** : `docs/security/ALERTING_EMAIL.md` et `docs/security/ALERTING_SLACK.md`
- **Documentation Institutionnelle** : `docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md`

---

## 🔔 Usage Institutionnel

### Pour les Auditeurs Externes

Les métriques permettent de vérifier que :
1. ✅ Les mécanismes de surveillance sont actifs
2. ✅ Les alertes sont détectées et enregistrées
3. ✅ Le système fonctionne de manière transparente

### Pour les Fondations et ONU

Les métriques démontrent :
1. ✅ **Vigilance active** : Le système surveille activement les violations
2. ✅ **Transparence** : Les métriques sont publiques et auditables
3. ✅ **Opposabilité** : Preuve que les garanties anti-dérive sont en place

### Pour la Gouvernance

Les métriques permettent de :
1. ✅ **Observer** : Suivre l'évolution des alertes dans le temps
2. ✅ **Décider** : Identifier les périodes nécessitant une attention particulière
3. ✅ **Communiquer** : Démontrer la transparence aux parties prenantes

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-05

