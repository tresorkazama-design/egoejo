"""
Tests de sécurité pour les paiements (Stripe, HelloAsso).

Vérifie que :
- Aucune clé API n'apparaît dans les logs
- Aucun secret n'est commité dans le code
- Les secrets sont correctement masqués dans les réponses
"""
import pytest
import logging
import re
from io import StringIO
from django.test import override_settings
from django.contrib.auth import get_user_model
from finance.views import StripeWebhookView
from finance.stripe_utils import verify_stripe_signature, ensure_test_mode

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestPaymentSecretsSecurity:
    """Tests que les secrets ne sont jamais exposés dans les logs ou réponses"""
    
    def test_stripe_secret_not_in_logs(self):
        """Vérifie qu'aucune clé Stripe n'apparaît dans les logs"""
        # Capturer les logs
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        logger = logging.getLogger('finance')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            # Simuler une opération qui pourrait logger des secrets
            from django.conf import settings
            secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
            
            # Vérifier que les secrets ne sont pas vides (sinon le test n'a pas de sens)
            if secret_key or webhook_secret:
                # Capturer les logs générés
                logger.debug(f"Test de logging avec secret_key: {secret_key[:10]}...")
                
                # Récupérer les logs
                log_contents = log_capture.getvalue()
                
                # Vérifier qu'aucun secret complet n'apparaît
                if secret_key:
                    assert secret_key not in log_contents, \
                        f"SECURITE VIOLATION: STRIPE_SECRET_KEY complet trouvé dans les logs"
                    # Vérifier qu'au moins les 10 premiers caractères ne sont pas dans les logs
                    assert secret_key[:10] not in log_contents or len(secret_key) <= 10, \
                        f"SECURITE VIOLATION: Préfixe STRIPE_SECRET_KEY trouvé dans les logs"
                
                if webhook_secret:
                    assert webhook_secret not in log_contents, \
                        f"SECURITE VIOLATION: STRIPE_WEBHOOK_SECRET complet trouvé dans les logs"
        finally:
            logger.removeHandler(handler)
    
    def test_helloasso_secret_not_in_logs(self):
        """Vérifie qu'aucune clé HelloAsso n'apparaît dans les logs"""
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        logger = logging.getLogger('finance')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            from django.conf import settings
            webhook_secret = getattr(settings, 'HELLOASSO_WEBHOOK_SECRET', '')
            
            if webhook_secret:
                logger.debug(f"Test de logging avec webhook_secret: {webhook_secret[:10]}...")
                
                log_contents = log_capture.getvalue()
                
                assert webhook_secret not in log_contents, \
                    f"SECURITE VIOLATION: HELLOASSO_WEBHOOK_SECRET complet trouvé dans les logs"
        finally:
            logger.removeHandler(handler)
    
    def test_stripe_secret_not_in_error_responses(self, client):
        """Vérifie qu'aucun secret n'apparaît dans les réponses d'erreur"""
        # Tester avec une requête invalide qui génère une erreur
        response = client.post(
            '/api/finance/stripe/webhook/',
            data='invalid json',
            content_type='application/json'
        )
        
        # Vérifier que la réponse ne contient pas de secrets
        response_text = response.content.decode('utf-8')
        
        from django.conf import settings
        secret_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        if secret_key:
            assert secret_key not in response_text, \
                "SECURITE VIOLATION: STRIPE_SECRET_KEY trouvé dans la réponse d'erreur"
        
        if webhook_secret:
            assert webhook_secret not in response_text, \
                "SECURITE VIOLATION: STRIPE_WEBHOOK_SECRET trouvé dans la réponse d'erreur"
    
    def test_no_secrets_in_codebase_patterns(self):
        """Vérifie qu'aucun pattern de secret n'est hardcodé dans le code"""
        import os
        import glob
        
        # Patterns de secrets à détecter
        secret_patterns = [
            r'sk_live_[a-zA-Z0-9]{24,}',
            r'sk_test_[a-zA-Z0-9]{24,}',
            r'whsec_[a-zA-Z0-9]{32,}',
            r'pk_live_[a-zA-Z0-9]{24,}',
            r'pk_test_[a-zA-Z0-9]{24,}',
        ]
        
        # Exclure les fichiers de test et migrations
        exclude_patterns = ['__pycache__', '.pyc', 'migrations', 'test_', 'junit.xml']
        
        backend_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        python_files = []
        
        for root, dirs, files in os.walk(backend_dir):
            # Exclure certains dossiers
            dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py') and not any(ex in file for ex in exclude_patterns):
                    python_files.append(os.path.join(root, file))
        
        violations = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            violations.append(f"{file_path}: {matches}")
            except Exception:
                pass  # Ignorer les erreurs de lecture
        
        assert len(violations) == 0, \
            f"SECURITE VIOLATION: Patterns de secrets trouvés dans le code:\n" + "\n".join(violations)


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestPaymentTestModeEnforcement:
    """Tests que le mode test est correctement appliqué"""
    
    @override_settings(STRIPE_TEST_MODE_ONLY=True)
    def test_test_mode_rejects_live_keys(self):
        """Vérifie que le mode test strict refuse les clés live"""
        from django.core.exceptions import ImproperlyConfigured
        
        # Simuler une clé live
        with override_settings(STRIPE_SECRET_KEY='sk_live_PLACEHOLDER_KEY_FOR_TESTING_ONLY'):
            try:
                ensure_test_mode()
                pytest.fail("ensure_test_mode() devrait lever ImproperlyConfigured avec une clé live")
            except ImproperlyConfigured:
                pass  # Comportement attendu
    
    @override_settings(STRIPE_TEST_MODE_ONLY=True)
    def test_test_mode_accepts_test_keys(self):
        """Vérifie que le mode test accepte les clés de test"""
        with override_settings(STRIPE_SECRET_KEY='sk_test_PLACEHOLDER_KEY_FOR_TESTING_ONLY'):
            try:
                ensure_test_mode()
                # Pas d'exception = succès
            except ImproperlyConfigured:
                pytest.fail("ensure_test_mode() ne devrait pas lever d'exception avec une clé de test")

