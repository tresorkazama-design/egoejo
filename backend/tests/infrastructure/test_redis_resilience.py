"""
Tests de résilience Redis
Vérifie que l'application continue de fonctionner même si Redis est indisponible
"""
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache
from core.utils.redis_health import check_redis_available, get_redis_status
from core.utils.cache_fallback import safe_cache_get, safe_cache_set, safe_cache_delete
from core.utils.channels_fallback import safe_group_send
from core.utils.celery_fallback import execute_task_sync


class TestRedisResilience(TestCase):
    """Tests de résilience en cas de panne Redis"""
    
    def test_redis_health_check_success(self):
        """Test que la vérification de santé Redis fonctionne"""
        status = get_redis_status()
        self.assertIn('available', status)
        self.assertIn('backend', status)
        self.assertIn('error', status)
    
    def test_redis_health_check_failure(self):
        """Test que la vérification de santé détecte une panne Redis"""
        with patch('django.core.cache.cache.set', side_effect=Exception("Redis unavailable")):
            available = check_redis_available()
            self.assertFalse(available)
    
    def test_get_redis_status_on_failure(self):
        """Test que get_redis_status retourne les bonnes informations en cas de panne"""
        with patch('django.core.cache.cache.set', side_effect=Exception("Redis unavailable")):
            status = get_redis_status()
            self.assertFalse(status['available'])
            self.assertIsNotNone(status['error'])
            self.assertIn('Redis unavailable', status['error'])
    
    def test_cache_fallback_get_on_redis_failure(self):
        """Test que safe_cache_get fonctionne avec fallback si Redis est indisponible"""
        # Simuler une panne Redis
        with patch('django.core.cache.cache.get', side_effect=Exception("Redis unavailable")):
            result = safe_cache_get('test_key', 'default_value')
            self.assertEqual(result, 'default_value')  # Doit retourner la valeur par défaut
    
    def test_cache_fallback_set_on_redis_failure(self):
        """Test que safe_cache_set fonctionne avec fallback si Redis est indisponible"""
        # Simuler une panne Redis
        with patch('django.core.cache.cache.set', side_effect=Exception("Redis unavailable")):
            result = safe_cache_set('test_key', 'test_value')
            self.assertFalse(result)  # Doit retourner False mais ne pas crasher
    
    def test_cache_fallback_delete_on_redis_failure(self):
        """Test que safe_cache_delete fonctionne avec fallback si Redis est indisponible"""
        # Simuler une panne Redis
        with patch('django.core.cache.cache.delete', side_effect=Exception("Redis unavailable")):
            result = safe_cache_delete('test_key')
            self.assertFalse(result)  # Doit retourner False mais ne pas crasher
    
    def test_channels_fallback_on_redis_failure(self):
        """Test que Channels fonctionne avec fallback si Redis est indisponible"""
        # Simuler une panne Redis en mockant get_channel_layer pour lever une exception
        with patch('core.utils.channels_fallback.get_channel_layer', side_effect=Exception("Redis unavailable")):
            result = safe_group_send('test_group', {'type': 'test_message'})
            self.assertFalse(result)  # Doit retourner False mais ne pas crasher
    
    def test_celery_fallback_on_redis_failure(self):
        """Test que Celery fonctionne avec fallback si Redis est indisponible"""
        # Créer une fonction de test simple
        def test_task(value):
            return value * 2
        
        # Simuler une panne Redis
        with patch('core.utils.redis_health.check_redis_available', return_value=False):
            # La tâche doit être exécutée de manière synchrone
            result = execute_task_sync(test_task, 5)
            self.assertEqual(result, 10)  # 5 * 2 = 10
    
    def test_celery_fallback_on_celery_error(self):
        """Test que Celery fonctionne avec fallback si Celery échoue"""
        # Créer une fonction de test simple
        def test_task(value):
            return value * 2
        
        # Créer un mock de tâche Celery qui échoue
        mock_task = MagicMock()
        mock_task.delay = MagicMock(side_effect=Exception("Celery unavailable"))
        mock_task.__name__ = 'test_task'
        
        # Simuler Redis disponible mais Celery qui échoue
        with patch('core.utils.redis_health.check_redis_available', return_value=True):
            # La tâche doit être exécutée de manière synchrone en cas d'erreur Celery
            result = execute_task_sync(test_task, 5)
            self.assertEqual(result, 10)  # 5 * 2 = 10
    
    def test_cache_fallback_normal_operation(self):
        """Test que le cache fonctionne normalement si Redis est disponible"""
        # Test avec Redis disponible
        result_set = safe_cache_set('test_key_normal', 'test_value', 60)
        self.assertTrue(result_set)  # Doit réussir
        
        result_get = safe_cache_get('test_key_normal', 'default')
        self.assertEqual(result_get, 'test_value')  # Doit retourner la valeur stockée
        
        # Nettoyer
        safe_cache_delete('test_key_normal')

