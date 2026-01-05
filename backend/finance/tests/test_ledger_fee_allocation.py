"""
Tests pour la répartition proportionnelle des frais Stripe.

Vérifie que :
- Les frais sont répartis proportionnellement entre Donation et Tip
- Sum(Net) + Sum(Fees) = Total Payment
- Les montants sont correctement enregistrés dans les Ledgers
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from finance.ledger_services.ledger import (
    calculate_proportional_fees,
    allocate_payment_to_ledgers,
    extract_stripe_fee_from_webhook
)
from finance.models import WalletTransaction

User = get_user_model()


@pytest.mark.django_db
class TestCalculateProportionalFees:
    """Tests pour calculate_proportional_fees"""
    
    def test_proportional_fee_calculation_example(self):
        """
        Test avec l'exemple de la spécification :
        - Total : 105€ (100€ Don + 5€ Tip)
        - Frais Stripe : 1.83€
        - Ratio Donation : 100/105 = 0.952
        - Ratio Tip : 5/105 = 0.048
        - Fee on Donation : 1.83 * 0.952 = 1.74€
        - Fee on Tip : 1.83 * 0.048 = 0.09€
        """
        total_amount = Decimal('105.00')
        donation_amount = Decimal('100.00')
        tip_amount = Decimal('5.00')
        total_stripe_fee = Decimal('1.83')
        
        fee_on_donation, fee_on_tip = calculate_proportional_fees(
            total_amount=total_amount,
            donation_amount=donation_amount,
            tip_amount=tip_amount,
            total_stripe_fee=total_stripe_fee
        )
        
        # Vérifier les ratios
        expected_donation_ratio = donation_amount / total_amount
        expected_tip_ratio = tip_amount / total_amount
        
        assert abs(fee_on_donation - (total_stripe_fee * expected_donation_ratio)) < Decimal('0.01')
        assert abs(fee_on_tip - (total_stripe_fee * expected_tip_ratio)) < Decimal('0.01')
        
        # Vérifier que la somme des frais = total_stripe_fee
        fee_sum = fee_on_donation + fee_on_tip
        assert abs(fee_sum - total_stripe_fee) < Decimal('0.01')
        
        # Vérifier les montants nets
        donation_net = donation_amount - fee_on_donation
        tip_net = tip_amount - fee_on_tip
        
        # Vérifier la garantie : Sum(Net) + Sum(Fees) = Total Payment
        net_sum = donation_net + tip_net
        assert abs((net_sum + fee_sum) - total_amount) < Decimal('0.01')
    
    def test_proportional_fee_only_donation(self):
        """Test avec seulement un don (pas de tip)"""
        total_amount = Decimal('100.00')
        donation_amount = Decimal('100.00')
        tip_amount = Decimal('0.00')
        total_stripe_fee = Decimal('1.83')
        
        fee_on_donation, fee_on_tip = calculate_proportional_fees(
            total_amount=total_amount,
            donation_amount=donation_amount,
            tip_amount=tip_amount,
            total_stripe_fee=total_stripe_fee
        )
        
        assert fee_on_donation == total_stripe_fee
        assert fee_on_tip == Decimal('0.00')
    
    def test_proportional_fee_only_tip(self):
        """Test avec seulement un tip (pas de donation)"""
        total_amount = Decimal('5.00')
        donation_amount = Decimal('0.00')
        tip_amount = Decimal('5.00')
        total_stripe_fee = Decimal('0.33')
        
        fee_on_donation, fee_on_tip = calculate_proportional_fees(
            total_amount=total_amount,
            donation_amount=donation_amount,
            tip_amount=tip_amount,
            total_stripe_fee=total_stripe_fee
        )
        
        assert fee_on_donation == Decimal('0.00')
        assert fee_on_tip == total_stripe_fee
    
    def test_proportional_fee_inconsistent_amounts(self):
        """Test avec des montants incohérents"""
        total_amount = Decimal('100.00')
        donation_amount = Decimal('50.00')
        tip_amount = Decimal('60.00')  # 50 + 60 = 110 ≠ 100
        
        with pytest.raises(ValidationError, match="Montants incohérents"):
            calculate_proportional_fees(
                total_amount=total_amount,
                donation_amount=donation_amount,
                tip_amount=tip_amount,
                total_stripe_fee=Decimal('1.83')
            )


@pytest.mark.django_db
class TestAllocatePaymentToLedgers:
    """Tests pour allocate_payment_to_ledgers"""
    
    @pytest.fixture
    def test_user(self):
        """Créer un utilisateur de test"""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def test_project(self):
        """Créer un projet de test"""
        from core.models import Projet
        return Projet.objects.create(
            titre='Test Project',
            description='Test Description',
            funding_type='DONATION'
        )
    
    def test_allocate_payment_example(self, test_user, test_project):
        """
        Test avec l'exemple de la spécification :
        - Total : 105€ (100€ Don + 5€ Tip)
        - Frais Stripe : 1.83€
        - PROJECT_ESCROW = 100€ - 1.74€ = 98.26€
        - OPERATING = 5€ - 0.09€ = 4.91€
        """
        donation_amount = Decimal('100.00')
        tip_amount = Decimal('5.00')
        total_stripe_fee = Decimal('1.83')
        
        result = allocate_payment_to_ledgers(
            user=test_user,
            donation_amount=donation_amount,
            tip_amount=tip_amount,
            total_stripe_fee=total_stripe_fee,
            project=test_project,
            idempotency_key=None
        )
        
        # Vérifier la structure du résultat
        assert result['donation'] is not None
        assert result['tip'] is not None
        
        # Vérifier les montants de la donation
        donation_data = result['donation']
        assert donation_data['amount_gross'] == donation_amount
        assert donation_data['amount_net'] == donation_amount - donation_data['stripe_fee']
        assert donation_data['transaction'].transaction_type == 'PLEDGE_DONATION'
        assert donation_data['transaction'].related_project == test_project
        
        # Vérifier les montants du tip
        tip_data = result['tip']
        assert tip_data['amount_gross'] == tip_amount
        assert tip_data['amount_net'] == tip_amount - tip_data['stripe_fee']
        assert tip_data['transaction'].transaction_type == 'DEPOSIT'
        assert tip_data['transaction'].related_project is None
        
        # Vérifier la garantie : Sum(Net) + Sum(Fees) = Total Payment
        total_amount = donation_amount + tip_amount
        net_sum = donation_data['amount_net'] + tip_data['amount_net']
        fee_sum = donation_data['stripe_fee'] + tip_data['stripe_fee']
        
        assert abs((net_sum + fee_sum) - total_amount) < Decimal('0.01')
        
        # Vérifier que les transactions sont enregistrées dans la DB
        assert WalletTransaction.objects.filter(
            idempotency_key=donation_data['transaction'].idempotency_key
        ).exists()
        assert WalletTransaction.objects.filter(
            idempotency_key=tip_data['transaction'].idempotency_key
        ).exists()
    
    def test_allocate_payment_only_donation(self, test_user, test_project):
        """Test avec seulement un don (pas de tip)"""
        donation_amount = Decimal('100.00')
        tip_amount = Decimal('0.00')
        total_stripe_fee = Decimal('1.83')
        
        result = allocate_payment_to_ledgers(
            user=test_user,
            donation_amount=donation_amount,
            tip_amount=tip_amount,
            total_stripe_fee=total_stripe_fee,
            project=test_project
        )
        
        assert result['donation'] is not None
        assert result['tip'] is None
        
        # Vérifier que tous les frais sont alloués à la donation
        donation_data = result['donation']
        assert donation_data['stripe_fee'] == total_stripe_fee
    
    def test_allocate_payment_idempotency(self, test_user, test_project):
        """Test de l'idempotence (éviter double dépense)"""
        import uuid
        
        donation_amount = Decimal('100.00')
        tip_amount = Decimal('5.00')
        total_stripe_fee = Decimal('1.83')
        idempotency_key = uuid.uuid4()
        
        # Première allocation
        result1 = allocate_payment_to_ledgers(
            user=test_user,
            donation_amount=donation_amount,
            tip_amount=tip_amount,
            total_stripe_fee=total_stripe_fee,
            project=test_project,
            idempotency_key=idempotency_key
        )
        
        # Vérifier que les transactions ont été créées
        assert result1['donation'] is not None
        assert result1['tip'] is not None
        
        # Tentative de double allocation (devrait échouer)
        # La fonction _lock_user_wallet dans finance/services.py vérifie l'idempotence
        # mais allocate_payment_to_ledgers ne l'appelle pas directement
        # On vérifie plutôt que les transactions avec la même idempotency_key ne peuvent pas être recréées
        with pytest.raises((ValidationError, Exception)):  # Peut être ValidationError ou IntegrityError
            allocate_payment_to_ledgers(
                user=test_user,
                donation_amount=donation_amount,
                tip_amount=tip_amount,
                total_stripe_fee=total_stripe_fee,
                project=test_project,
                idempotency_key=idempotency_key
            )


@pytest.mark.django_db
class TestExtractStripeFeeFromWebhook:
    """Tests pour extract_stripe_fee_from_webhook"""
    
    def test_extract_fee_from_expanded_webhook(self):
        """Test avec balance_transaction expandé"""
        webhook_event_data = {
            'data': {
                'object': {
                    'charges': {
                        'data': [
                            {
                                'balance_transaction': {
                                    'fee': 183  # 1.83€ en centimes
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        fee = extract_stripe_fee_from_webhook(webhook_event_data)
        assert fee == Decimal('1.83')
    
    def test_extract_fee_missing_charge(self):
        """Test avec charge manquante"""
        webhook_event_data = {
            'data': {
                'object': {
                    'charges': {
                        'data': []
                    }
                }
            }
        }
        
        with pytest.raises(ValidationError, match="Aucune charge trouvée"):
            extract_stripe_fee_from_webhook(webhook_event_data)
    
    def test_extract_fee_missing_balance_transaction(self):
        """Test avec balance_transaction manquant"""
        webhook_event_data = {
            'data': {
                'object': {
                    'charges': {
                        'data': [
                            {
                                'balance_transaction': None
                            }
                        ]
                    }
                }
            }
        }
        
        with pytest.raises(ValidationError, match="balance_transaction manquant"):
            extract_stripe_fee_from_webhook(webhook_event_data)

