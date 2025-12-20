"""
Configuration pytest pour désactiver le throttling pendant les tests.
"""
import os

# Désactiver le throttling pour tous les tests
# Cela évite que les tests échouent à cause du rate limiting
os.environ['DISABLE_THROTTLE_FOR_TESTS'] = '1'

# Définir le token admin pour les tests si non défini
# Cela permet aux tests d'administration de fonctionner
if 'ADMIN_TOKEN' not in os.environ:
    os.environ['ADMIN_TOKEN'] = 'test-admin-token-123'

# Activer les feature flags SAKA pour les tests
# PHILOSOPHIE EGOEJO : Les flags SAKA doivent être activés pour les tests de conformité
os.environ['ENABLE_SAKA'] = 'True'
os.environ['SAKA_COMPOST_ENABLED'] = 'True'
os.environ['SAKA_SILO_REDIS_ENABLED'] = 'True'

# Forcer DEBUG=True pour les tests (évite le blocage production)
os.environ['DEBUG'] = '1'

