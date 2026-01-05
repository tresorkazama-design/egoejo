"""
EGOEJO Compliance Test : Anti-Accumulation

LOI EGOEJO :
"L'accumulation passive de SAKA est interdite. Le SAKA doit circuler."

Ce test vérifie que :
- Le compostage est obligatoire
- La redistribution est obligatoire
- Aucune accumulation passive n'est possible

Violation du Manifeste EGOEJO si :
- Le compostage peut être désactivé
- La redistribution peut être désactivée
- L'accumulation passive est possible
"""
import pytest
from django.test import override_settings
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.models.saka import SakaWallet
from core.services.saka import harvest_saka, SakaReason
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.egoejo_compliance
class TestAntiAccumulation:
    """
    Tests de conformité : Anti-Accumulation
    
    RÈGLE ABSOLUE : L'accumulation passive de SAKA est interdite.
    """
    
    def test_compostage_obligatoire_en_production(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le compostage peut être désactivé en production.
        
        Test : Vérifier que SAKA_COMPOST_ENABLED=True en production.
        """
        with override_settings(DEBUG=False):
            compost_enabled = getattr(settings, 'SAKA_COMPOST_ENABLED', False)
            saka_enabled = getattr(settings, 'ENABLE_SAKA', False)
            
            if saka_enabled:
                assert compost_enabled == True, (
                    "VIOLATION DU MANIFESTE EGOEJO : "
                    "SAKA_COMPOST_ENABLED doit être True en production si SAKA est activé. "
                    "Le compostage est obligatoire pour respecter l'anti-accumulation."
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
    
    @pytest.mark.django_db
    def test_solde_saka_se_degrade_si_inactif(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un solde SAKA ne se dégrade jamais, même après inactivité prolongée.
        
        Test : Vérifier que le compostage réduit le solde après inactivité.
        """
        from core.services.saka import run_saka_compost_cycle
        
        # Créer un utilisateur avec un wallet SAKA
        user = User.objects.create_user(
            username=f'test_inactif_{timezone.now().timestamp()}',
            email=f'test_inactif_{timezone.now().timestamp()}@example.com',
            password='password'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={'balance': 1000}
        )
        
        # Initialiser le wallet avec un solde élevé
        wallet.balance = 1000
        wallet.last_activity_date = timezone.now() - timedelta(days=100)  # Inactif depuis 100 jours
        wallet.save()
        
        initial_balance = wallet.balance
        
        # Exécuter le cycle de compostage
        result = run_saka_compost_cycle(dry_run=False, source="test")
        
        # Recharger le wallet
        wallet.refresh_from_db()
        
        # Vérifier que le solde a diminué (compostage effectif)
        if getattr(settings, 'SAKA_COMPOST_ENABLED', False):
            assert wallet.balance < initial_balance, (
                f"VIOLATION DU MANIFESTE EGOEJO : "
                f"Le solde SAKA n'a pas diminué après compostage (initial: {initial_balance}, actuel: {wallet.balance}). "
                f"L'anti-accumulation exige que le SAKA inactif soit composté."
            )
    
    @pytest.mark.django_db
    def test_limites_quotidiennes_respectees(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Les limites quotidiennes de récolte ne sont pas respectées.
        
        Test : Vérifier que les limites quotidiennes empêchent l'accumulation excessive.
        """
        from core.services.saka import SAKA_DAILY_LIMITS, SAKA_BASE_REWARDS
        
        user = User.objects.create_user(
            username=f'test_limites_{timezone.now().timestamp()}',
            email=f'test_limites_{timezone.now().timestamp()}@example.com',
            password='password'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(user=user)
        initial_harvested = wallet.total_harvested
        
        # Tenter de récolter au-delà de la limite quotidienne
        reason = SakaReason.CONTENT_READ
        daily_limit = SAKA_DAILY_LIMITS.get(reason, 0)
        base_reward = SAKA_BASE_REWARDS.get(reason, 0)
        max_daily = daily_limit * base_reward
        
        # Récolter jusqu'à la limite
        for i in range(daily_limit + 1):  # +1 pour dépasser la limite
            harvest_saka(user, reason)
        
        wallet.refresh_from_db()
        
        # Vérifier que la limite est respectée
        harvested_today = wallet.total_harvested - initial_harvested
        
        assert harvested_today <= max_daily, (
            f"VIOLATION DU MANIFESTE EGOEJO : "
            f"Les limites quotidiennes ne sont pas respectées. "
            f"Récolté aujourd'hui: {harvested_today}, Maximum autorisé: {max_daily}. "
            f"L'anti-accumulation exige des limites quotidiennes strictes."
        )

