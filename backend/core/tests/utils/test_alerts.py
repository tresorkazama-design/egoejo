"""
Tests pour le système d'alerte critique EGOEJO.

Vérifie que send_critical_alert fonctionne correctement avec :
- Dédoublonnage via cache
- Payload structuré JSON
- Gestion robuste des erreurs SMTP
- Configuration via variables d'environnement
"""
import pytest
from unittest.mock import patch, MagicMock, call
from django.core.cache import cache
from django.core import mail
from django.conf import settings
from django.test import override_settings

from core.utils.alerts import send_critical_alert, DEDUPE_CACHE_TTL


@pytest.mark.django_db
class TestSendCriticalAlert:
    """Tests pour send_critical_alert"""
    
    def setup_method(self):
        """Nettoyer le cache avant chaque test"""
        cache.clear()
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_send_critical_alert_success(self):
        """Test que send_critical_alert envoie un email correctement"""
        payload = {
            "user_id": 123,
            "username": "testuser",
            "old_balance": 1000,
            "new_balance": 2000,
            "delta": 1000,
            "detection_method": "post_save_signal"
        }
        
        result = send_critical_alert(
            title="TEST ALERT",
            payload=payload,
            dedupe_key="test:123"
        )
        
        assert result is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert "[URGENT] EGOEJO TEST ALERT" in email.subject
        assert "TEST ALERT" in email.body
        assert "user_id: 123" in email.body
        assert "username: testuser" in email.body
        assert "PAYLOAD STRUCTURÉ (JSON)" in email.body
    
    @override_settings(
        ALERT_EMAIL_ENABLED=False,
        ADMINS=[('Test Admin', 'admin@example.com')]
    )
    def test_send_critical_alert_disabled(self):
        """Test que send_critical_alert retourne False si les alertes sont désactivées"""
        result = send_critical_alert(
            title="TEST ALERT",
            payload={"test": "data"},
            dedupe_key="test:123"
        )
        
        assert result is False
        assert len(mail.outbox) == 0
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_send_critical_alert_no_admins(self):
        """Test que send_critical_alert retourne False si aucun admin n'est configuré"""
        result = send_critical_alert(
            title="TEST ALERT",
            payload={"test": "data"},
            dedupe_key="test:123"
        )
        
        assert result is False
        assert len(mail.outbox) == 0
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_send_critical_alert_deduplication(self):
        """Test que send_critical_alert déduplique les alertes via cache"""
        payload = {"test": "data"}
        
        # Premier appel
        result1 = send_critical_alert(
            title="TEST ALERT",
            payload=payload,
            dedupe_key="test:123"
        )
        
        # Deuxième appel avec la même clé (dans les 5 minutes)
        result2 = send_critical_alert(
            title="TEST ALERT",
            payload=payload,
            dedupe_key="test:123"
        )
        
        assert result1 is True
        assert result2 is True  # Considéré comme succès car déjà envoyé
        assert len(mail.outbox) == 1  # Un seul email envoyé
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_send_critical_alert_different_dedupe_keys(self):
        """Test que send_critical_alert envoie plusieurs emails avec des clés différentes"""
        payload = {"test": "data"}
        
        # Premier appel
        result1 = send_critical_alert(
            title="TEST ALERT",
            payload=payload,
            dedupe_key="test:123"
        )
        
        # Deuxième appel avec une clé différente
        result2 = send_critical_alert(
            title="TEST ALERT",
            payload=payload,
            dedupe_key="test:456"
        )
        
        assert result1 is True
        assert result2 is True
        assert len(mail.outbox) == 2  # Deux emails envoyés
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_send_critical_alert_no_dedupe_key(self):
        """Test que send_critical_alert envoie toujours si pas de dedupe_key"""
        payload = {"test": "data"}
        
        # Premier appel
        result1 = send_critical_alert(
            title="TEST ALERT",
            payload=payload
        )
        
        # Deuxième appel sans dedupe_key
        result2 = send_critical_alert(
            title="TEST ALERT",
            payload=payload
        )
        
        assert result1 is True
        assert result2 is True
        assert len(mail.outbox) == 2  # Deux emails envoyés (pas de dédoublonnage)
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        ALERT_EMAIL_SUBJECT_PREFIX='[CRITICAL] EGOEJO'
    )
    @patch('core.utils.alerts.mail_admins')
    def test_send_critical_alert_custom_subject_prefix(self, mock_mail_admins):
        """Test que send_critical_alert utilise le préfixe de sujet personnalisé"""
        send_critical_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        mock_mail_admins.assert_called_once()
        call_args = mock_mail_admins.call_args
        assert "[CRITICAL] EGOEJO TEST ALERT" in call_args[1]['subject']
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')]
    )
    @patch('core.utils.alerts.mail_admins')
    def test_send_critical_alert_custom_subject_prefix_override(self, mock_mail_admins):
        """Test que send_critical_alert accepte un préfixe de sujet personnalisé"""
        send_critical_alert(
            title="TEST ALERT",
            payload={"test": "data"},
            subject_prefix="[CUSTOM]"
        )
        
        mock_mail_admins.assert_called_once()
        call_args = mock_mail_admins.call_args
        assert "[CUSTOM] TEST ALERT" in call_args[1]['subject']
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')]
    )
    @patch('core.utils.alerts.mail_admins')
    def test_send_critical_alert_payload_structure(self, mock_mail_admins):
        """Test que send_critical_alert structure correctement le payload JSON"""
        payload = {
            "user_id": 123,
            "nested": {
                "key": "value"
            },
            "list": [1, 2, 3]
        }
        
        send_critical_alert(
            title="TEST ALERT",
            payload=payload
        )
        
        mock_mail_admins.assert_called_once()
        call_args = mock_mail_admins.call_args
        message = call_args[1]['message']
        
        # Vérifier que le JSON est présent
        assert "PAYLOAD STRUCTURÉ (JSON)" in message
        assert '"user_id": 123' in message
        assert '"nested"' in message
        assert '"list"' in message
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')]
    )
    @patch('core.utils.alerts.mail_admins')
    @patch('core.utils.alerts.logger')
    def test_send_critical_alert_smtp_error_handling(self, mock_logger, mock_mail_admins):
        """Test que send_critical_alert gère correctement les erreurs SMTP"""
        # Simuler une erreur SMTP
        mock_mail_admins.side_effect = Exception("SMTP connection failed")
        
        result = send_critical_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is False
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert "Échec envoi email alerte critique" in error_call[0][0]
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    @patch('core.utils.alerts.cache')
    def test_send_critical_alert_cache_set(self, mock_cache):
        """Test que send_critical_alert met en cache la clé de dédoublonnage"""
        mock_cache.get.return_value = None  # Pas encore en cache
        mock_cache.set = MagicMock()
        
        send_critical_alert(
            title="TEST ALERT",
            payload={"test": "data"},
            dedupe_key="test:123"
        )
        
        # Vérifier que cache.set a été appelé avec la bonne clé et TTL
        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        assert call_args[0][0] == "critical_alert:test:123"
        assert call_args[0][1] is True
        assert call_args[0][2] == DEDUPE_CACHE_TTL


@pytest.mark.django_db
class TestSendWebhookAlert:
    """Tests pour send_webhook_alert"""
    
    def setup_method(self):
        """Nettoyer le cache avant chaque test"""
        cache.clear()
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=False,
        ALERT_WEBHOOK_URL='https://example.com/webhook'
    )
    @patch('core.utils.alerts.requests')
    def test_send_webhook_alert_disabled(self, mock_requests):
        """Test que send_webhook_alert retourne False si les webhooks sont désactivés"""
        from core.utils.alerts import send_webhook_alert
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is False
        mock_requests.post.assert_not_called()
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='',
        ALERT_WEBHOOK_TYPE='generic'
    )
    @patch('core.utils.alerts.requests')
    def test_send_webhook_alert_no_url(self, mock_requests):
        """Test que send_webhook_alert retourne False si l'URL n'est pas configurée"""
        from core.utils.alerts import send_webhook_alert
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is False
        mock_requests.post.assert_not_called()
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://example.com/webhook',
        ALERT_WEBHOOK_TYPE='generic',
        ALERT_WEBHOOK_TIMEOUT_SECONDS=5
    )
    @patch('core.utils.alerts.requests')
    def test_send_webhook_alert_generic_success(self, mock_requests):
        """Test que send_webhook_alert envoie un webhook generic avec succès"""
        from core.utils.alerts import send_webhook_alert
        
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        payload = {
            "user_id": 123,
            "username": "testuser",
            "delta": 1000
        }
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload=payload
        )
        
        assert result is True
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        
        # Vérifier l'URL
        assert call_args[0][0] == 'https://example.com/webhook'
        
        # Vérifier le payload
        webhook_payload = call_args[1]['json']
        assert webhook_payload['title'] == "TEST ALERT"
        assert webhook_payload['payload'] == payload
        assert 'timestamp' in webhook_payload
        assert webhook_payload['source'] == 'egoejo_critical_alert'
        
        # Vérifier les headers
        assert call_args[1]['headers']['Content-Type'] == 'application/json'
        
        # Vérifier le timeout
        assert call_args[1]['timeout'] == 5
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://hooks.slack.com/services/XXX',
        ALERT_WEBHOOK_TYPE='slack',
        ALERT_WEBHOOK_TIMEOUT_SECONDS=5
    )
    @patch('core.utils.alerts.requests')
    def test_send_webhook_alert_slack_success(self, mock_requests):
        """Test que send_webhook_alert envoie un webhook Slack avec succès"""
        from core.utils.alerts import send_webhook_alert
        
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        payload = {
            "user_id": 123,
            "username": "testuser",
            "delta": 1000
        }
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload=payload
        )
        
        assert result is True
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        
        # Vérifier le payload Slack
        webhook_payload = call_args[1]['json']
        assert 'text' in webhook_payload
        assert 'blocks' in webhook_payload
        assert webhook_payload['blocks'][0]['type'] == 'header'
        assert 'TEST ALERT' in webhook_payload['blocks'][0]['text']['text']
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://example.com/webhook',
        ALERT_WEBHOOK_TYPE='generic'
    )
    @patch('core.utils.alerts.requests')
    @patch('core.utils.alerts.logger')
    def test_send_webhook_alert_timeout(self, mock_logger, mock_requests):
        """Test que send_webhook_alert gère correctement les timeouts"""
        from core.utils.alerts import send_webhook_alert
        from requests.exceptions import Timeout
        
        # Simuler un timeout
        mock_requests.post.side_effect = Timeout("Connection timeout")
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is False
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args
        assert "timeout" in warning_call[0][0].lower()
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://example.com/webhook',
        ALERT_WEBHOOK_TYPE='generic'
    )
    @patch('core.utils.alerts.requests')
    @patch('core.utils.alerts.logger')
    def test_send_webhook_alert_network_error(self, mock_logger, mock_requests):
        """Test que send_webhook_alert gère correctement les erreurs réseau"""
        from core.utils.alerts import send_webhook_alert
        from requests.exceptions import ConnectionError
        
        # Simuler une erreur réseau
        mock_requests.post.side_effect = ConnectionError("Connection failed")
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is False
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args
        assert "erreur réseau" in warning_call[0][0].lower() or "network" in warning_call[0][0].lower()
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://example.com/webhook',
        ALERT_WEBHOOK_TYPE='generic'
    )
    @patch('core.utils.alerts.requests')
    @patch('core.utils.alerts.logger')
    def test_send_webhook_alert_http_error(self, mock_logger, mock_requests):
        """Test que send_webhook_alert gère correctement les erreurs HTTP (status != 2xx)"""
        from core.utils.alerts import send_webhook_alert
        
        # Mock d'une réponse HTTP avec erreur
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_requests.post.return_value = mock_response
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is False
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args
        assert "échoué" in warning_call[0][0].lower() or "failed" in warning_call[0][0].lower()
    
    @override_settings(
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://example.com/webhook',
        ALERT_WEBHOOK_TYPE='invalid_type'
    )
    @patch('core.utils.alerts.requests')
    @patch('core.utils.alerts.logger')
    def test_send_webhook_alert_invalid_type(self, mock_logger, mock_requests):
        """Test que send_webhook_alert utilise 'generic' si le type est invalide"""
        from core.utils.alerts import send_webhook_alert
        
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        result = send_webhook_alert(
            title="TEST ALERT",
            payload={"test": "data"}
        )
        
        assert result is True
        mock_logger.warning.assert_called_once()  # Warning pour type invalide
        call_args = mock_requests.post.call_args
        webhook_payload = call_args[1]['json']
        # Vérifier que c'est le format generic (pas slack)
        assert 'source' in webhook_payload
        assert 'blocks' not in webhook_payload
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        ALERT_WEBHOOK_ENABLED=True,
        ALERT_WEBHOOK_URL='https://example.com/webhook',
        ALERT_WEBHOOK_TYPE='generic',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    @patch('core.utils.alerts.requests')
    def test_send_critical_alert_calls_webhook(self, mock_requests):
        """Test que send_critical_alert appelle aussi send_webhook_alert"""
        from core.utils.alerts import send_critical_alert
        
        # Mock de la réponse HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        payload = {"test": "data"}
        
        result = send_critical_alert(
            title="TEST ALERT",
            payload=payload
        )
        
        # Vérifier que l'email a été envoyé
        assert result is True
        assert len(mail.outbox) == 1
        
        # Vérifier que le webhook a été appelé
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert call_args[0][0] == 'https://example.com/webhook'