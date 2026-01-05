"""
Tests pour le système financier (UserWallet, WalletTransaction, EscrowContract, WalletPocket).
"""
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from finance.models import UserWallet, WalletTransaction, EscrowContract, WalletPocket
from core.models.projects import Projet


class UserWalletTestCase(TestCase):
    """Tests pour le modèle UserWallet"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_wallet_created_automatically(self):
        """Test que le wallet est créé automatiquement via get_or_create"""
        wallet, created = UserWallet.objects.get_or_create(user=self.user)
        self.assertTrue(created)
        self.assertEqual(wallet.balance, Decimal('0.00'))
        self.assertEqual(wallet.user, self.user)
    
    def test_wallet_balance_default(self):
        """Test que le solde par défaut est 0"""
        wallet = UserWallet.objects.create(user=self.user)
        self.assertEqual(wallet.balance, Decimal('0.00'))
    
    def test_wallet_str(self):
        """Test la représentation string du wallet"""
        wallet = UserWallet.objects.create(user=self.user)
        self.assertIn('testuser', str(wallet))
        # Le __str__ retourne "0 €" (format français), pas "0.00"
        self.assertIn('0', str(wallet))
        self.assertIn('€', str(wallet))


class WalletTransactionTestCase(TestCase):
    """Tests pour le modèle WalletTransaction"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = UserWallet.objects.get_or_create(user=self.user)[0]
        self.project = Projet.objects.create(
            titre='Test Project',
            description='Test Description'
        )
    
    def test_create_deposit_transaction(self):
        """Test la création d'une transaction de dépôt"""
        transaction = WalletTransaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('100.00'),
            transaction_type='DEPOSIT',
            description='Dépôt initial'
        )
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.transaction_type, 'DEPOSIT')
        self.assertEqual(transaction.wallet, self.wallet)
    
    def test_create_pledge_donation_transaction(self):
        """Test la création d'une transaction de don (cantonné)"""
        transaction = WalletTransaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('50.00'),
            transaction_type='PLEDGE_DONATION',
            related_project=self.project,
            description='Don au projet Test'
        )
        self.assertEqual(transaction.amount, Decimal('50.00'))
        self.assertEqual(transaction.transaction_type, 'PLEDGE_DONATION')
        self.assertEqual(transaction.related_project, self.project)
    
    def test_transaction_idempotency_key(self):
        """Test que l'idempotency_key est unique"""
        import uuid
        key = uuid.uuid4()
        
        transaction1 = WalletTransaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('100.00'),
            transaction_type='DEPOSIT',
            idempotency_key=key
        )
        
        # Tentative de créer une deuxième transaction avec la même clé
        with self.assertRaises(Exception):  # IntegrityError
            WalletTransaction.objects.create(
                wallet=self.wallet,
                amount=Decimal('200.00'),
                transaction_type='DEPOSIT',
                idempotency_key=key
            )
    
    def test_transaction_str(self):
        """Test la représentation string de la transaction"""
        transaction = WalletTransaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('100.00'),
            transaction_type='DEPOSIT'
        )
        self.assertIn('DEPOSIT', str(transaction))
        self.assertIn('100.00', str(transaction))


class EscrowContractTestCase(TestCase):
    """Tests pour le modèle EscrowContract"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = UserWallet.objects.get_or_create(user=self.user)[0]
        self.project = Projet.objects.create(
            titre='Test Project',
            description='Test Description'
        )
        self.pledge_transaction = WalletTransaction.objects.create(
            wallet=self.wallet,
            amount=Decimal('100.00'),
            transaction_type='PLEDGE_DONATION',
            related_project=self.project
        )
    
    def test_create_escrow_contract(self):
        """Test la création d'un contrat d'escrow"""
        escrow = EscrowContract.objects.create(
            user=self.user,
            project=self.project,
            amount=Decimal('100.00'),
            status='LOCKED',
            pledge_transaction=self.pledge_transaction
        )
        self.assertEqual(escrow.amount, Decimal('100.00'))
        self.assertEqual(escrow.status, 'LOCKED')
        self.assertEqual(escrow.user, self.user)
        self.assertEqual(escrow.project, self.project)
    
    def test_escrow_default_status(self):
        """Test que le statut par défaut est LOCKED"""
        escrow = EscrowContract.objects.create(
            user=self.user,
            project=self.project,
            amount=Decimal('100.00'),
            pledge_transaction=self.pledge_transaction
        )
        self.assertEqual(escrow.status, 'LOCKED')
    
    def test_escrow_str(self):
        """Test la représentation string du contrat d'escrow"""
        escrow = EscrowContract.objects.create(
            user=self.user,
            project=self.project,
            amount=Decimal('100.00'),
            pledge_transaction=self.pledge_transaction
        )
        self.assertIn('testuser', str(escrow))
        self.assertIn('Test Project', str(escrow))
        self.assertIn('100.00', str(escrow))
        self.assertIn('LOCKED', str(escrow))


class WalletPocketTestCase(TestCase):
    """Tests pour le modèle WalletPocket"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.wallet = UserWallet.objects.get_or_create(user=self.user)[0]
    
    def test_create_donation_pocket(self):
        """Test la création d'une pocket de type DONATION"""
        pocket = WalletPocket.objects.create(
            wallet=self.wallet,
            name='Dons Environnement',
            pocket_type='DONATION',
            current_amount=Decimal('50.00')
        )
        self.assertEqual(pocket.name, 'Dons Environnement')
        self.assertEqual(pocket.pocket_type, 'DONATION')
        self.assertEqual(pocket.current_amount, Decimal('50.00'))
    
    def test_create_investment_reserve_pocket(self):
        """Test la création d'une pocket de type INVESTMENT_RESERVE"""
        pocket = WalletPocket.objects.create(
            wallet=self.wallet,
            name='Réserve Investissement',
            pocket_type='INVESTMENT_RESERVE',
            current_amount=Decimal('200.00')
        )
        self.assertEqual(pocket.pocket_type, 'INVESTMENT_RESERVE')
    
    def test_pocket_unique_name_per_wallet(self):
        """Test qu'un wallet ne peut pas avoir deux pockets avec le même nom"""
        WalletPocket.objects.create(
            wallet=self.wallet,
            name='Dons Environnement',
            pocket_type='DONATION'
        )
        
        # Tentative de créer une deuxième pocket avec le même nom
        with self.assertRaises(Exception):  # IntegrityError
            WalletPocket.objects.create(
                wallet=self.wallet,
                name='Dons Environnement',
                pocket_type='DONATION'
            )
    
    def test_pocket_allocation_percentage_validation(self):
        """Test que le pourcentage d'allocation ne peut pas dépasser 100%"""
        pocket = WalletPocket(
            wallet=self.wallet,
            name='Test Pocket',
            pocket_type='DONATION',
            allocation_percentage=Decimal('150.00')  # > 100%
        )
        with self.assertRaises(Exception):  # ValidationError
            pocket.full_clean()
    
    def test_pocket_str(self):
        """Test la représentation string de la pocket"""
        pocket = WalletPocket.objects.create(
            wallet=self.wallet,
            name='Dons Environnement',
            pocket_type='DONATION',
            current_amount=Decimal('50.00')
        )
        self.assertIn('Dons Environnement', str(pocket))
        self.assertIn('testuser', str(pocket))
        self.assertIn('50.00', str(pocket))

