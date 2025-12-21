"""
Configuration pytest pour désactiver le throttling pendant les tests.
"""
import os
import secrets

# Désactiver le throttling pour tous les tests
# Cela évite que les tests échouent à cause du rate limiting
os.environ['DISABLE_THROTTLE_FOR_TESTS'] = '1'

# Générer un token admin sécurisé pour les tests si non défini
# SECURITE : Utilisation de secrets.token_urlsafe() pour éviter les tokens hardcodés
# Le token est généré une seule fois au chargement du module et partagé via os.environ
if 'ADMIN_TOKEN' not in os.environ:
    # Générer un token aléatoire de 32 bytes (44 caractères en base64)
    # Ce token est uniquement utilisé en mode test et n'est jamais commité
    test_admin_token = secrets.token_urlsafe(32)
    os.environ['ADMIN_TOKEN'] = test_admin_token

# Activer les feature flags SAKA pour les tests
# PHILOSOPHIE EGOEJO : Les flags SAKA doivent être activés pour les tests de conformité
os.environ['ENABLE_SAKA'] = 'True'
os.environ['SAKA_COMPOST_ENABLED'] = 'True'
os.environ['SAKA_SILO_REDIS_ENABLED'] = 'True'

# SECURITE : Ne PAS forcer DEBUG=True dans les tests
# Les tests doivent utiliser la configuration de test Django (settings.TESTING)
# Si DEBUG doit être désactivé pour certains tests, utiliser @override_settings(DEBUG=False)
# Forcer DEBUG=True pourrait masquer des problèmes de sécurité et créer des failles en production

