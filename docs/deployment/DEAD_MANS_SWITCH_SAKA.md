# 🚨 Dead Man's Switch SAKA

**Document** : Mécanisme de sécurité pour empêcher le démarrage en production sans SAKA  
**Date** : 2025-12-19  
**Version** : 1.0  
**Statut** : ✅ Implémenté

---

## 🎯 Objectif

Empêcher EGOEJO de démarrer en production si le protocole SAKA est désactivé par erreur de configuration.

**Risque** : Si `ENABLE_SAKA=False` en production, la structure relationnelle fondamentale d'EGOEJO est désactivée, ce qui est inacceptable.

---

## 🔒 Mécanisme

### Implémentation

**Fichier** : `backend/core/apps.py`

**Méthode** : `CoreConfig.check_saka_flags_in_production()`

**Exécution** : Automatique lors du démarrage Django (méthode `ready()`)

**Exception** : `ImproperlyConfigured` (exception Django standard)

---

## ⚙️ Fonctionnement

### Conditions de Déclenchement

1. **Mode Production** : `DEBUG = False`
2. **SAKA Désactivé** : `ENABLE_SAKA = False`

Si les deux conditions sont réunies → **Exception bloquante**

### Message d'Erreur

```
🚨 CRITICAL SAFETY STOP 🚨

Attempting to run Production without SAKA Protocol.
Enable ENABLE_SAKA env var.

PHILOSOPHIE EGOEJO :
La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.
Elle ne peut PAS être désactivée en production.

ACTION REQUISE :
Activez le protocole SAKA en définissant la variable d'environnement :
  ENABLE_SAKA=True

Le serveur ne démarrera pas tant que cette condition n'est pas remplie.
```

---

## 🛡️ Protection

### Serveurs Protégés

- ✅ **Gunicorn** : Exception levée avant le démarrage des workers
- ✅ **Daphne** : Exception levée avant le démarrage du serveur ASGI
- ✅ **uWSGI** : Exception levée avant le démarrage des processus
- ✅ **runserver** : Exception levée (mais uniquement en production)

### Mode Développement

En mode développement (`DEBUG=True`), la vérification est **ignorée** pour permettre :
- Tests unitaires avec SAKA désactivé
- Développement local sans configuration complète
- Debugging

---

## 📋 Exemple d'Erreur

### Scénario : Démarrage en Production sans SAKA

```bash
# Configuration (production)
export DEBUG=False
export ENABLE_SAKA=False

# Tentative de démarrage
gunicorn config.wsgi:application

# Résultat :
# django.core.exceptions.ImproperlyConfigured: 
# CRITICAL SAFETY STOP: Attempting to run Production without SAKA Protocol. 
# Enable ENABLE_SAKA env var.
```

**Le serveur ne démarre pas** → Protection garantie ✅

---

## ✅ Scénario de Succès

### Configuration Correcte

```bash
# Configuration (production)
export DEBUG=False
export ENABLE_SAKA=True

# Démarrage
gunicorn config.wsgi:application

# Résultat :
# ✅ Dead Man's Switch SAKA : Protocole SAKA activé en production
# [INFO] Application démarrée avec succès
```

---

## 🔍 Code Source

### Méthode `check_saka_flags_in_production()`

```python
def check_saka_flags_in_production(self):
    """
    Dead Man's Switch : Vérifie que le protocole SAKA est activé en production.
    """
    # Ne vérifier qu'en production (DEBUG=False)
    if settings.DEBUG:
        logger.debug("Mode développement détecté : Dead Man's Switch SAKA ignoré")
        return
    
    # Dead Man's Switch : Vérifier ENABLE_SAKA en production
    if not getattr(settings, 'ENABLE_SAKA', False):
        raise ImproperlyConfigured(
            "CRITICAL SAFETY STOP: Attempting to run Production without SAKA Protocol. Enable ENABLE_SAKA env var."
        )
    
    logger.info("✅ Dead Man's Switch SAKA : Protocole SAKA activé en production")
```

### Appel dans `ready()`

```python
def ready(self):
    # ...
    # Vérification des feature flags SAKA en production
    self.check_saka_flags_in_production()
    # ...
```

---

## 🧪 Tests

### Test de la Vérification

```python
from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps

class DeadMansSwitchTestCase(TestCase):
    @override_settings(DEBUG=False, ENABLE_SAKA=False)
    def test_dead_mans_switch_blocks_production_without_saka(self):
        """Test que le Dead Man's Switch bloque le démarrage en production sans SAKA"""
        with self.assertRaises(ImproperlyConfigured) as cm:
            # Réinitialiser l'app pour déclencher ready()
            apps.get_app_config('core').ready()
        
        self.assertIn("CRITICAL SAFETY STOP", str(cm.exception))
        self.assertIn("ENABLE_SAKA", str(cm.exception))
    
    @override_settings(DEBUG=False, ENABLE_SAKA=True)
    def test_dead_mans_switch_allows_production_with_saka(self):
        """Test que le Dead Man's Switch permet le démarrage en production avec SAKA"""
        # Ne doit pas lever d'exception
        try:
            apps.get_app_config('core').ready()
        except ImproperlyConfigured:
            self.fail("Dead Man's Switch ne devrait pas bloquer si ENABLE_SAKA=True")
    
    @override_settings(DEBUG=True, ENABLE_SAKA=False)
    def test_dead_mans_switch_ignored_in_debug(self):
        """Test que le Dead Man's Switch est ignoré en mode DEBUG"""
        # Ne doit pas lever d'exception en mode DEBUG
        try:
            apps.get_app_config('core').ready()
        except ImproperlyConfigured:
            self.fail("Dead Man's Switch ne devrait pas bloquer en mode DEBUG")
```

---

## 📚 Références

- **Code Source** : `backend/core/apps.py` (méthode `check_saka_flags_in_production()`)
- **WSGI** : `backend/config/wsgi.py`
- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`

---

## 🔄 Historique

- **2025-12-19** : Implémentation du Dead Man's Switch
  - Utilisation de `ImproperlyConfigured` au lieu de `RuntimeError`
  - Vérification uniquement de `ENABLE_SAKA` (flag principal)
  - Message d'erreur standardisé

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : ✅ Implémenté et actif**

