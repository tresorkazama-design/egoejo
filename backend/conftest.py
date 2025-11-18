"""
Configuration pytest pour désactiver le throttling pendant les tests.
"""
import os

# Désactiver le throttling pour tous les tests
# Cela évite que les tests échouent à cause du rate limiting
os.environ['DISABLE_THROTTLE_FOR_TESTS'] = '1'

