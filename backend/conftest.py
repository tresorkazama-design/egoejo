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

