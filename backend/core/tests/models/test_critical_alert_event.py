"""
Tests pour le modèle CriticalAlertEvent.

Vérifie :
- Création d'événements
- Dédoublonnage n'incrémente pas le compteur
- Agrégation correcte (count_for_month, count_by_event_type, count_by_channel)
- Gestion timezone/UTC
"""

import pytest
from django.utils import timezone
from datetime import datetime, timedelta
from core.models.alerts import CriticalAlertEvent


@pytest.mark.django_db
@pytest.mark.critical
class TestCriticalAlertEvent:
    """Tests pour CriticalAlertEvent"""
    
    def test_create_from_alert(self):
        """Test la création d'un événement d'alerte"""
        payload = {
            "user_id": 123,
            "username": "testuser",
            "violation_type": "saka_wallet_bypass",
            "delta": 1000
        }
        
        event = CriticalAlertEvent.create_from_alert(
            title="INTEGRITY BREACH DETECTED",
            payload=payload,
            channel="email",
            fingerprint="test:123",
            severity="critical"
        )
        
        assert event.event_type == "INTEGRITY BREACH DETECTED"
        assert event.severity == "critical"
        assert event.channel == "email"
        assert event.fingerprint == "test:123"
        assert event.payload_excerpt is not None
        assert event.payload_excerpt["user_id"] == 123
        assert event.payload_excerpt["username"] == "testuser"
        assert event.created_at is not None
    
    def test_create_from_alert_with_webhook(self):
        """Test la création d'un événement avec webhook"""
        payload = {"test": "data"}
        
        event = CriticalAlertEvent.create_from_alert(
            title="TEST ALERT",
            payload=payload,
            channel="both",  # Email + Webhook
            fingerprint="test:456",
            severity="critical"
        )
        
        assert event.channel == "both"
    
    def test_count_for_month_empty(self):
        """Test count_for_month avec aucun événement"""
        now = timezone.now()
        count = CriticalAlertEvent.count_for_month(now.year, now.month)
        assert count == 0
    
    def test_count_for_month_with_events(self):
        """Test count_for_month avec des événements"""
        now = timezone.now()
        
        # Créer 3 événements ce mois-ci
        for i in range(3):
            CriticalAlertEvent.create_from_alert(
                title=f"TEST ALERT {i}",
                payload={"test": i},
                channel="email",
                fingerprint=f"test:{i}",
                severity="critical"
            )
        
        count = CriticalAlertEvent.count_for_month(now.year, now.month)
        assert count == 3
    
    def test_count_for_month_timezone_utc(self):
        """Test que count_for_month utilise UTC correctement"""
        # Créer un événement avec une date spécifique en UTC
        target_year = 2025
        target_month = 1
        
        # Créer un événement en janvier 2025
        event = CriticalAlertEvent.create_from_alert(
            title="TEST ALERT UTC",
            payload={"test": "utc"},
            channel="email",
            fingerprint="test:utc",
            severity="critical"
        )
        
        # Forcer la date à janvier 2025
        event.created_at = timezone.make_aware(datetime(target_year, target_month, 15, 12, 0, 0))
        event.save()
        
        # Vérifier le comptage pour janvier 2025
        count = CriticalAlertEvent.count_for_month(target_year, target_month)
        assert count == 1
        
        # Vérifier que décembre 2024 n'a pas cet événement
        count_dec = CriticalAlertEvent.count_for_month(2024, 12)
        assert count_dec == 0
        
        # Vérifier que février 2025 n'a pas cet événement
        count_feb = CriticalAlertEvent.count_for_month(2025, 2)
        assert count_feb == 0
    
    def test_count_by_event_type_for_month(self):
        """Test count_by_event_type_for_month"""
        now = timezone.now()
        
        # Créer des événements de types différents
        CriticalAlertEvent.create_from_alert(
            title="TYPE_A",
            payload={"test": 1},
            channel="email",
            fingerprint="test:1",
            severity="critical"
        )
        CriticalAlertEvent.create_from_alert(
            title="TYPE_A",
            payload={"test": 2},
            channel="email",
            fingerprint="test:2",
            severity="critical"
        )
        CriticalAlertEvent.create_from_alert(
            title="TYPE_B",
            payload={"test": 3},
            channel="email",
            fingerprint="test:3",
            severity="critical"
        )
        
        by_type = CriticalAlertEvent.count_by_event_type_for_month(now.year, now.month)
        
        assert "TYPE_A" in by_type
        assert by_type["TYPE_A"] == 2
        assert "TYPE_B" in by_type
        assert by_type["TYPE_B"] == 1
    
    def test_count_by_channel_for_month(self):
        """Test count_by_channel_for_month"""
        now = timezone.now()
        
        # Créer des événements sur différents canaux
        CriticalAlertEvent.create_from_alert(
            title="TEST ALERT",
            payload={"test": 1},
            channel="email",
            fingerprint="test:1",
            severity="critical"
        )
        CriticalAlertEvent.create_from_alert(
            title="TEST ALERT",
            payload={"test": 2},
            channel="webhook",
            fingerprint="test:2",
            severity="critical"
        )
        CriticalAlertEvent.create_from_alert(
            title="TEST ALERT",
            payload={"test": 3},
            channel="both",
            fingerprint="test:3",
            severity="critical"
        )
        CriticalAlertEvent.create_from_alert(
            title="TEST ALERT",
            payload={"test": 4},
            channel="both",
            fingerprint="test:4",
            severity="critical"
        )
        
        by_channel = CriticalAlertEvent.count_by_channel_for_month(now.year, now.month)
        
        assert "email" in by_channel
        assert by_channel["email"] == 1
        assert "webhook" in by_channel
        assert by_channel["webhook"] == 1
        assert "both" in by_channel
        assert by_channel["both"] == 2
    
    def test_count_critical_alerts_for_month_alias(self):
        """Test que count_critical_alerts_for_month est un alias de count_for_month"""
        now = timezone.now()
        
        # Créer un événement
        CriticalAlertEvent.create_from_alert(
            title="TEST ALERT",
            payload={"test": 1},
            channel="email",
            fingerprint="test:alias",
            severity="critical"
        )
        
        count1 = CriticalAlertEvent.count_for_month(now.year, now.month)
        count2 = CriticalAlertEvent.count_critical_alerts_for_month(now.year, now.month)
        
        assert count1 == count2
        assert count1 == 1


@pytest.mark.django_db
@pytest.mark.critical
class TestCriticalAlertEventDeduplication:
    """Tests pour vérifier que le dédoublonnage n'incrémente pas le compteur"""
    
    def test_deduplication_does_not_create_event(self):
        """
        Test que si send_critical_alert() est dédoublonné (retourne True sans envoyer),
        aucun événement n'est créé.
        
        Ce test vérifie indirectement que l'enregistrement se fait uniquement
        après dédoublonnage (dans send_critical_alert()).
        """
        from core.utils.alerts import send_critical_alert
        from django.core import mail
        from django.test import override_settings
        
        mail.outbox.clear()
        
        # Compter les événements avant
        initial_count = CriticalAlertEvent.objects.count()
        
        payload = {"test": "data"}
        
        # Premier appel (devrait créer un événement)
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            result1 = send_critical_alert(
                title="TEST ALERT",
                payload=payload,
                dedupe_key="test:dedup"
            )
            
            assert result1 is True
            assert len(mail.outbox) == 1
            
            # Vérifier qu'un événement a été créé
            count_after_first = CriticalAlertEvent.objects.count()
            assert count_after_first == initial_count + 1
        
        # Deuxième appel avec la même dedupe_key (devrait être dédoublonné)
        mail.outbox.clear()
        
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            result2 = send_critical_alert(
                title="TEST ALERT",
                payload=payload,
                dedupe_key="test:dedup"
            )
            
            assert result2 is True  # Considéré comme succès car déjà envoyé
            assert len(mail.outbox) == 0  # Pas d'email envoyé (dédoublonné)
            
            # Vérifier qu'aucun nouvel événement n'a été créé
            count_after_second = CriticalAlertEvent.objects.count()
            assert count_after_second == initial_count + 1  # Même nombre qu'après le premier appel
    
    def test_no_dedupe_key_creates_multiple_events(self):
        """Test que sans dedupe_key, chaque appel crée un événement"""
        from core.utils.alerts import send_critical_alert
        from django.core import mail
        from django.test import override_settings
        
        mail.outbox.clear()
        
        initial_count = CriticalAlertEvent.objects.count()
        
        payload = {"test": "data"}
        
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            # Premier appel (sans dedupe_key)
            result1 = send_critical_alert(
                title="TEST ALERT",
                payload=payload
            )
            
            assert result1 is True
            assert len(mail.outbox) == 1
            
            count_after_first = CriticalAlertEvent.objects.count()
            assert count_after_first == initial_count + 1
            
            # Deuxième appel (sans dedupe_key, donc pas dédoublonné)
            result2 = send_critical_alert(
                title="TEST ALERT",
                payload=payload
            )
            
            assert result2 is True
            assert len(mail.outbox) == 2  # Deux emails envoyés
            
            count_after_second = CriticalAlertEvent.objects.count()
            assert count_after_second == initial_count + 2  # Deux événements créés

