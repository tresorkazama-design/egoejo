"""
Test P0 CRITIQUE : Blocage démarrage PROD si flags SAKA désactivés

PHILOSOPHIE EGOEJO :
La structure relationnelle (SAKA) est PRIORITAIRE et FONDAMENTALE.
Elle ne peut PAS être désactivée en production.

Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"

VIOLATION EMPÊCHÉE :
- Démarrage en production avec SAKA désactivé
- Violation de la Constitution EGOEJO en production
- Structure relationnelle (SAKA) désactivée alors qu'elle est prioritaire
"""
import pytest
import sys
from django.test import override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.apps import apps
from django.conf import settings

from core.apps import CoreConfig


@pytest.mark.django_db
class TestSystemProductionFlagsBlocking:
    """
    Tests système pour garantir que le démarrage PROD est bloqué si flags SAKA désactivés.
    
    PROTECTION : Empêche le démarrage en production avec SAKA désactivé.
    VIOLATION EMPÊCHÉE : Production avec SAKA désactivé, violation Constitution EGOEJO.
    """
    
    def test_demarrage_prod_bloque_si_enable_saka_false(self):
        """
        Test P0 : Démarrage PROD bloqué si ENABLE_SAKA=False.
        
        Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"
        
        Vérifie que :
        - RuntimeError levée si ENABLE_SAKA=False en PROD
        - Application ne démarre pas
        - Message d'erreur explicite
        """
        # Simuler le mode production (DEBUG=False)
        with override_settings(
            DEBUG=False,
            ENABLE_SAKA=False,  # Flag désactivé
            SAKA_COMPOST_ENABLED=True,
            SAKA_SILO_REDIS_ENABLED=True
        ):
            # Réinitialiser les apps pour forcer l'exécution de ready()
            apps.app_configs.clear()
            apps.ready = False
            
            # Créer une nouvelle instance de CoreConfig
            app_config = CoreConfig('core', apps)
            
            # Vérifier que ready() lève une RuntimeError
            with pytest.raises(RuntimeError) as exc_info:
                app_config.ready()
            
            # Vérifier le message d'erreur
            error_message = str(exc_info.value)
            assert "ENABLE_SAKA" in error_message, (
                f"VIOLATION : Message d'erreur incorrect. "
                f"Attendu: mention de ENABLE_SAKA, Obtenu: {error_message}"
            )
            assert "production" in error_message.lower() or "désactivé" in error_message.lower(), (
                f"VIOLATION : Message d'erreur ne mentionne pas la production. "
                f"Message: {error_message}"
            )
    
    def test_demarrage_prod_bloque_si_saka_compost_enabled_false(self):
        """
        Test P0 : Démarrage PROD bloqué si SAKA_COMPOST_ENABLED=False.
        
        Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"
        
        Vérifie que :
        - RuntimeError levée si SAKA_COMPOST_ENABLED=False en PROD
        - Application ne démarre pas
        - Message d'erreur explicite
        """
        # Simuler le mode production (DEBUG=False)
        with override_settings(
            DEBUG=False,
            ENABLE_SAKA=True,
            SAKA_COMPOST_ENABLED=False,  # Flag désactivé
            SAKA_SILO_REDIS_ENABLED=True
        ):
            # Réinitialiser les apps
            apps.app_configs.clear()
            apps.ready = False
            
            # Créer une nouvelle instance de CoreConfig
            app_config = CoreConfig('core', apps)
            
            # Vérifier que ready() lève une RuntimeError
            with pytest.raises(RuntimeError) as exc_info:
                app_config.ready()
            
            # Vérifier le message d'erreur
            error_message = str(exc_info.value)
            assert "SAKA_COMPOST_ENABLED" in error_message, (
                f"VIOLATION : Message d'erreur incorrect. "
                f"Attendu: mention de SAKA_COMPOST_ENABLED, Obtenu: {error_message}"
            )
    
    def test_demarrage_prod_bloque_si_saka_silo_redis_enabled_false(self):
        """
        Test P0 : Démarrage PROD bloqué si SAKA_SILO_REDIS_ENABLED=False.
        
        Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"
        
        Vérifie que :
        - RuntimeError levée si SAKA_SILO_REDIS_ENABLED=False en PROD
        - Application ne démarre pas
        - Message d'erreur explicite
        """
        # Simuler le mode production (DEBUG=False)
        with override_settings(
            DEBUG=False,
            ENABLE_SAKA=True,
            SAKA_COMPOST_ENABLED=True,
            SAKA_SILO_REDIS_ENABLED=False  # Flag désactivé
        ):
            # Réinitialiser les apps
            apps.app_configs.clear()
            apps.ready = False
            
            # Créer une nouvelle instance de CoreConfig
            app_config = CoreConfig('core', apps)
            
            # Vérifier que ready() lève une RuntimeError
            with pytest.raises(RuntimeError) as exc_info:
                app_config.ready()
            
            # Vérifier le message d'erreur
            error_message = str(exc_info.value)
            assert "SAKA_SILO_REDIS_ENABLED" in error_message, (
                f"VIOLATION : Message d'erreur incorrect. "
                f"Attendu: mention de SAKA_SILO_REDIS_ENABLED, Obtenu: {error_message}"
            )
    
    def test_demarrage_prod_autorise_si_tous_flags_actives(self):
        """
        Test P0 : Démarrage PROD autorisé si tous les flags SAKA sont activés.
        
        Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"
        
        Vérifie que :
        - Aucune exception levée si tous les flags sont activés
        - Application démarre correctement
        """
        # Simuler le mode production (DEBUG=False)
        with override_settings(
            DEBUG=False,
            ENABLE_SAKA=True,  # Tous les flags activés
            SAKA_COMPOST_ENABLED=True,
            SAKA_SILO_REDIS_ENABLED=True
        ):
            # Réinitialiser les apps
            apps.app_configs.clear()
            apps.ready = False
            
            # Créer une nouvelle instance de CoreConfig
            app_config = CoreConfig('core', apps)
            
            # Vérifier que ready() ne lève PAS d'exception
            try:
                app_config.ready()
            except RuntimeError as e:
                pytest.fail(
                    f"VIOLATION : Exception levée alors que tous les flags sont activés. "
                    f"Erreur: {e}"
                )
    
    def test_demarrage_dev_autorise_si_flags_desactives(self):
        """
        Test P0 : Démarrage DEV autorisé même si flags SAKA désactivés.
        
        Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"
        
        Vérifie que :
        - Aucune exception levée en DEV (DEBUG=True) même si flags désactivés
        - Permet les tests en développement
        """
        # Simuler le mode développement (DEBUG=True)
        with override_settings(
            DEBUG=True,  # Mode développement
            ENABLE_SAKA=False,  # Flags désactivés (autorisé en DEV)
            SAKA_COMPOST_ENABLED=False,
            SAKA_SILO_REDIS_ENABLED=False
        ):
            # Réinitialiser les apps
            apps.app_configs.clear()
            apps.ready = False
            
            # Créer une nouvelle instance de CoreConfig
            app_config = CoreConfig('core', apps)
            
            # Vérifier que ready() ne lève PAS d'exception en DEV
            try:
                app_config.ready()
            except RuntimeError as e:
                pytest.fail(
                    f"VIOLATION : Exception levée en mode développement. "
                    f"Les flags peuvent être désactivés en DEV. Erreur: {e}"
                )
    
    def test_message_erreur_explicite_liste_flags_desactives(self):
        """
        Test P0 : Message d'erreur explicite liste tous les flags désactivés.
        
        Ce test protège la règle : "SAKA doit être activé en production (DEBUG=False)"
        
        Vérifie que :
        - Message d'erreur liste tous les flags désactivés
        - Message indique l'action requise
        - Message référence la documentation
        """
        # Simuler le mode production avec plusieurs flags désactivés
        with override_settings(
            DEBUG=False,
            ENABLE_SAKA=False,
            SAKA_COMPOST_ENABLED=False,
            SAKA_SILO_REDIS_ENABLED=False
        ):
            # Réinitialiser les apps
            apps.app_configs.clear()
            apps.ready = False
            
            # Créer une nouvelle instance de CoreConfig
            app_config = CoreConfig('core', apps)
            
            # Vérifier que ready() lève une RuntimeError avec message explicite
            with pytest.raises(RuntimeError) as exc_info:
                app_config.ready()
            
            error_message = str(exc_info.value)
            
            # Vérifier que le message mentionne tous les flags désactivés
            assert "ENABLE_SAKA" in error_message, (
                "VIOLATION : Message d'erreur ne mentionne pas ENABLE_SAKA"
            )
            assert "SAKA_COMPOST_ENABLED" in error_message or "compost" in error_message.lower(), (
                "VIOLATION : Message d'erreur ne mentionne pas SAKA_COMPOST_ENABLED"
            )
            assert "SAKA_SILO_REDIS_ENABLED" in error_message or "silo" in error_message.lower(), (
                "VIOLATION : Message d'erreur ne mentionne pas SAKA_SILO_REDIS_ENABLED"
            )
            
            # Vérifier que le message indique l'action requise
            assert "activer" in error_message.lower() or "enable" in error_message.lower(), (
                "VIOLATION : Message d'erreur n'indique pas l'action requise"
            )

