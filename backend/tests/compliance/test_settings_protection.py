"""
EGOEJO Compliance Test : Protection des Settings SAKA

LOI EGOEJO :
"Les settings SAKA critiques ne peuvent pas être désactivés ou modifiés arbitrairement."

Ce test vérifie que :
- Le compostage est obligatoire en production
- Le taux de compostage est > 0
- La redistribution est obligatoire si le Silo est actif
- Les paramètres sont dans des plages valides

Violation du Manifeste EGOEJO si :
- SAKA_COMPOST_ENABLED=False en production
- SAKA_COMPOST_RATE=0
- SAKA_SILO_REDIS_RATE=0 si redistribution activée
"""
import pytest
from django.test import override_settings
from django.conf import settings


@pytest.mark.egoejo_compliance
class TestSettingsProtection:
    """
    Tests de conformité : Protection des Settings SAKA
    
    RÈGLE ABSOLUE : Les settings SAKA critiques ne peuvent pas être désactivés.
    """
    
    def test_compostage_obligatoire_en_production(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le compostage peut être désactivé en production.
        
        Test : Vérifier que SAKA_COMPOST_ENABLED=True en production.
        """
        # Simuler production (DEBUG=False)
        with override_settings(DEBUG=False):
            compost_enabled = getattr(settings, 'SAKA_COMPOST_ENABLED', False)
            
            # Si SAKA est activé, le compostage DOIT être activé en production
            saka_enabled = getattr(settings, 'ENABLE_SAKA', False)
            if saka_enabled:
                assert compost_enabled == True, (
                    "VIOLATION DU MANIFESTE EGOEJO : "
                    "SAKA_COMPOST_ENABLED doit être True en production si SAKA est activé. "
                    "Le compostage est obligatoire pour respecter la philosophie anti-accumulation."
                )
    
    def test_compost_rate_doit_etre_positif(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le taux de compostage peut être 0 ou négatif.
        
        Test : Vérifier que SAKA_COMPOST_RATE > 0.
        """
        rate = getattr(settings, 'SAKA_COMPOST_RATE', 0.1)
        
        assert rate > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"SAKA_COMPOST_RATE doit être > 0 (actuel: {rate}). "
            f"Un taux de 0 empêche le compostage, violant l'anti-accumulation."
        )
        
        assert rate <= 1.0, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"SAKA_COMPOST_RATE doit être <= 1.0 (actuel: {rate}). "
            f"Un taux > 1.0 est invalide (plus de 100% composté)."
        )
    
    def test_redistribution_obligatoire_si_silo_actif(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        La redistribution peut être désactivée alors que le Silo est actif.
        
        Test : Vérifier que si SAKA_SILO_REDIS_ENABLED=True, alors SAKA_SILO_REDIS_RATE > 0.
        """
        silo_enabled = getattr(settings, 'SAKA_SILO_REDIS_ENABLED', False)
        
        if silo_enabled:
            rate = getattr(settings, 'SAKA_SILO_REDIS_RATE', 0.05)
            
            assert rate > 0, (
                f"VIOLATION DU MANIFESTE EGOEJO : "
                f"Si SAKA_SILO_REDIS_ENABLED=True, SAKA_SILO_REDIS_RATE doit être > 0 (actuel: {rate}). "
                f"Un taux de 0 empêche la redistribution, violant la circulation obligatoire."
            )
            
            assert rate <= 1.0, (
                f"VIOLATION DU MANIFESTE EGOEJO : "
                f"SAKA_SILO_REDIS_RATE doit être <= 1.0 (actuel: {rate}). "
                f"Un taux > 1.0 est invalide (plus de 100% redistribué)."
            )
    
    def test_inactivity_days_doit_etre_raisonnable(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Les jours d'inactivité sont trop élevés (évite le compostage).
        
        Test : Vérifier que SAKA_COMPOST_INACTIVITY_DAYS < seuil max (ex: 365 jours).
        """
        inactivity_days = getattr(settings, 'SAKA_COMPOST_INACTIVITY_DAYS', 90)
        MAX_INACTIVITY_DAYS = 365  # 1 an maximum
        
        assert inactivity_days > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"SAKA_COMPOST_INACTIVITY_DAYS doit être > 0 (actuel: {inactivity_days})."
        )
        
        assert inactivity_days <= MAX_INACTIVITY_DAYS, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"SAKA_COMPOST_INACTIVITY_DAYS doit être <= {MAX_INACTIVITY_DAYS} jours (actuel: {inactivity_days}). "
            f"Une valeur trop élevée évite le compostage, violant l'anti-accumulation."
        )
    
    def test_min_balance_doit_etre_raisonnable(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le solde minimum pour compostage est trop élevé (évite le compostage).
        
        Test : Vérifier que SAKA_COMPOST_MIN_BALANCE < seuil max (ex: 10000 SAKA).
        """
        min_balance = getattr(settings, 'SAKA_COMPOST_MIN_BALANCE', 50)
        MAX_MIN_BALANCE = 10000  # Seuil maximum raisonnable
        
        assert min_balance >= 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"SAKA_COMPOST_MIN_BALANCE doit être >= 0 (actuel: {min_balance})."
        )
        
        assert min_balance <= MAX_MIN_BALANCE, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"SAKA_COMPOST_MIN_BALANCE doit être <= {MAX_MIN_BALANCE} (actuel: {min_balance}). "
            f"Une valeur trop élevée évite le compostage pour la plupart des wallets."
        )

