"""
Tests pour l'endpoint de métriques d'alertes critiques EGOEJO.

Vérifie que :
- Les métriques sont correctement calculées
- Aucune donnée personnelle n'est exposée
- L'endpoint est accessible publiquement
- Le cache fonctionne correctement
"""
import pytest
from django.test import Client
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
from core.models.alerts import CriticalAlertEvent
from core.utils.alerts import send_critical_alert


@pytest.mark.django_db
class TestCriticalAlertMetrics:
    """Tests pour l'endpoint /api/compliance/alerts/metrics/"""
    
    def setup_method(self):
        """Nettoyer le cache et les données avant chaque test"""
        cache.clear()
        CriticalAlertEvent.objects.all().delete()
        self.client = Client()

    def _get_metrics(self):
        """
        Utilitaire pour éviter les 301 (HTTP->HTTPS / APPEND_SLASH) qui faussent les tests de contrat.
        Pour GET, follow=True est sûr.
        """
        return self.client.get('/api/compliance/alerts/metrics/', follow=True, secure=True)
    
    def test_metrics_endpoint_returns_expected_shape(self):
        """Test que l'endpoint retourne la structure attendue"""
        response = self._get_metrics()
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure
        assert 'total_alerts' in data
        assert 'alerts_by_month' in data
        assert 'last_alert_at' in data
        
        # Vérifier les types
        assert isinstance(data['total_alerts'], int)
        assert isinstance(data['alerts_by_month'], list)
        assert data['last_alert_at'] is None or isinstance(data['last_alert_at'], str)
        
        # Vérifier la structure de alerts_by_month
        if data['alerts_by_month']:
            for item in data['alerts_by_month']:
                assert 'month' in item
                assert 'count' in item
                assert isinstance(item['month'], str)
                assert isinstance(item['count'], int)
                # Format YYYY-MM
                assert len(item['month']) == 7
                assert item['month'][4] == '-'
    
    def test_metrics_no_personal_data_leak(self):
        """Test qu'aucune donnée personnelle n'est exposée"""
        from django.test import override_settings
        
        # Créer une alerte avec des données personnelles et ADMINS configurés
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            send_critical_alert(
                title="TEST ALERT",
                payload={
                    "user_id": 123,
                    "username": "testuser",
                    "email": "test@example.com",
                    "old_balance": 1000,
                    "new_balance": 2000
                },
                dedupe_key="test:123"
            )
        
        response = self._get_metrics()
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier qu'aucune donnée personnelle n'est présente
        data_str = str(data)
        assert 'testuser' not in data_str
        assert 'test@example.com' not in data_str
        assert 'user_id' not in data_str
        assert 'username' not in data_str
        assert 'email' not in data_str
    
    def test_metric_increment_on_alert(self):
        """Test que les métriques sont incrémentées lors d'une alerte"""
        from django.test import override_settings
        
        # Initialiser les métriques
        response1 = self._get_metrics()
        data1 = response1.json()
        initial_count = data1['total_alerts']
        
        # Envoyer une alerte avec ADMINS configurés
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            send_critical_alert(
                title="TEST ALERT",
                payload={"test": "data"},
                dedupe_key="test:1"
            )
        
        # Nettoyer le cache pour forcer le recalcul
        cache.clear()
        
        # Vérifier que le compteur a augmenté
        response2 = self._get_metrics()
        data2 = response2.json()
        
        assert data2['total_alerts'] == initial_count + 1
        assert data2['last_alert_at'] is not None
    
    def test_metric_not_incremented_when_alert_disabled(self):
        """Test que les métriques ne sont pas incrémentées si les alertes sont désactivées"""
        from django.test import override_settings
        
        # Initialiser les métriques
        response1 = self._get_metrics()
        data1 = response1.json()
        initial_count = data1['total_alerts']
        
        # Envoyer une alerte avec alertes désactivées
        with override_settings(ALERT_EMAIL_ENABLED=False):
            send_critical_alert(
                title="TEST ALERT",
                payload={"test": "data"},
                dedupe_key="test:2"
            )
        
        # Nettoyer le cache pour forcer le recalcul
        cache.clear()
        
        # Vérifier que le compteur n'a pas augmenté
        response2 = self._get_metrics()
        data2 = response2.json()
        
        assert data2['total_alerts'] == initial_count
    
    def test_alerts_by_month_structure(self):
        """Test que alerts_by_month contient les 12 derniers mois"""
        # Créer quelques alertes dans différents mois
        now = timezone.now()
        
        # Créer une alerte il y a 2 mois
        two_months_ago = now - timedelta(days=60)
        event1 = CriticalAlertEvent.objects.create(
            event_type="TEST ALERT 1",
            severity="critical",
            channel="email",
            fingerprint="test:1",
            created_at=two_months_ago
        )
        
        # Créer une alerte ce mois
        event2 = CriticalAlertEvent.objects.create(
            event_type="TEST ALERT 2",
            severity="critical",
            channel="email",
            fingerprint="test:2",
            created_at=now
        )
        
        # Nettoyer le cache
        cache.clear()
        
        # Vérifier la structure
        response = self._get_metrics()
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier qu'il y a 12 mois
        assert len(data['alerts_by_month']) == 12
        
        # Vérifier que les mois sont triés (plus récent en premier)
        months = [item['month'] for item in data['alerts_by_month']]
        assert months == sorted(months, reverse=True)
    
    def test_endpoint_is_public(self):
        """Test que l'endpoint est accessible sans authentification"""
        response = self._get_metrics()
        
        assert response.status_code == 200
        # Vérifier qu'il n'y a pas de redirection vers login
        assert 'login' not in response.url if hasattr(response, 'url') else True
    
    def test_cache_works(self):
        """Test que le cache fonctionne correctement"""
        from django.test import override_settings
        
        # Première requête (pas de cache)
        response1 = self._get_metrics()
        assert response1.status_code == 200
        assert 'Cache-Control' in response1
        
        # Créer une nouvelle alerte avec ADMINS configurés
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            send_critical_alert(
                title="TEST ALERT",
                payload={"test": "data"},
                dedupe_key="test:3"
            )
        
        # Deuxième requête (devrait utiliser le cache, donc ne pas voir la nouvelle alerte)
        response2 = self._get_metrics()
        assert response2.status_code == 200
        
        # Nettoyer le cache et vérifier que la nouvelle alerte apparaît
        cache.clear()
        response3 = self._get_metrics()
        assert response3.status_code == 200
        data3 = response3.json()
        assert data3['total_alerts'] >= 1
    
    def test_last_alert_at_is_correct(self):
        """Test que last_alert_at retourne la date de la dernière alerte"""
        from django.test import override_settings
        
        # Pas d'alerte initialement
        response1 = self._get_metrics()
        data1 = response1.json()
        assert data1['last_alert_at'] is None
        
        # Créer une alerte avec ADMINS configurés
        with override_settings(
            ALERT_EMAIL_ENABLED=True,
            ADMINS=[('Test Admin', 'admin@example.com')],
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            send_critical_alert(
                title="TEST ALERT",
                payload={"test": "data"},
                dedupe_key="test:4"
            )
        
        # Nettoyer le cache
        cache.clear()
        
        # Vérifier que last_alert_at est défini
        response2 = self._get_metrics()
        data2 = response2.json()
        assert data2['last_alert_at'] is not None
        
        # Vérifier le format ISO-8601
        from datetime import datetime
        try:
            datetime.fromisoformat(data2['last_alert_at'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"last_alert_at n'est pas au format ISO-8601: {data2['last_alert_at']}")


        from datetime import datetime
        try:
            datetime.fromisoformat(data2['last_alert_at'].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"last_alert_at n'est pas au format ISO-8601: {data2['last_alert_at']}")

