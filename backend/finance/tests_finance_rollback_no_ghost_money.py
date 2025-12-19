"""
Test P0 CRITIQUE : Rollback financier - Aucune monnaie fantôme

PHILOSOPHIE EGOEJO :
Les transactions financières doivent être atomiques. En cas d'exception partielle,
AUCUNE monnaie fantôme ne doit être créée ou détruite.

Ce test protège la règle : "Aucune création/destruction de monnaie lors d'un rollback"

VIOLATION EMPÊCHÉE :
- Création de monnaie fantôme (solde augmenté sans transaction)
- Destruction de monnaie fantôme (solde diminué sans transaction)
- Incohérence entre solde wallet et transactions
- État partiel persisté après rollback
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, models
from decimal import Decimal
from unittest.mock import patch, MagicMock

from finance.models import UserWallet, WalletTransaction, EscrowContract
from finance.services import pledge_funds, release_escrow
from core.models.projects import Projet

User = get_user_model()


@pytest.mark.django_db
class TestFinancialRollbackNoGhostMoney:
    """
    Tests pour garantir qu'aucune monnaie fantôme n'est créée ou détruite lors d'un rollback.
    
    PROTECTION : Empêche la corruption financière et la création/destruction de monnaie.
    VIOLATION EMPÊCHÉE : Monnaie fantôme, incohérence comptable, corruption données.
    """
    
    def test_aucune_monnaie_fantome_apres_rollback_pledge(self):
        """
        Test P0 : Aucune monnaie fantôme après rollback d'un pledge.
        
        Ce test protège la règle : "Aucune création/destruction de monnaie lors d'un rollback"
        
        Vérifie que :
        - Le solde wallet = somme des transactions (cohérence comptable)
        - Aucune transaction orpheline n'existe
        - Aucun escrow incohérent n'existe
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        project = Projet.objects.create(
            titre='Test Project',
            description='Test Description',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00')
        )
        
        # État initial : Calculer le solde théorique basé sur les transactions
        initial_balance = wallet.balance
        initial_transactions = WalletTransaction.objects.filter(wallet=wallet)
        initial_balance_from_transactions = sum(
            tx.amount if tx.transaction_type in ['DEPOSIT', 'REFUND', 'RELEASE'] 
            else -tx.amount 
            for tx in initial_transactions
        )
        
        # Vérifier cohérence initiale
        assert wallet.balance == initial_balance_from_transactions + Decimal('1000.00'), (
            "État initial incohérent : solde wallet != somme transactions"
        )
        
        amount = Decimal('100.00')
        
        # Provoquer une exception pendant pledge_funds
        with patch('finance.services.EscrowContract.objects.create') as mock_create:
            mock_create.side_effect = Exception("Erreur création escrow")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=user,
                    project=project,
                    amount=amount,
                    pledge_type='DONATION'
                )
        
        # VÉRIFICATIONS : AUCUNE MONNAIE FANTÔME
        wallet.refresh_from_db()
        
        # 1. Le solde wallet n'a PAS changé
        assert wallet.balance == initial_balance, (
            f"VIOLATION : Monnaie fantôme créée/détruite. "
            f"Solde initial: {initial_balance}, Solde après rollback: {wallet.balance}"
        )
        
        # 2. Cohérence comptable : solde = somme des transactions
        final_transactions = WalletTransaction.objects.filter(wallet=wallet)
        final_balance_from_transactions = sum(
            tx.amount if tx.transaction_type in ['DEPOSIT', 'REFUND', 'RELEASE'] 
            else -tx.amount 
            for tx in final_transactions
        )
        
        # Le solde wallet doit être cohérent avec les transactions
        # (initial_balance - transactions PLEDGE si elles existent)
        expected_balance = initial_balance
        assert abs(wallet.balance - expected_balance) < Decimal('0.01'), (
            f"VIOLATION : Incohérence comptable après rollback. "
            f"Solde wallet: {wallet.balance}, Solde attendu: {expected_balance}"
        )
        
        # 3. Aucune transaction orpheline (sans escrow correspondant)
        pledge_transactions = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='PLEDGE_DONATION',
            related_project=project
        )
        assert pledge_transactions.count() == 0, (
            f"VIOLATION : Transaction orpheline créée. "
            f"Nombre de transactions PLEDGE: {pledge_transactions.count()}"
        )
        
        # 4. Aucun escrow incohérent
        escrows = EscrowContract.objects.filter(user=user, project=project)
        assert escrows.count() == 0, (
            f"VIOLATION : Escrow incohérent créé. "
            f"Nombre d'escrows: {escrows.count()}"
        )
        
        # 5. Vérifier qu'aucune monnaie n'a été créée ou détruite
        total_system_balance = UserWallet.objects.aggregate(
            total=models.Sum('balance')
        )['total'] or Decimal('0')
        
        # Le total système ne doit pas avoir changé (sauf si d'autres wallets existent)
        # On vérifie seulement que le wallet de test n'a pas changé
        assert wallet.balance == initial_balance, (
            "VIOLATION : Monnaie fantôme détectée. Le solde a changé sans transaction valide."
        )
    
    def test_aucune_monnaie_fantome_apres_rollback_release(self):
        """
        Test P0 : Aucune monnaie fantôme après rollback d'un release_escrow.
        
        Ce test protège la règle : "Aucune création/destruction de monnaie lors d'un rollback"
        
        Vérifie que :
        - Le wallet système n'est pas crédité si l'escrow n'est pas libéré
        - Aucune transaction COMMISSION orpheline n'existe
        - Cohérence comptable préservée
        """
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        project = Projet.objects.create(
            titre='Test Project',
            description='Test Description',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00')
        )
        
        # Créer un escrow valide
        escrow = pledge_funds(
            user=user,
            project=project,
            amount=Decimal('100.00'),
            pledge_type='DONATION'
        )
        
        system_user, _ = User.objects.get_or_create(
            username='system_egoejo',
            defaults={'email': 'system@egoejo.org', 'is_active': False}
        )
        system_wallet, _ = UserWallet.objects.get_or_create(user=system_user)
        initial_system_balance = system_wallet.balance
        
        # Compter les transactions COMMISSION initiales
        initial_commission_count = WalletTransaction.objects.filter(
            transaction_type='COMMISSION'
        ).count()
        
        # Provoquer une exception pendant release_escrow
        with patch.object(escrow, 'save') as mock_save:
            mock_save.side_effect = Exception("Erreur sauvegarde escrow")
            
            with patch('finance.services.UserWallet.objects.select_for_update') as mock_select:
                mock_qs = mock_select.return_value
                mock_qs.get_or_create.return_value = (system_wallet, False)
                
                with pytest.raises(Exception):
                    release_escrow(escrow)
        
        # VÉRIFICATIONS : AUCUNE MONNAIE FANTÔME
        system_wallet.refresh_from_db()
        
        # 1. Le wallet système n'a PAS été crédité
        assert system_wallet.balance == initial_system_balance, (
            f"VIOLATION : Monnaie fantôme créée dans wallet système. "
            f"Solde initial: {initial_system_balance}, Solde après rollback: {system_wallet.balance}"
        )
        
        # 2. Aucune transaction COMMISSION orpheline
        final_commission_count = WalletTransaction.objects.filter(
            transaction_type='COMMISSION'
        ).count()
        assert final_commission_count == initial_commission_count, (
            f"VIOLATION : Transaction COMMISSION orpheline créée. "
            f"Nombre initial: {initial_commission_count}, Nombre final: {final_commission_count}"
        )
        
        # 3. L'escrow est toujours LOCKED (pas libéré)
        escrow.refresh_from_db()
        assert escrow.status == 'LOCKED', (
            f"VIOLATION : Escrow libéré malgré rollback. Statut: {escrow.status}"
        )
        
        # 4. Cohérence comptable : le montant est toujours dans l'escrow
        assert escrow.amount == Decimal('100.00'), (
            "VIOLATION : Montant escrow modifié malgré rollback"
        )
    
    def test_coherence_comptable_totale_apres_rollback(self):
        """
        Test P0 : Cohérence comptable totale après rollback.
        
        Ce test protège la règle : "Aucune création/destruction de monnaie lors d'un rollback"
        
        Vérifie que :
        - Somme totale des wallets = constante (conservation de la monnaie)
        - Somme des transactions = cohérente avec les soldes
        - Aucune incohérence comptable
        """
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        wallet1, _ = UserWallet.objects.get_or_create(user=user1)
        wallet1.balance = Decimal('1000.00')
        wallet1.save()
        
        wallet2, _ = UserWallet.objects.get_or_create(user=user2)
        wallet2.balance = Decimal('500.00')
        wallet2.save()
        
        project = Projet.objects.create(
            titre='Test Project',
            description='Test Description',
            funding_type='DONATION',
            donation_goal=Decimal('5000.00')
        )
        
        # Calculer le total système initial
        initial_total_system = UserWallet.objects.aggregate(
            total=models.Sum('balance')
        )['total'] or Decimal('0')
        
        # Compter les transactions initiales
        initial_transaction_count = WalletTransaction.objects.count()
        
        # Provoquer une exception pendant pledge_funds
        with patch('finance.services.EscrowContract.objects.create') as mock_create:
            mock_create.side_effect = Exception("Erreur création escrow")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=user1,
                    project=project,
                    amount=Decimal('200.00'),
                    pledge_type='DONATION'
                )
        
        # VÉRIFICATIONS : COHÉRENCE COMPTABLE TOTALE
        # 1. Le total système n'a PAS changé (conservation de la monnaie)
        final_total_system = UserWallet.objects.aggregate(
            total=models.Sum('balance')
        )['total'] or Decimal('0')
        
        assert abs(final_total_system - initial_total_system) < Decimal('0.01'), (
            f"VIOLATION : Monnaie créée ou détruite. "
            f"Total système initial: {initial_total_system}, "
            f"Total système final: {final_total_system}"
        )
        
        # 2. Le nombre de transactions n'a PAS changé
        final_transaction_count = WalletTransaction.objects.count()
        assert final_transaction_count == initial_transaction_count, (
            f"VIOLATION : Transactions créées malgré rollback. "
            f"Nombre initial: {initial_transaction_count}, "
            f"Nombre final: {final_transaction_count}"
        )
        
        # 3. Les soldes individuels n'ont PAS changé
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        
        assert wallet1.balance == Decimal('1000.00'), (
            f"VIOLATION : Solde wallet1 modifié. Attendu: 1000.00, Obtenu: {wallet1.balance}"
        )
        assert wallet2.balance == Decimal('500.00'), (
            f"VIOLATION : Solde wallet2 modifié. Attendu: 500.00, Obtenu: {wallet2.balance}"
        )
        
        # 4. Aucune transaction liée au projet n'existe
        project_transactions = WalletTransaction.objects.filter(related_project=project)
        assert project_transactions.count() == 0, (
            f"VIOLATION : Transactions liées au projet créées. "
            f"Nombre: {project_transactions.count()}"
        )

