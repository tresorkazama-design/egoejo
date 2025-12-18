"""
Tests d'intégration pour vérifier le rollback complet des transactions financières.

PHILOSOPHIE EGOEJO :
Les transactions financières doivent être atomiques. En cas d'exception partielle,
aucun changement ne doit persister (rollback complet).

Ces tests vérifient que :
1. Si une exception survient après un premier write, tous les changements sont annulés
2. Aucun solde n'a changé
3. Aucune transaction n'a été persistée
4. Aucun escrow incohérent n'existe
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


@pytest.fixture
def test_user(db):
    """Fixture pour créer un utilisateur de test"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_project(db):
    """Fixture pour créer un projet de test"""
    return Projet.objects.create(
        titre='Test Project',
        description='Test Description',
        funding_type='DONATION',
        donation_goal=Decimal('5000.00')
    )


@pytest.fixture
def funded_wallet(db, test_user):
    """Fixture pour créer un wallet avec des fonds"""
    wallet, _ = UserWallet.objects.get_or_create(user=test_user)
    wallet.balance = Decimal('1000.00')
    wallet.save()
    return wallet


@pytest.mark.django_db
class TestFinancialTransactionRollback:
    """
    Tests d'intégration pour vérifier le rollback complet des transactions financières.
    """
    
    def test_rollback_complet_si_exception_apres_modification_wallet(self, test_user, test_project, funded_wallet):
        """
        Test que si une exception survient APRÈS la modification du wallet.balance,
        le rollback est complet : aucun changement ne persiste.
        
        PHILOSOPHIE : Les transactions financières doivent être atomiques.
        Aucun write partiel ne doit survivre.
        
        Assertions obligatoires :
        - wallet.balance avant == après
        - aucune Transaction persistée
        - aucune trace escrow incohérente
        """
        # État initial
        initial_balance = funded_wallet.balance
        initial_transaction_count = WalletTransaction.objects.count()
        initial_escrow_count = EscrowContract.objects.count()
        
        amount = Decimal('100.00')
        
        # Provoquer une exception APRÈS que wallet.balance a été modifié
        # mais AVANT que l'escrow soit créé
        # On va mocker EscrowContract.objects.create() pour lever une exception
        with patch('finance.services.EscrowContract.objects.create') as mock_escrow_create:
            # Simuler une exception lors de la création de l'escrow
            mock_escrow_create.side_effect = Exception("Erreur simulée lors de la création de l'escrow")
            
            # La transaction doit échouer complètement
            with pytest.raises(Exception) as exc_info:
                pledge_funds(
                    user=test_user,
                    project=test_project,
                    amount=amount,
                    pledge_type='DONATION'
                )
            
            assert "Erreur simulée" in str(exc_info.value)
        
        # Vérifications : ROLLBACK COMPLET
        # 1. Le solde du wallet n'a PAS changé
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == initial_balance, (
            f"Le solde du wallet a changé malgré l'exception. "
            f"Attendu: {initial_balance}, Obtenu: {funded_wallet.balance}"
        )
        
        # 2. Aucune transaction n'a été persistée
        final_transaction_count = WalletTransaction.objects.count()
        assert final_transaction_count == initial_transaction_count, (
            f"Des transactions ont été créées malgré l'exception. "
            f"Initial: {initial_transaction_count}, Final: {final_transaction_count}"
        )
        
        # 3. Aucun escrow n'a été créé
        final_escrow_count = EscrowContract.objects.count()
        assert final_escrow_count == initial_escrow_count, (
            f"Un escrow a été créé malgré l'exception. "
            f"Initial: {initial_escrow_count}, Final: {final_escrow_count}"
        )
        
        # 4. Vérifier qu'aucune transaction liée au projet n'existe
        project_transactions = WalletTransaction.objects.filter(
            related_project=test_project
        )
        assert project_transactions.count() == 0, (
            f"Des transactions liées au projet existent malgré l'exception. "
            f"Nombre: {project_transactions.count()}"
        )
        
        # 5. Vérifier qu'aucun escrow lié au projet n'existe
        project_escrows = EscrowContract.objects.filter(
            project=test_project,
            user=test_user
        )
        assert project_escrows.count() == 0, (
            f"Des escrows liés au projet existent malgré l'exception. "
            f"Nombre: {project_escrows.count()}"
        )
    
    def test_rollback_complet_si_exception_apres_creation_transaction(self, test_user, test_project, funded_wallet):
        """
        Test que si une exception survient APRÈS la création de la WalletTransaction,
        le rollback est complet : aucun changement ne persiste.
        
        PHILOSOPHIE : Même si une transaction a été créée, le rollback doit l'annuler.
        """
        # État initial
        initial_balance = funded_wallet.balance
        initial_transaction_count = WalletTransaction.objects.count()
        initial_escrow_count = EscrowContract.objects.count()
        
        amount = Decimal('150.00')
        
        # Provoquer une exception APRÈS la création de WalletTransaction
        # mais AVANT la création de l'escrow
        with patch('finance.services.EscrowContract.objects.create') as mock_escrow_create:
            mock_escrow_create.side_effect = Exception("Erreur lors de la création de l'escrow")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=test_user,
                    project=test_project,
                    amount=amount,
                    pledge_type='DONATION'
                )
        
        # Vérifications : ROLLBACK COMPLET
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == initial_balance
        
        final_transaction_count = WalletTransaction.objects.count()
        assert final_transaction_count == initial_transaction_count
        
        final_escrow_count = EscrowContract.objects.count()
        assert final_escrow_count == initial_escrow_count
    
    def test_rollback_complet_si_exception_pendant_release_escrow(self, test_user, test_project, funded_wallet, db):
        """
        Test que si une exception survient pendant release_escrow,
        le rollback est complet : aucun changement ne persiste.
        
        PHILOSOPHIE : Même lors de la libération d'escrow, le rollback doit être complet.
        """
        from django.conf import settings
        
        # Créer un utilisateur système pour le wallet de commission
        system_user, _ = User.objects.get_or_create(
            username='system_egoejo',
            defaults={'email': 'system@egoejo.org', 'is_active': False}
        )
        system_wallet, _ = UserWallet.objects.get_or_create(user=system_user)
        
        # État initial
        initial_user_balance = funded_wallet.balance
        initial_system_balance = system_wallet.balance
        initial_transaction_count = WalletTransaction.objects.count()
        
        # Créer un escrow valide
        amount = Decimal('200.00')
        escrow = pledge_funds(
            user=test_user,
            project=test_project,
            amount=amount,
            pledge_type='DONATION'
        )
        
        # Vérifier que l'escrow a été créé
        assert escrow.status == 'LOCKED'
        
        # Provoquer une exception APRÈS la modification du wallet système
        # mais AVANT la mise à jour de l'escrow
        with patch.object(escrow, 'save') as mock_escrow_save:
            mock_escrow_save.side_effect = Exception("Erreur lors de la sauvegarde de l'escrow")
            
            with pytest.raises(Exception):
                release_escrow(escrow)
        
        # Vérifications : ROLLBACK COMPLET
        # 1. Le solde du wallet système n'a PAS changé
        system_wallet.refresh_from_db()
        assert system_wallet.balance == initial_system_balance, (
            f"Le solde du wallet système a changé malgré l'exception. "
            f"Attendu: {initial_system_balance}, Obtenu: {system_wallet.balance}"
        )
        
        # 2. Aucune transaction COMMISSION n'a été créée
        commission_transactions = WalletTransaction.objects.filter(
            transaction_type='COMMISSION',
            related_project=test_project
        )
        assert commission_transactions.count() == 0, (
            f"Une transaction COMMISSION a été créée malgré l'exception. "
            f"Nombre: {commission_transactions.count()}"
        )
        
        # 3. L'escrow est toujours en état LOCKED (pas RELEASED)
        escrow.refresh_from_db()
        assert escrow.status == 'LOCKED', (
            f"L'escrow a été libéré malgré l'exception. Statut: {escrow.status}"
        )
        assert escrow.released_at is None, (
            f"L'escrow a une date de libération malgré l'exception. "
            f"released_at: {escrow.released_at}"
        )
        
        # 4. Le nombre total de transactions n'a pas changé (sauf la transaction PLEDGE initiale)
        final_transaction_count = WalletTransaction.objects.count()
        # On a créé une transaction PLEDGE lors de pledge_funds, donc +1
        assert final_transaction_count == initial_transaction_count + 1, (
            f"Le nombre de transactions a changé de manière inattendue. "
            f"Initial: {initial_transaction_count}, Final: {final_transaction_count}"
        )
    
    def test_rollback_complet_si_exception_pendant_save_wallet(self, test_user, test_project, funded_wallet):
        """
        Test que si une exception survient pendant la sauvegarde du wallet,
        le rollback est complet : aucun changement ne persiste.
        
        PHILOSOPHIE : Même si le wallet.balance a été modifié en mémoire,
        le rollback doit annuler la sauvegarde.
        """
        # État initial
        initial_balance = funded_wallet.balance
        initial_transaction_count = WalletTransaction.objects.count()
        initial_escrow_count = EscrowContract.objects.count()
        
        amount = Decimal('75.00')
        
        # Provoquer une exception APRÈS la modification de wallet.balance
        # mais AVANT wallet.save()
        with patch.object(funded_wallet, 'save') as mock_wallet_save:
            # Première sauvegarde réussit (celle dans pledge_funds)
            # Mais on va intercepter la sauvegarde pour provoquer une exception
            call_count = [0]
            
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    # Première sauvegarde : laisser passer (celle qui modifie le balance)
                    return MagicMock()
                else:
                    # Deuxième sauvegarde : provoquer une exception
                    raise Exception("Erreur lors de la sauvegarde du wallet")
            
            mock_wallet_save.side_effect = side_effect
            
            # Utiliser un mock différent pour provoquer l'exception au bon moment
            # On va mocker directement dans pledge_funds
            with patch('finance.services.UserWallet.save') as mock_save:
                mock_save.side_effect = Exception("Erreur lors de la sauvegarde du wallet")
                
                with pytest.raises(Exception):
                    pledge_funds(
                        user=test_user,
                        project=test_project,
                        amount=amount,
                        pledge_type='DONATION'
                    )
        
        # Vérifications : ROLLBACK COMPLET
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == initial_balance
        
        final_transaction_count = WalletTransaction.objects.count()
        assert final_transaction_count == initial_transaction_count
        
        final_escrow_count = EscrowContract.objects.count()
        assert final_escrow_count == initial_escrow_count
    
    def test_rollback_complet_si_exception_pendant_creation_transaction(self, test_user, test_project, funded_wallet):
        """
        Test que si une exception survient pendant la création de WalletTransaction,
        le rollback est complet : aucun changement ne persiste.
        
        PHILOSOPHIE : Même si wallet.balance a été modifié, le rollback doit être complet.
        """
        # État initial
        initial_balance = funded_wallet.balance
        initial_transaction_count = WalletTransaction.objects.count()
        initial_escrow_count = EscrowContract.objects.count()
        
        amount = Decimal('125.00')
        
        # Provoquer une exception lors de la création de WalletTransaction
        with patch('finance.services.WalletTransaction.objects.create') as mock_tx_create:
            mock_tx_create.side_effect = Exception("Erreur lors de la création de la transaction")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=test_user,
                    project=test_project,
                    amount=amount,
                    pledge_type='DONATION'
                )
        
        # Vérifications : ROLLBACK COMPLET
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == initial_balance, (
            f"Le solde du wallet a changé malgré l'exception. "
            f"Attendu: {initial_balance}, Obtenu: {funded_wallet.balance}"
        )
        
        final_transaction_count = WalletTransaction.objects.count()
        assert final_transaction_count == initial_transaction_count, (
            f"Des transactions ont été créées malgré l'exception. "
            f"Initial: {initial_transaction_count}, Final: {final_transaction_count}"
        )
        
        final_escrow_count = EscrowContract.objects.count()
        assert final_escrow_count == initial_escrow_count, (
            f"Des escrows ont été créés malgré l'exception. "
            f"Initial: {initial_escrow_count}, Final: {final_escrow_count}"
        )
    
    def test_etat_strictement_identique_apres_rollback(self, test_user, test_project, funded_wallet):
        """
        Test que l'état est strictement identique à l'état initial après un rollback.
        
        PHILOSOPHIE : Aucune trace de la transaction partielle ne doit exister.
        """
        # État initial complet
        initial_balance = funded_wallet.balance
        initial_transaction_count = WalletTransaction.objects.count()
        initial_escrow_count = EscrowContract.objects.count()
        
        # Récupérer tous les IDs initiaux pour vérifier qu'aucun nouvel objet n'a été créé
        initial_transaction_ids = set(
            WalletTransaction.objects.values_list('id', flat=True)
        )
        initial_escrow_ids = set(
            EscrowContract.objects.values_list('id', flat=True)
        )
        
        amount = Decimal('300.00')
        
        # Provoquer une exception
        with patch('finance.services.EscrowContract.objects.create') as mock_escrow_create:
            mock_escrow_create.side_effect = Exception("Erreur simulée")
            
            with pytest.raises(Exception):
                pledge_funds(
                    user=test_user,
                    project=test_project,
                    amount=amount,
                    pledge_type='DONATION'
                )
        
        # Vérifications : ÉTAT STRICTEMENT IDENTIQUE
        # 1. Solde identique
        funded_wallet.refresh_from_db()
        assert funded_wallet.balance == initial_balance
        
        # 2. Nombre de transactions identique
        final_transaction_count = WalletTransaction.objects.count()
        assert final_transaction_count == initial_transaction_count
        
        # 3. Nombre d'escrows identique
        final_escrow_count = EscrowContract.objects.count()
        assert final_escrow_count == initial_escrow_count
        
        # 4. Aucun nouvel objet créé (IDs identiques)
        final_transaction_ids = set(
            WalletTransaction.objects.values_list('id', flat=True)
        )
        assert final_transaction_ids == initial_transaction_ids, (
            f"De nouvelles transactions ont été créées malgré l'exception. "
            f"Initial: {initial_transaction_ids}, Final: {final_transaction_ids}"
        )
        
        final_escrow_ids = set(
            EscrowContract.objects.values_list('id', flat=True)
        )
        assert final_escrow_ids == initial_escrow_ids, (
            f"De nouveaux escrows ont été créés malgré l'exception. "
            f"Initial: {initial_escrow_ids}, Final: {final_escrow_ids}"
        )
        
        # 5. Aucune transaction liée au projet
        project_transactions = WalletTransaction.objects.filter(
            related_project=test_project
        )
        assert project_transactions.count() == 0
        
        # 6. Aucun escrow lié au projet
        project_escrows = EscrowContract.objects.filter(
            project=test_project,
            user=test_user
        )
        assert project_escrows.count() == 0

