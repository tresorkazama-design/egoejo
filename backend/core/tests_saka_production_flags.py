"""
Tests pour la protection des feature flags SAKA en production

PHILOSOPHIE EGOEJO :
La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.
Elle ne peut pas être désactivée en production.

Ces tests vérifient que :
1. L'application refuse de démarrer si les flags SAKA sont désactivés en production
2. L'application démarre normalement si les flags sont activés en production
3. L'application démarre normalement en développement même si les flags sont désactivés
"""
import pytest
from django.test import override_settings
from django.apps import apps
from core.apps import CoreConfig


class TestSakaProductionFlags:
    """
    Tests de protection des feature flags SAKA en production
    """
    
    def test_application_refuse_demarrage_si_enable_saka_false_en_production(self):
        """
        Test que l'application refuse de démarrer si ENABLE_SAKA=False en production.
        
        PHILOSOPHIE : La structure relationnelle (SAKA) est PRIORITAIRE.
        Elle ne peut pas être désactivée en production.
        """
        with override_settings(
            DEBUG=False,  # Mode production
            ENABLE_SAKA=False,  # Flag désactivé
            SAKA_COMPOST_ENABLED=True,
            SAKA_SILO_REDIS_ENABLED=True,
        ):
            # Obtenir l'instance réelle de CoreConfig
            config = apps.get_app_config('core')
            
            # La vérification doit lever une exception
            with pytest.raises(RuntimeError) as exc_info:
                config.check_saka_flags_in_production()
            
            assert "ENABLE_SAKA" in str(exc_info.value)
            assert "production" in str(exc_info.value).lower()
    
    def test_application_refuse_demarrage_si_compost_disabled_en_production(self):
        """
        Test que l'application refuse de démarrer si SAKA_COMPOST_ENABLED=False en production.
        
        PHILOSOPHIE : Le compostage est essentiel pour l'anti-accumulation.
        Il ne peut pas être désactivé en production.
        """
        with override_settings(
            DEBUG=False,  # Mode production
            ENABLE_SAKA=True,
            SAKA_COMPOST_ENABLED=False,  # Flag désactivé
            SAKA_SILO_REDIS_ENABLED=True,
        ):
            config = apps.get_app_config('core')
            
            with pytest.raises(RuntimeError) as exc_info:
                config.check_saka_flags_in_production()
            
            assert "SAKA_COMPOST_ENABLED" in str(exc_info.value)
            assert "production" in str(exc_info.value).lower()
    
    def test_application_refuse_demarrage_si_redistribution_disabled_en_production(self):
        """
        Test que l'application refuse de démarrer si SAKA_SILO_REDIS_ENABLED=False en production.
        
        PHILOSOPHIE : La redistribution est essentielle pour le retour au commun.
        Elle ne peut pas être désactivée en production.
        """
        with override_settings(
            DEBUG=False,  # Mode production
            ENABLE_SAKA=True,
            SAKA_COMPOST_ENABLED=True,
            SAKA_SILO_REDIS_ENABLED=False,  # Flag désactivé
        ):
            config = apps.get_app_config('core')
            
            with pytest.raises(RuntimeError) as exc_info:
                config.check_saka_flags_in_production()
            
            assert "SAKA_SILO_REDIS_ENABLED" in str(exc_info.value)
            assert "production" in str(exc_info.value).lower()
    
    def test_application_refuse_demarrage_si_tous_flags_disabled_en_production(self):
        """
        Test que l'application refuse de démarrer si tous les flags SAKA sont désactivés en production.
        
        PHILOSOPHIE : Le protocole SAKA complet est requis en production.
        """
        with override_settings(
            DEBUG=False,  # Mode production
            ENABLE_SAKA=False,
            SAKA_COMPOST_ENABLED=False,
            SAKA_SILO_REDIS_ENABLED=False,
        ):
            config = apps.get_app_config('core')
            
            with pytest.raises(RuntimeError) as exc_info:
                config.check_saka_flags_in_production()
            
            error_message = str(exc_info.value)
            assert "ENABLE_SAKA" in error_message
            assert "SAKA_COMPOST_ENABLED" in error_message
            assert "SAKA_SILO_REDIS_ENABLED" in error_message
    
    def test_application_demarre_si_flags_actives_en_production(self):
        """
        Test que l'application démarre normalement si tous les flags SAKA sont activés en production.
        
        PHILOSOPHIE : Si les flags sont activés, l'application doit démarrer normalement.
        """
        with override_settings(
            DEBUG=False,  # Mode production
            ENABLE_SAKA=True,
            SAKA_COMPOST_ENABLED=True,
            SAKA_SILO_REDIS_ENABLED=True,
        ):
            config = apps.get_app_config('core')
            
            # Ne doit pas lever d'exception
            try:
                config.check_saka_flags_in_production()
            except RuntimeError:
                pytest.fail("L'application ne devrait pas lever d'exception si les flags sont activés")
    
    def test_application_demarre_en_dev_meme_si_flags_disabled(self):
        """
        Test que l'application démarre normalement en développement même si les flags SAKA sont désactivés.
        
        PHILOSOPHIE : En développement, les flags peuvent être désactivés pour les tests.
        """
        with override_settings(
            DEBUG=True,  # Mode développement
            ENABLE_SAKA=False,
            SAKA_COMPOST_ENABLED=False,
            SAKA_SILO_REDIS_ENABLED=False,
        ):
            config = apps.get_app_config('core')
            
            # Ne doit pas lever d'exception en mode développement
            try:
                config.check_saka_flags_in_production()
            except RuntimeError:
                pytest.fail("L'application ne devrait pas lever d'exception en mode développement")
    
    def test_message_erreur_explicite(self):
        """
        Test que le message d'erreur est explicite et contient les instructions nécessaires.
        
        PHILOSOPHIE : L'erreur doit être claire et guider vers la solution.
        """
        with override_settings(
            DEBUG=False,
            ENABLE_SAKA=False,
            SAKA_COMPOST_ENABLED=False,
            SAKA_SILO_REDIS_ENABLED=False,
        ):
            config = apps.get_app_config('core')
            
            with pytest.raises(RuntimeError) as exc_info:
                config.check_saka_flags_in_production()
            
            error_message = str(exc_info.value)
            
            # Vérifier que le message contient les informations nécessaires
            assert "ENABLE_SAKA" in error_message
            assert "SAKA_COMPOST_ENABLED" in error_message
            assert "SAKA_SILO_REDIS_ENABLED" in error_message
            assert "production" in error_message.lower()
            assert "structure relationnelle" in error_message.lower() or "SAKA" in error_message
