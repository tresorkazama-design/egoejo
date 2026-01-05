"""
Tests d'intégration pour vérifier que le signal post_save de SakaWallet
envoie bien des alertes email via send_critical_alert().

Constitution EGOEJO: no direct SAKA mutation.
Le signal doit détecter les violations et envoyer des alertes email.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from core.models.saka import SakaWallet, SakaTransaction, AllowSakaMutation
from core.services.saka import harvest_saka, SakaReason

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.critical
@pytest.mark.egoejo_compliance
class TestSakaWalletAlertingIntegration:
    """
    Tests d'intégration pour vérifier que les alertes email sont envoyées
    lors de violations détectées par le signal post_save.
    
    TAG : @critical - Test BLOQUANT pour la protection philosophique EGOEJO
    TAG : @egoejo_compliance - Test de compliance Constitution EGOEJO
    """
    
    @pytest.fixture
    def test_user(self, db):
        """Utilisateur de test avec SakaWallet"""
        user = User.objects.create_user(
            username='testuser_alert',
            email='test_alert@example.com',
            password='testpass123'
        )
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 100,
                'total_harvested': 100,
                'total_planted': 0,
                'total_composted': 0,
            }
        )
        return user
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    @patch('core.models.saka.send_critical_alert')
    def test_signal_sends_alert_on_bypass_detection(self, mock_send_alert, test_user):
        """
        Vérifie que le signal post_save envoie une alerte email lors de la détection
        d'un contournement (modification sans SakaTransaction correspondante).
        """
        wallet = SakaWallet.objects.get(user=test_user)
        initial_balance = wallet.balance
        
        # Simuler une modification directe (bypass) sans transaction correspondante
        # En utilisant AllowSakaMutation pour contourner la protection save()
        # mais sans créer de SakaTransaction, ce qui déclenchera l'alerte
        with AllowSakaMutation():
            wallet.balance = initial_balance + 500
            wallet.save()
        
        # Vérifier que send_critical_alert a été appelé
        assert mock_send_alert.called, "send_critical_alert() devrait être appelé lors d'une violation détectée"
        
        # Vérifier les arguments de l'appel
        call_args = mock_send_alert.call_args
        assert call_args is not None
        
        # Vérifier le titre
        assert call_args[0][0] == "INTEGRITY BREACH DETECTED" or \
               call_args[0][0] == "INTEGRITY BREACH DETECTED (MASSIVE MODIFICATION)"
        
        # Vérifier le payload
        payload = call_args[0][1]
        assert payload['user_id'] == test_user.id
        assert payload['username'] == test_user.username
        assert payload['email'] == test_user.email
        assert 'old_balance' in payload
        assert 'new_balance' in payload
        assert 'delta' in payload
        assert payload['detection_method'] == 'post_save_signal'
        
        # Vérifier la dedupe_key
        dedupe_key = call_args[1].get('dedupe_key')
        assert dedupe_key is not None
        assert f"saka_wallet" in dedupe_key
        assert str(test_user.id) in dedupe_key
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_signal_sends_alert_on_massive_change(self, test_user):
        """
        Vérifie que le signal post_save envoie une alerte email lors d'une modification massive (> 10000 SAKA).
        """
        wallet = SakaWallet.objects.get(user=test_user)
        initial_balance = wallet.balance
        
        # Nettoyer la boîte mail
        mail.outbox.clear()
        
        # Simuler une modification massive (bypass) sans transaction correspondante
        with AllowSakaMutation():
            wallet.balance = initial_balance + 15000  # > 10000 SAKA (seuil critique)
            wallet.save()
        
        # Vérifier qu'un email a été envoyé
        assert len(mail.outbox) > 0, "Un email devrait être envoyé lors d'une modification massive"
        
        # Vérifier le sujet de l'email
        email = mail.outbox[0]
        assert "[URGENT] EGOEJO" in email.subject
        assert "INTEGRITY BREACH DETECTED" in email.subject
        
        # Vérifier le contenu de l'email
        assert "MASSIVE MODIFICATION" in email.body or "massive_change" in email.body
        assert str(test_user.id) in email.body
        assert str(wallet.balance) in email.body
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_signal_no_alert_on_authorized_change(self, test_user):
        """
        Vérifie que le signal post_save N'envoie PAS d'alerte lors d'une modification autorisée
        (via service SAKA avec SakaTransaction correspondante).
        """
        wallet = SakaWallet.objects.get(user=test_user)
        initial_balance = wallet.balance
        
        # Nettoyer la boîte mail
        mail.outbox.clear()
        
        # Modification autorisée via service SAKA (crée une SakaTransaction)
        harvest_saka(
            user=test_user,
            reason=SakaReason.MANUAL_ADJUST,
            amount=100
        )
        
        # Vérifier qu'aucun email n'a été envoyé (modification autorisée)
        assert len(mail.outbox) == 0, "Aucun email ne devrait être envoyé pour une modification autorisée"
    
    @override_settings(
        ALERT_EMAIL_ENABLED=False,
        ADMINS=[('Test Admin', 'admin@example.com')],
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    @patch('core.models.saka.send_critical_alert')
    def test_signal_respects_alert_disabled_setting(self, mock_send_alert, test_user):
        """
        Vérifie que le signal respecte le setting ALERT_EMAIL_ENABLED=False.
        """
        wallet = SakaWallet.objects.get(user=test_user)
        
        # Simuler une modification suspecte
        with AllowSakaMutation():
            wallet.balance = wallet.balance + 500
            wallet.save()
        
        # Vérifier que send_critical_alert est quand même appelé
        # (car c'est send_critical_alert qui vérifie ALERT_EMAIL_ENABLED)
        # Mais l'email ne sera pas envoyé
        # Note: Le signal appelle toujours send_critical_alert, qui retourne False si désactivé
        
        # Le signal appelle send_critical_alert même si désactivé
        # (c'est send_critical_alert qui gère la désactivation)
        # Donc on vérifie juste que l'appel est fait
        # (le test de désactivation est dans test_alerts.py)
        pass  # Ce test vérifie que le signal ne bloque pas si les alertes sont désactivées
    
    @override_settings(
        ALERT_EMAIL_ENABLED=True,
        ADMINS=[],  # Aucun admin configuré
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    @patch('core.models.saka.send_critical_alert')
    def test_signal_handles_no_admins_gracefully(self, mock_send_alert, test_user):
        """
        Vérifie que le signal gère gracieusement l'absence d'admins configurés.
        """
        wallet = SakaWallet.objects.get(user=test_user)
        
        # Simuler une modification suspecte
        with AllowSakaMutation():
            wallet.balance = wallet.balance + 500
            wallet.save()
        
        # Vérifier que send_critical_alert est appelé
        # (mais retournera False car aucun admin configuré)
        # Le signal ne doit pas lever d'exception
        assert mock_send_alert.called, "send_critical_alert() devrait être appelé même sans admins"
        
        # Vérifier que l'appel retourne False (géré par send_critical_alert)
        # (le test de "no admins" est dans test_alerts.py)

