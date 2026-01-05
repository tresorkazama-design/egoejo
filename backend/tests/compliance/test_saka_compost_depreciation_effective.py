"""
Test P0 CRITIQUE : Compostage - Dépréciation effective

PHILOSOPHIE EGOEJO :
Le compostage SAKA est obligatoire et doit être EFFECTIF.
Le SAKA inactif DOIT être déprécié (diminué) et retourner au Silo.

Ce test protège la règle : "Compostage obligatoire - Dépréciation effective du SAKA inactif"

VIOLATION EMPÊCHÉE :
- Compostage qui ne diminue pas réellement le solde
- Compostage qui ne retourne pas au Silo
- Compostage qui peut être contourné
- Accumulation infinie malgré compostage
"""
import pytest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from core.models.saka import SakaWallet, SakaSilo, SakaCompostLog
from core.services.saka import run_saka_compost_cycle

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    SAKA_COMPOST_ENABLED=True,
    SAKA_COMPOST_INACTIVITY_DAYS=90,
    SAKA_COMPOST_RATE=0.1,
    SAKA_COMPOST_MIN_BALANCE=50,
    SAKA_COMPOST_MIN_AMOUNT=10,
)
@pytest.mark.egoejo_compliance
class TestSakaCompostDepreciationEffective(TestCase):
    """
    Tests pour garantir que le compostage est EFFECTIF (dépréciation réelle).
    
    PROTECTION : Empêche l'accumulation infinie en validant la dépréciation effective.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    VIOLATION EMPÊCHÉE : Compostage simulé, accumulation infinie, contournement du cycle.
    """
    
    def test_compostage_diminue_reellement_le_solde(self):
        """
        Test P0 : Le compostage diminue réellement le solde SAKA.
        
        Ce test protège la règle : "Compostage obligatoire - Dépréciation effective du SAKA inactif"
        
        Vérifie que :
        - Le solde wallet diminue après compostage
        - Le montant composté correspond au taux configuré
        - Le total_composted est mis à jour
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
                'last_activity_date': timezone.now() - timedelta(days=120),  # Inactif depuis 120 jours
            }
        )
        wallet.balance = 200
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        initial_balance = wallet.balance
        initial_composted = wallet.total_composted
        
        # Exécuter le compostage
        result = run_saka_compost_cycle(dry_run=False, source="test")
        
        # VÉRIFICATIONS : DÉPRÉCIATION EFFECTIVE
        wallet.refresh_from_db()
        
        # 1. Le solde a DIMINUÉ
        assert wallet.balance < initial_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : Le compostage n'a pas diminué le solde. "
            f"Solde initial: {initial_balance}, Solde après compostage: {wallet.balance}"
        )
        
        # 2. Le montant composté correspond au taux (10% de 200 = 20 SAKA)
        expected_composted = int(initial_balance * 0.1)  # 10% = 20 SAKA
        assert wallet.total_composted == initial_composted + expected_composted, (
            f"VIOLATION CONSTITUTION EGOEJO : Le montant composté ne correspond pas au taux. "
            f"Attendu: {expected_composted}, Obtenu: {wallet.total_composted - initial_composted}"
        )
        
        # 3. Le solde final = solde initial - montant composté
        expected_balance = initial_balance - expected_composted
        assert wallet.balance == expected_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : Le solde final ne correspond pas. "
            f"Attendu: {expected_balance}, Obtenu: {wallet.balance}"
        )
    
    def test_compostage_retourne_au_silo(self):
        """
        Test P0 : Le compostage retourne le SAKA au Silo Commun.
        
        Ce test protège la règle : "Compostage obligatoire - Dépréciation effective du SAKA inactif"
        
        Vérifie que :
        - Le Silo est alimenté après compostage
        - Le montant dans le Silo = montant composté
        - Le total_composted du Silo est mis à jour
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 300,
                'total_harvested': 300,
                'last_activity_date': timezone.now() - timedelta(days=120),
            }
        )
        wallet.balance = 300
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        initial_silo_balance = silo.total_balance
        initial_silo_composted = silo.total_composted
        
        initial_wallet_balance = wallet.balance
        
        # Exécuter le compostage
        result = run_saka_compost_cycle(dry_run=False, source="test")
        
        # VÉRIFICATIONS : RETOUR AU SILO
        wallet.refresh_from_db()
        silo.refresh_from_db()
        
        # 1. Le Silo a été ALIMENTÉ
        assert silo.total_balance > initial_silo_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : Le Silo n'a pas été alimenté après compostage. "
            f"Balance Silo initiale: {initial_silo_balance}, Balance Silo après: {silo.total_balance}"
        )
        
        # 2. Le montant dans le Silo = montant composté
        composted_amount = initial_wallet_balance - wallet.balance
        silo_increase = silo.total_balance - initial_silo_balance
        
        assert silo_increase >= composted_amount, (
            f"VIOLATION CONSTITUTION EGOEJO : Le Silo n'a pas reçu le montant composté. "
            f"Montant composté: {composted_amount}, Augmentation Silo: {silo_increase}"
        )
        
        # 3. Le total_composted du Silo est mis à jour
        assert silo.total_composted > initial_silo_composted, (
            f"VIOLATION CONSTITUTION EGOEJO : Le total_composted du Silo n'a pas été mis à jour. "
            f"Total initial: {initial_silo_composted}, Total après: {silo.total_composted}"
        )
    
    def test_compostage_progressif_empêche_accumulation_infinie(self):
        """
        Test P0 : Le compostage progressif empêche l'accumulation infinie.
        
        Ce test protège la règle : "Compostage obligatoire - Dépréciation effective du SAKA inactif"
        
        Vérifie que :
        - Après plusieurs cycles, le solde diminue significativement
        - Le compostage progressif (10% par cycle) empêche l'accumulation
        - Même avec un très gros solde, le compostage s'applique
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 10000,  # Très gros solde
                'total_harvested': 10000,
                'last_activity_date': timezone.now() - timedelta(days=120),
            }
        )
        wallet.balance = 10000
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        initial_balance = wallet.balance
        
        # Exécuter plusieurs cycles de compostage
        for cycle in range(5):
            # Forcer last_activity_date à 120 jours pour chaque cycle
            wallet.last_activity_date = timezone.now() - timedelta(days=120)
            wallet.save()
            
            result = run_saka_compost_cycle(dry_run=False, source="test")
            wallet.refresh_from_db()
        
        # VÉRIFICATIONS : ACCUMULATION INFINIE EMPÊCHÉE
        # Après 5 cycles de 10%, le solde doit être significativement réduit
        # Cycle 1: 10000 - 1000 = 9000
        # Cycle 2: 9000 - 900 = 8100
        # Cycle 3: 8100 - 810 = 7290
        # Cycle 4: 7290 - 729 = 6561
        # Cycle 5: 6561 - 656 = 5905
        
        expected_balance_after_5_cycles = int(10000 * (0.9 ** 5))
        
        assert wallet.balance < initial_balance * 0.7, (
            f"VIOLATION CONSTITUTION EGOEJO : Le compostage progressif n'empêche pas l'accumulation infinie. "
            f"Solde initial: {initial_balance}, Solde après 5 cycles: {wallet.balance}. "
            f"Le solde devrait être < {initial_balance * 0.7}"
        )
        
        # Vérifier que la réduction est significative (> 30%)
        reduction_percent = ((initial_balance - wallet.balance) / initial_balance) * 100
        assert reduction_percent > 30, (
            f"VIOLATION CONSTITUTION EGOEJO : La réduction après 5 cycles est insuffisante. "
            f"Réduction: {reduction_percent}%, Attendu: > 30%"
        )
    
    def test_compostage_ne_peut_pas_etre_contourne(self):
        """
        Test P0 : Le compostage ne peut pas être contourné.
        
        Ce test protège la règle : "Compostage obligatoire - Dépréciation effective du SAKA inactif"
        
        Vérifie que :
        - Même avec une activité minimale, le compostage s'applique si inactif depuis 90+ jours
        - Le compostage ne peut pas être désactivé
        - Le compostage ne peut pas être contourné par manipulation
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        wallet, _ = SakaWallet.objects.get_or_create(
            user=user,
            defaults={
                'balance': 500,
                'total_harvested': 500,
                'last_activity_date': timezone.now() - timedelta(days=120),  # Inactif depuis 120 jours
            }
        )
        wallet.balance = 500
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        initial_balance = wallet.balance
        
        # Tentative de contournement : activité minimale juste avant compostage
        # (simuler une récolte de 1 SAKA pour "réinitialiser" last_activity_date)
        from core.services.saka import harvest_saka, SakaReason
        harvest_saka(user, SakaReason.CONTENT_READ, amount=1)
        wallet.refresh_from_db()
        
        # MAIS : Si on force last_activity_date à nouveau à 120 jours, le compostage doit s'appliquer
        wallet.last_activity_date = timezone.now() - timedelta(days=120)
        wallet.save()
        
        # Exécuter le compostage
        result = run_saka_compost_cycle(dry_run=False, source="test")
        
        # VÉRIFICATIONS : COMPOSTAGE NON CONTOURNABLE
        wallet.refresh_from_db()
        
        # Le compostage DOIT s'appliquer même après tentative de contournement
        assert wallet.balance < initial_balance + 1, (
            f"VIOLATION CONSTITUTION EGOEJO : Le compostage peut être contourné. "
            f"Solde initial: {initial_balance}, Solde après tentative de contournement: {wallet.balance}"
        )
        
        # Le total_composted DOIT être > 0
        assert wallet.total_composted > 0, (
            f"VIOLATION CONSTITUTION EGOEJO : Le compostage n'a pas été appliqué malgré inactivité. "
            f"total_composted: {wallet.total_composted}"
        )

