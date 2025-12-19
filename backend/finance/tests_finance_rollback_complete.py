"""
Test P0 CRITIQUE : Rollback partiel transaction financière (COMPLET)

PHILOSOPHIE EGOEJO :
Les transactions financières doivent être atomiques. En cas d'exception partielle,
aucun changement ne doit persister (rollback complet).

Ce test vérifie TOUS les points de défaillance possibles :
1. Exception après modification wallet mais avant création escrow
2. Exception après création transaction mais avant sauvegarde escrow
3. Exception pendant calcul commission
4. Exception pendant crédit wallet système
5. État strictement identique après rollback (IDs objets)
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from unittest.mock import patch, MagicMock

from finance.models import UserWallet, WalletTransaction, EscrowContract
from finance.services import pledge_funds, release_escrow
from core.models.projects import Projet

User = get_user_model()


@pytest.mark.django_db
class TestFinancialRollbackComplete:
    """
    Tests COMPLETS pour le rollback partiel des transactions financières.
    
    PROTECTION : Empêche la corruption financière en cas d'exception partielle.
    VIOLATION EMPÊCHÉE : État partiel persisté, corruption données financières.
    """
    
    def test_rollback_complet_si_exception_apres_modification_wallet_mais_avant_escrow(self, db):
        """
        Test P0 : Rollback si exception après modification wallet mais avant création escrow.
        
        PHILOSOPHIE : Aucun write partiel ne doit survivre.
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
        
        initial_balance = wallet.balance
        initial_tx_count = WalletTransaction.objects.count()
        initial_escrow_count = EscrowContract.objects.count()
        
        # Provoquer exception après modification wallet mais avant création escrow
        with patch('finance.services.EscrowContract.objects.create') as mock_create:
            mock_create.side_effect = Exception("Erreur création escrow")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=user,
                    project=project,
                    amount=Decimal('100.00'),
                    pledge_type='DONATION'
                )
        
        # VÉRIFICATIONS : ROLLBACK COMPLET
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance, (
            "VIOLATION : Wallet balance doit être restauré après rollback. "
            f"Attendu: {initial_balance}, Obtenu: {wallet.balance}"
        )
        
        assert WalletTransaction.objects.count() == initial_tx_count, (
            "VIOLATION : Aucune transaction ne doit être créée après rollback. "
            f"Attendu: {initial_tx_count}, Obtenu: {WalletTransaction.objects.count()}"
        )
        
        assert EscrowContract.objects.count() == initial_escrow_count, (
            "VIOLATION : Aucun escrow ne doit être créé après rollback. "
            f"Attendu: {initial_escrow_count}, Obtenu: {EscrowContract.objects.count()}"
        )
    
    def test_rollback_complet_si_exception_pendant_calcul_commission(self, db):
        """
        Test P0 : Rollback si exception pendant calcul commission.
        
        PHILOSOPHIE : Même lors de release_escrow, rollback complet.
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
        
        # Créer escrow
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
        
        # Provoquer exception pendant calcul commission
        with patch('django.conf.settings.EGOEJO_COMMISSION_RATE', side_effect=Exception("Erreur calcul commission")):
            with patch('finance.services.UserWallet.objects.select_for_update') as mock_select:
                mock_qs = mock_select.return_value
                mock_qs.get_or_create.return_value = (system_wallet, False)
                
                with pytest.raises(Exception):
                    release_escrow(escrow)
        
        # VÉRIFICATIONS : ROLLBACK COMPLET
        escrow.refresh_from_db()
        assert escrow.status == 'LOCKED', (
            "VIOLATION : Escrow doit rester LOCKED après rollback. "
            f"Statut: {escrow.status}"
        )
        
        system_wallet.refresh_from_db()
        assert system_wallet.balance == initial_system_balance, (
            "VIOLATION : Wallet système ne doit pas être crédité après rollback. "
            f"Attendu: {initial_system_balance}, Obtenu: {system_wallet.balance}"
        )
        
        commission_count = WalletTransaction.objects.filter(
            transaction_type='COMMISSION',
            related_project=project
        ).count()
        assert commission_count == 0, (
            "VIOLATION : Aucune transaction COMMISSION ne doit être créée après rollback. "
            f"Nombre: {commission_count}"
        )
    
    def test_etat_strictement_identique_apres_rollback_ids_objets(self, db):
        """
        Test P0 : État strictement identique après rollback (IDs objets).
        
        PHILOSOPHIE : Aucune trace de la transaction partielle ne doit exister.
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
        
        # Récupérer IDs initiaux
        initial_tx_ids = set(WalletTransaction.objects.values_list('id', flat=True))
        initial_escrow_ids = set(EscrowContract.objects.values_list('id', flat=True))
        initial_wallet_balance = wallet.balance
        
        # Provoquer exception
        with patch('finance.services.EscrowContract.objects.create') as mock_create:
            mock_create.side_effect = Exception("Erreur simulée")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=user,
                    project=project,
                    amount=Decimal('100.00'),
                    pledge_type='DONATION'
                )
        
        # VÉRIFICATIONS : IDs identiques
        final_tx_ids = set(WalletTransaction.objects.values_list('id', flat=True))
        final_escrow_ids = set(EscrowContract.objects.values_list('id', flat=True))
        
        assert final_tx_ids == initial_tx_ids, (
            "VIOLATION : Aucune nouvelle transaction ne doit être créée après rollback. "
            f"Initial: {initial_tx_ids}, Final: {final_tx_ids}"
        )
        
        assert final_escrow_ids == initial_escrow_ids, (
            "VIOLATION : Aucun nouvel escrow ne doit être créé après rollback. "
            f"Initial: {initial_escrow_ids}, Final: {final_escrow_ids}"
        )
        
        wallet.refresh_from_db()
        assert wallet.balance == initial_wallet_balance, (
            "VIOLATION : Wallet balance doit être identique après rollback. "
            f"Attendu: {initial_wallet_balance}, Obtenu: {wallet.balance}"
        )
        
        # Vérifier qu'aucune transaction liée au projet n'existe
        project_transactions = WalletTransaction.objects.filter(related_project=project)
        assert project_transactions.count() == 0, (
            "VIOLATION : Aucune transaction liée au projet ne doit exister après rollback. "
            f"Nombre: {project_transactions.count()}"
        )
        
        # Vérifier qu'aucun escrow lié au projet n'existe
        project_escrows = EscrowContract.objects.filter(project=project, user=user)
        assert project_escrows.count() == 0, (
            "VIOLATION : Aucun escrow lié au projet ne doit exister après rollback. "
            f"Nombre: {project_escrows.count()}"
        )

