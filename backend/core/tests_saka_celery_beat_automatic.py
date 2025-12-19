"""
Test P0 CRITIQUE : Compostage automatique après inactivité (Celery Beat)

PHILOSOPHIE EGOEJO :
Le compostage DOIT être automatique. Aucune intervention manuelle ne doit être nécessaire.
Le cycle SAKA (Récolte → Usage → Compost → Silo → Redistribution) est NON NÉGOCIABLE.

PROTECTION : Empêche l'accumulation SAKA en validant le compostage automatique.
VIOLATION EMPÊCHÉE : Accumulation infinie SAKA, cycle SAKA rompu.
"""
import pytest
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from core.models.saka import SakaWallet, SakaSilo, SakaCompostLog
from core.tasks import saka_run_compost_cycle

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    SAKA_COMPOST_ENABLED=True,
    SAKA_COMPOST_INACTIVITY_DAYS=90,
    SAKA_COMPOST_RATE=0.1,
    SAKA_COMPOST_MIN_BALANCE=50,
    SAKA_COMPOST_MIN_AMOUNT=10,
    CELERY_TASK_ALWAYS_EAGER=True,
)
@pytest.mark.django_db
class TestSakaCompostAutomatic:
    """
    Tests pour le compostage automatique via Celery Beat.
    
    Ces tests vérifient que le compostage s'applique automatiquement
    sans intervention manuelle, respectant le cycle SAKA obligatoire.
    """
    
    def test_compostage_automatique_apres_exactement_90_jours(self):
        """
        Test P0 : Compostage s'applique après exactement 90 jours.
        
        PHILOSOPHIE : Le compostage est automatique, pas manuel.
        Le cycle SAKA est NON NÉGOCIABLE.
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 200,
                'total_harvested': 200,
                'last_activity_date': timezone.now() - timedelta(days=90),  # Exactement 90 jours
            }
        )
        wallet.balance = 200
        wallet.last_activity_date = timezone.now() - timedelta(days=90)
        wallet.save()
        
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        initial_silo_balance = silo.total_balance
        initial_balance = wallet.balance
        
        # Exécuter la tâche Celery (simulation Celery Beat)
        result = saka_run_compost_cycle()
        
        # VÉRIFICATIONS
        wallet.refresh_from_db()
        assert wallet.balance < initial_balance, (
            "VIOLATION CONSTITUTION EGOEJO : Wallet doit être composté après 90 jours d'inactivité. "
            f"Balance initiale: {initial_balance}, Balance après: {wallet.balance}"
        )
        
        assert wallet.total_composted > 0, (
            "VIOLATION CONSTITUTION EGOEJO : total_composted doit être > 0 après compostage. "
            f"total_composted: {wallet.total_composted}"
        )
        
        silo.refresh_from_db()
        assert silo.total_balance > initial_silo_balance, (
            "VIOLATION CONSTITUTION EGOEJO : Silo doit être alimenté après compostage. "
            f"Balance Silo initiale: {initial_silo_balance}, Balance Silo après: {silo.total_balance}"
        )
        
        # Vérifier qu'un log de compostage a été créé
        compost_logs = SakaCompostLog.objects.filter(wallet=wallet)
        assert compost_logs.exists(), (
            "VIOLATION CONSTITUTION EGOEJO : Un log de compostage doit être créé. "
            "La traçabilité du cycle SAKA est obligatoire."
        )
    
    def test_compostage_ne_sapplique_pas_avant_90_jours(self):
        """
        Test P0 : Compostage ne s'applique pas avant 90 jours.
        
        PHILOSOPHIE : Le compostage respecte le seuil d'inactivité.
        Seul le SAKA inactif depuis 90+ jours est composté.
        """
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 200,
                'total_harvested': 200,
                'last_activity_date': timezone.now() - timedelta(days=89),  # 89 jours (pas éligible)
            }
        )
        wallet.balance = 200
        wallet.last_activity_date = timezone.now() - timedelta(days=89)
        wallet.save()
        
        initial_balance = wallet.balance
        initial_composted = wallet.total_composted
        
        # Exécuter la tâche Celery
        result = saka_run_compost_cycle()
        
        # VÉRIFICATIONS
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance, (
            "VIOLATION CONSTITUTION EGOEJO : Wallet ne doit PAS être composté avant 90 jours. "
            f"Balance initiale: {initial_balance}, Balance après: {wallet.balance}"
        )
        
        assert wallet.total_composted == initial_composted, (
            "VIOLATION CONSTITUTION EGOEJO : total_composted doit rester à 0 avant 90 jours. "
            f"total_composted: {wallet.total_composted}"
        )
    
    def test_compostage_progressif_10_pourcent_par_cycle(self):
        """
        Test P0 : Compostage progressif (10% par cycle).
        
        PHILOSOPHIE : Le compostage progressif empêche l'accumulation infinie.
        Même avec un très gros solde, le compostage progressif réduit le solde.
        """
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 1000,
                'total_harvested': 1000,
                'last_activity_date': timezone.now() - timedelta(days=120),
            }
        )
        wallet.balance = 1000
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        initial_balance = wallet.balance
        
        # Exécuter la tâche Celery
        result = saka_run_compost_cycle()
        
        # VÉRIFICATIONS
        wallet.refresh_from_db()
        expected_composted = int(initial_balance * 0.1)  # 10% = 100 SAKA
        expected_balance = initial_balance - expected_composted
        
        assert wallet.balance == expected_balance, (
            "VIOLATION CONSTITUTION EGOEJO : Compostage doit être 10% du solde. "
            f"Balance initiale: {initial_balance}, Balance attendue: {expected_balance}, "
            f"Balance obtenue: {wallet.balance}"
        )
        
        assert wallet.total_composted == expected_composted, (
            "VIOLATION CONSTITUTION EGOEJO : total_composted doit être 10% du solde. "
            f"Attendu: {expected_composted}, Obtenu: {wallet.total_composted}"
        )
        
        # Vérifier que le Silo a été alimenté
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        silo.refresh_from_db()
        assert silo.total_balance >= expected_composted, (
            "VIOLATION CONSTITUTION EGOEJO : Silo doit être alimenté du montant composté. "
            f"Montant composté: {expected_composted}, Balance Silo: {silo.total_balance}"
        )
    
    def test_compostage_automatique_plusieurs_cycles(self):
        """
        Test P0 : Compostage automatique après plusieurs cycles.
        
        PHILOSOPHIE : Le compostage progressif empêche l'accumulation infinie.
        Après plusieurs cycles, le solde diminue significativement.
        """
        user = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 5000,
                'total_harvested': 5000,
                'last_activity_date': timezone.now() - timedelta(days=120),
            }
        )
        wallet.balance = 5000
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        initial_balance = wallet.balance
        
        # Exécuter plusieurs cycles de compostage
        for cycle in range(3):
            # Forcer last_activity_date à 120 jours pour chaque cycle
            wallet.last_activity_date = timezone.now() - timedelta(days=120)
            wallet.save()
            
            result = saka_run_compost_cycle()
            wallet.refresh_from_db()
        
        # VÉRIFICATIONS
        # Après 3 cycles de 10%, le solde doit être significativement réduit
        # Cycle 1: 5000 - 500 = 4500
        # Cycle 2: 4500 - 450 = 4050
        # Cycle 3: 4050 - 405 = 3645
        expected_balance_after_3_cycles = int(5000 * (0.9 ** 3))
        
        assert wallet.balance < initial_balance * 0.8, (
            "VIOLATION CONSTITUTION EGOEJO : Après plusieurs cycles, le solde doit diminuer significativement. "
            f"Balance initiale: {initial_balance}, Balance après 3 cycles: {wallet.balance}"
        )
        
        # Vérifier que le compostage progressif empêche l'accumulation infinie
        reduction_percent = ((initial_balance - wallet.balance) / initial_balance) * 100
        assert reduction_percent > 20, (
            "VIOLATION CONSTITUTION EGOEJO : Le compostage progressif doit réduire le solde de plus de 20% "
            f"après 3 cycles. Réduction: {reduction_percent}%"
        )

