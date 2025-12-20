# 🎯 Architecture des Oracles d'Impact

**Document** : Architecture pour intégrer des données externes dans les scores P3 et P4  
**Date** : 2025-12-19  
**Version** : 1.0  
**Statut** : Architecture préparée (tuyauterie), non connectée aux scores finaux

---

## 🎯 Objectif

Permettre l'intégration de données externes vérifiées (APIs) pour enrichir les scores P3 (Social) et P4 (Sens), actuellement calculés sur des métriques internes uniquement.

**État actuel** :
- P3 : Utilise `project.impact_score` (proxy interne)
- P4 : Formule simplifiée basée sur supporters SAKA + cagnottes (proxy interne)

**Objectif** : Ouvrir P3 et P4 à des données réelles via des oracles externes.

---

## 🏗️ Architecture

### Classe Abstraite : `BaseImpactOracle`

**Fichier** : `backend/core/services/impact_oracles.py`

**Méthodes abstraites** :
- `fetch_impact_data(project)` : Récupère les données depuis la source externe
- `get_impact_metrics(data)` : Extrait les métriques pour P3/P4

**Méthodes utilitaires** :
- `validate_data(data)` : Valide les données récupérées
- `get_oracle_info()` : Retourne les métadonnées de l'oracle
- `is_enabled()` : Vérifie si l'oracle est activé

---

### Implémentations Concrètes

#### 1. `CO2AvoidedOracle`

**Identifiant** : `co2_avoided`

**Description** : Mesure la quantité de CO2 évitée par le projet (en kg CO2e)

**Dimensions** : `['P3']` (contribue au score P3)

**Métriques retournées** :
```python
{
    'p3_contributions': {
        'co2_avoided_kg': 500.0,
        'co2_score': 50,  # Score normalisé (0-100)
    },
    'p4_contributions': {},  # Ne contribue pas à P4
    'metadata': {
        'last_updated': '2025-12-19T10:00:00Z',
        'source': 'co2_avoided',
        'confidence': 0.7,
    }
}
```

**Configuration** :
```python
IMPACT_ORACLES = {
    'CO2_API_ENDPOINT': 'https://api.carbon.example.com/v1/calculate',
    'CO2_API_KEY': 'your-api-key',
}
```

---

#### 2. `SocialImpactOracle`

**Identifiant** : `social_impact`

**Description** : Mesure l'impact social (personnes impactées, emplois créés)

**Dimensions** : `['P3', 'P4']` (contribue aux scores P3 et P4)

**Métriques retournées** :
```python
{
    'p3_contributions': {
        'people_impacted': 500,
        'jobs_created': 10,
        'social_impact_score': 70,
    },
    'p4_contributions': {
        'purpose_alignment': 0.75,  # Score de cohérence (0-1)
    },
    'metadata': {
        'last_updated': '2025-12-19T10:00:00Z',
        'source': 'social_impact',
        'confidence': 0.6,
    }
}
```

---

### Registre des Oracles

**Fichier** : `backend/core/services/impact_oracles.py`

```python
ORACLE_REGISTRY = {
    'co2_avoided': CO2AvoidedOracle,
    'social_impact': SocialImpactOracle,
}
```

**Ajout d'un nouvel oracle** :
1. Créer une classe héritant de `BaseImpactOracle`
2. Implémenter `fetch_impact_data()` et `get_impact_metrics()`
3. Ajouter au registre : `ORACLE_REGISTRY['nouvel_oracle'] = NouvelOracle`

---

## 📊 Modèle Projet

### Champ `active_oracles`

**Migration** : `0028_add_active_oracles_to_projet.py`

**Type** : `JSONField` (liste de strings)

**Exemple** :
```python
project.active_oracles = ['co2_avoided', 'social_impact']
project.save()
```

**Format** :
```json
["co2_avoided", "social_impact"]
```

---

## 🔧 Service OracleManager

**Fichier** : `backend/core/services/oracle_manager.py`

**Responsabilités** :
- Exécution des oracles actifs pour un projet
- Cache des résultats (1 heure par défaut)
- Agrégation des métriques de plusieurs oracles
- Gestion des erreurs et fallbacks

**Méthodes principales** :

### `get_oracle_data(project, force_refresh=False)`

Récupère les données de tous les oracles actifs.

**Retour** :
```python
{
    'oracles': {
        'co2_avoided': {
            'data': {...},
            'metrics': {...},
            'status': 'success'
        },
        ...
    },
    'aggregated_metrics': {
        'p3_contributions': {
            'co2_avoided_kg': [{'value': 500, 'source': 'co2_avoided'}],
            'people_impacted': [{'value': 500, 'source': 'social_impact'}],
        },
        'p4_contributions': {
            'purpose_alignment': [{'value': 0.75, 'source': 'social_impact'}],
        },
    },
    'metadata': {
        'last_updated': '2025-12-19T10:00:00Z',
        'oracles_count': 2,
        'success_count': 2,
    }
}
```

---

## 📝 Utilisation

### 1. Activer des oracles pour un projet

```python
from core.models.projects import Projet

project = Projet.objects.get(id=1)
project.active_oracles = ['co2_avoided', 'social_impact']
project.save()
```

### 2. Récupérer les données des oracles

```python
from core.services.oracle_manager import OracleManager

# Récupérer les données (avec cache)
oracle_data = OracleManager.get_oracle_data(project)

# Forcer le refresh (ignorer le cache)
oracle_data = OracleManager.get_oracle_data(project, force_refresh=True)

# Accéder aux métriques agrégées
p3_contribs = oracle_data['aggregated_metrics']['p3_contributions']
p4_contribs = oracle_data['aggregated_metrics']['p4_contributions']
```

### 3. Lister les oracles disponibles

```python
from core.services.oracle_manager import OracleManager

available_oracles = OracleManager.get_available_oracles()
# [
#     {
#         'oracle_id': 'co2_avoided',
#         'name': 'Oracle CO2 Évité',
#         'description': '...',
#         'impact_dimensions': ['P3'],
#     },
#     ...
# ]
```

---

## ⚠️ État Actuel

### ✅ Implémenté

- [x] Classe abstraite `BaseImpactOracle`
- [x] Implémentation `CO2AvoidedOracle`
- [x] Implémentation `SocialImpactOracle`
- [x] Champ `active_oracles` dans le modèle `Projet`
- [x] Service `OracleManager` pour gestion centralisée
- [x] Cache des résultats (1 heure)
- [x] Agrégation des métriques

### ❌ Non Implémenté (Intentionnel)

- [ ] **Connexion au calcul final P3/P4** : Les métriques des oracles ne sont PAS encore utilisées dans `update_project_4p()`
- [ ] **Intégration dans l'API** : Pas encore d'endpoint pour exposer les données oracle
- [ ] **Appels API réels** : Les oracles simulent actuellement les appels API

---

## 🔄 Prochaines Étapes

### Phase 1 : Validation Architecture (Actuelle)

- [x] Créer l'architecture abstraite
- [x] Implémenter 2 exemples concrets
- [x] Ajouter champ `active_oracles` au modèle
- [x] Créer service de gestion

### Phase 2 : Intégration API Réelle

- [ ] Connecter `CO2AvoidedOracle` à une API carbone réelle
- [ ] Connecter `SocialImpactOracle` à une API sociale réelle
- [ ] Gérer authentification et rate limiting
- [ ] Gérer les erreurs API (retry, fallback)

### Phase 3 : Connexion aux Scores

- [ ] Modifier `update_project_4p()` pour utiliser les métriques oracle
- [ ] Créer formule d'agrégation P3 (oracles + proxy interne)
- [ ] Créer formule d'agrégation P4 (oracles + proxy interne)
- [ ] Tests de validation

### Phase 4 : Exposition API

- [ ] Endpoint `/api/projets/{id}/oracles/` pour récupérer les données
- [ ] Endpoint `/api/oracles/available/` pour lister les oracles disponibles
- [ ] Documentation API

---

## 📚 Exemples de Code

### Créer un Nouvel Oracle

```python
from core.services.impact_oracles import BaseImpactOracle

class BiodiversityOracle(BaseImpactOracle):
    oracle_id = 'biodiversity'
    name = 'Oracle Biodiversité'
    description = 'Mesure l\'impact sur la biodiversité'
    impact_dimensions = ['P3']
    
    def fetch_impact_data(self, project):
        # Appel API réel ou simulation
        return {
            'raw_data': {
                'species_protected': 25,
                'habitat_area_ha': 10.5,
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': self.oracle_id,
            'status': 'success',
        }
    
    def get_impact_metrics(self, data):
        raw_data = data.get('raw_data', {})
        return {
            'p3_contributions': {
                'species_protected': raw_data.get('species_protected', 0),
                'habitat_area_ha': raw_data.get('habitat_area_ha', 0),
            },
            'p4_contributions': {},
            'metadata': {
                'last_updated': data.get('timestamp'),
                'source': self.oracle_id,
                'confidence': 0.8,
            }
        }

# Ajouter au registre
from core.services.impact_oracles import ORACLE_REGISTRY
ORACLE_REGISTRY['biodiversity'] = BiodiversityOracle
```

---

## 🔒 Sécurité & Configuration

### Variables d'Environnement

```bash
# Configuration des oracles
IMPACT_ORACLES_CO2_API_ENDPOINT=https://api.carbon.example.com/v1/calculate
IMPACT_ORACLES_CO2_API_KEY=your-api-key
IMPACT_ORACLES_SOCIAL_API_ENDPOINT=https://api.social.example.com/v1/impact
IMPACT_ORACLES_SOCIAL_API_KEY=your-api-key
```

### Settings Django

```python
# backend/config/settings.py
IMPACT_ORACLES = {
    'CO2_API_ENDPOINT': os.environ.get('IMPACT_ORACLES_CO2_API_ENDPOINT', ''),
    'CO2_API_KEY': os.environ.get('IMPACT_ORACLES_CO2_API_KEY', ''),
    'SOCIAL_API_ENDPOINT': os.environ.get('IMPACT_ORACLES_SOCIAL_API_ENDPOINT', ''),
    'SOCIAL_API_KEY': os.environ.get('IMPACT_ORACLES_SOCIAL_API_KEY', ''),
}
```

---

## 🧪 Tests

### Tests à Créer

1. **Test classe abstraite** : Vérifier que `BaseImpactOracle` ne peut pas être instanciée
2. **Test CO2AvoidedOracle** : Vérifier récupération et extraction métriques
3. **Test SocialImpactOracle** : Vérifier récupération et extraction métriques
4. **Test OracleManager** : Vérifier agrégation et cache
5. **Test intégration Projet** : Vérifier que `active_oracles` fonctionne

---

## 📖 Références

- **Service Oracles** : `backend/core/services/impact_oracles.py`
- **Service Manager** : `backend/core/services/oracle_manager.py`
- **Modèle Projet** : `backend/core/models/projects.py`
- **Migration** : `backend/core/migrations/0028_add_active_oracles_to_projet.py`
- **Service Impact 4P** : `backend/core/services/impact_4p.py`

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Architecture préparée (tuyauterie), non connectée aux scores finaux**

