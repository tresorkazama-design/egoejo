"""
Tests complets pour la répartition proportionnelle des frais Stripe via Webhook.

Prouve par le code que : Net Projet + Net Asso + Frais Stripe = Total Payé

Scénarios testés :
1. Cas Standard (Don + Tip)
2. Arrondi Vicieux (Penny Splitting)
3. Don Pur (Sans Tip)
"""

from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
import uuid
import pytest

from finance.models import WalletTransaction, UserWallet
from core.models import Projet

User = get_user_model()


@pytest.mark.payments
@pytest.mark.critical
@pytest.mark.django_db
class StripeWebhookSegregationTest(APITestCase):
    """
    Tests d'intégration pour la répartition proportionnelle des frais Stripe
    via l'endpoint webhook Stripe.
    
    Utilise APITestCase pour tester l'endpoint webhook complet.
    """
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Créer un utilisateur de test
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un projet de test
        self.test_project = Projet.objects.create(
            titre='Test Project',
            description='Test Description',
            funding_type='DONATION'
        )
        
        # URL de l'endpoint webhook
        self.webhook_url = reverse('stripe-webhook')
    
    def _create_stripe_webhook_payload(
        self,
        user_id: int,
        project_id: int,
        amount_cents: int,
        donation_amount: str,
        tip_amount: str,
        fee_cents: int,
        payment_intent_id: str = None
    ) -> dict:
        """
        Crée un payload de webhook Stripe standardisé.
        
        Args:
            user_id: ID de l'utilisateur
            project_id: ID du projet
            amount_cents: Montant total en centimes
            donation_amount: Montant du don en euros (string)
            tip_amount: Montant du tip en euros (string)
            fee_cents: Frais Stripe en centimes
            payment_intent_id: ID du payment intent (optionnel)
        
        Returns:
            dict: Payload de webhook Stripe
        """
        if payment_intent_id is None:
            payment_intent_id = f"pi_test_{uuid.uuid4().hex[:8]}"
        
        return {
            "id": f"evt_test_{uuid.uuid4().hex[:8]}",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": payment_intent_id,
                    "amount": amount_cents,
                    "currency": "eur",
                    "metadata": {
                        "donation_amount": donation_amount,
                        "tip_amount": tip_amount,
                        "user_id": str(user_id),
                        "project_id": str(project_id),
                        "target_type": "project"
                    },
                    "charges": {
                        "data": [
                            {
                                "id": f"ch_test_{uuid.uuid4().hex[:8]}",
                                "balance_transaction": {
                                    "fee": fee_cents  # Frais en centimes
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def _assert_integrity_check(self, user, total_paid: Decimal):
        """
        Vérifie l'intégrité : Net Projet + Net Asso + Frais Stripe = Total Payé
        
        Args:
            user: Utilisateur
            total_paid: Montant total payé (en euros)
        """
        # Récupérer toutes les transactions créées pour cet utilisateur
        transactions = WalletTransaction.objects.filter(wallet__user=user).order_by('-created_at')
        
        # Calculer les sommes
        net_projet = Decimal('0')
        net_asso = Decimal('0')
        total_fees = Decimal('0')
        
        for tx in transactions:
            if tx.transaction_type == 'PLEDGE_DONATION':
                net_projet += tx.amount  # amount = net
                total_fees += tx.stripe_fee or Decimal('0')
            elif tx.transaction_type == 'DEPOSIT' and tx.related_project is None:
                # Tip (OPERATING)
                net_asso += tx.amount  # amount = net
                total_fees += tx.stripe_fee or Decimal('0')
        
        # Vérifier l'intégrité
        calculated_total = net_projet + net_asso + total_fees
        cents = Decimal('0.01')
        
        self.assertAlmostEqual(
            float(calculated_total),
            float(total_paid),
            places=2,
            msg=f"Intégrité violée: Net Projet ({net_projet}) + Net Asso ({net_asso}) + "
                f"Frais ({total_fees}) = {calculated_total} ≠ Total Payé ({total_paid})"
        )
    
    def test_scenario_1_standard_case_don_plus_tip(self):
        """
        SCÉNARIO 1 : Le Cas Standard (Don + Tip)
        
        Input :
        - Montant Total : 105.00 € (10500 cents)
        - Metadata : tip_amount='500', donation_amount='10000', target_type='project'
        - Mock Fee : 183 cents (1.83€)
        
        Assertions :
        1. 2 entrées créées
        2. PROJECT_ESCROW : Gross=100.00, Fee=1.74, Net=98.26
        3. OPERATING : Gross=5.00, Fee=0.09, Net=4.91
        4. Intégrité : Sum(Net) + Sum(Fee) == 105.00
        """
        # Pas besoin de mock car balance_transaction est expandé dans le payload
        
        # Créer le payload webhook
        payload = self._create_stripe_webhook_payload(
            user_id=self.test_user.id,
            project_id=self.test_project.id,
            amount_cents=10500,  # 105.00 €
            donation_amount='100.00',
            tip_amount='5.00',
            fee_cents=183  # 1.83 €
        )
        
        # Envoyer la requête POST au webhook
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        
        # Vérifier qu'il y a 2 transactions créées
        transactions = WalletTransaction.objects.filter(wallet__user=self.test_user)
        self.assertEqual(transactions.count(), 2, "Il doit y avoir exactement 2 transactions")
        
        # Récupérer les transactions
        donation_tx = transactions.filter(transaction_type='PLEDGE_DONATION').first()
        tip_tx = transactions.filter(transaction_type='DEPOSIT', related_project__isnull=True).first()
        
        # Assertions pour PROJECT_ESCROW (Donation)
        self.assertIsNotNone(donation_tx, "Transaction donation doit exister")
        self.assertEqual(donation_tx.amount_gross, Decimal('100.00'), "Gross donation doit être 100.00")
        self.assertAlmostEqual(
            float(donation_tx.stripe_fee),
            float(Decimal('1.74')),
            places=2,
            msg=f"Fee donation doit être 1.74 (calcul: 1.83 * 100/105), obtenu: {donation_tx.stripe_fee}"
        )
        self.assertAlmostEqual(
            float(donation_tx.amount),
            float(Decimal('98.26')),
            places=2,
            msg=f"Net donation doit être 98.26 (100.00 - 1.74), obtenu: {donation_tx.amount}"
        )
        self.assertEqual(donation_tx.related_project, self.test_project)
        
        # Assertions pour OPERATING (Tip)
        self.assertIsNotNone(tip_tx, "Transaction tip doit exister")
        self.assertEqual(tip_tx.amount_gross, Decimal('5.00'), "Gross tip doit être 5.00")
        self.assertAlmostEqual(
            float(tip_tx.stripe_fee),
            float(Decimal('0.09')),
            places=2,
            msg=f"Fee tip doit être 0.09 (calcul: 1.83 * 5/105), obtenu: {tip_tx.stripe_fee}"
        )
        self.assertAlmostEqual(
            float(tip_tx.amount),
            float(Decimal('4.91')),
            places=2,
            msg=f"Net tip doit être 4.91 (5.00 - 0.09), obtenu: {tip_tx.amount}"
        )
        self.assertIsNone(tip_tx.related_project, "Tip ne doit pas être lié à un projet")
        
        # Check d'Intégrité : Sum(Net) + Sum(Fee) == 105.00
        net_sum = donation_tx.amount + tip_tx.amount
        fee_sum = donation_tx.stripe_fee + tip_tx.stripe_fee
        total_calculated = net_sum + fee_sum
        
        self.assertAlmostEqual(
            float(total_calculated),
            float(Decimal('105.00')),
            places=2,
            msg=f"Intégrité: Net ({net_sum}) + Fees ({fee_sum}) = {total_calculated} ≠ 105.00"
        )
        
        # Vérification globale d'intégrité
        self._assert_integrity_check(self.test_user, Decimal('105.00'))
    
    def test_scenario_2_penny_splitting_rounding(self):
        """
        SCÉNARIO 2 : L'Arrondi Vicieux (Penny Splitting)
        
        Input :
        - Montant : 33.33 € (Don 33.00 + Tip 0.33)
        - Mock Fee : 0.25 € (25 cents)
        
        Assertions :
        - Le système ne perd pas 1 centime dans la division
        - Fee_Part_1 + Fee_Part_2 == 0.25 exactement
        """
        # Pas besoin de mock car balance_transaction est expandé dans le payload
        
        # Créer le payload webhook
        payload = self._create_stripe_webhook_payload(
            user_id=self.test_user.id,
            project_id=self.test_project.id,
            amount_cents=3333,  # 33.33 €
            donation_amount='33.00',
            tip_amount='0.33',
            fee_cents=25  # 0.25 €
        )
        
        # Envoyer la requête POST au webhook
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Récupérer les transactions
        transactions = WalletTransaction.objects.filter(wallet__user=self.test_user)
        self.assertEqual(transactions.count(), 2, "Il doit y avoir exactement 2 transactions")
        
        donation_tx = transactions.filter(transaction_type='PLEDGE_DONATION').first()
        tip_tx = transactions.filter(transaction_type='DEPOSIT', related_project__isnull=True).first()
        
        # Vérifier que les frais sont correctement répartis
        fee_donation = donation_tx.stripe_fee
        fee_tip = tip_tx.stripe_fee
        total_fees = fee_donation + fee_tip
        
        # Assertion critique : les frais doivent totaliser exactement 0.25€
        self.assertEqual(
            total_fees,
            Decimal('0.25'),
            f"Frais totaux doivent être 0.25€ exactement, obtenu: {total_fees} "
            f"(Donation: {fee_donation}, Tip: {fee_tip})"
        )
        
        # Vérifier que les montants nets sont cohérents
        donation_net = donation_tx.amount
        tip_net = tip_tx.amount
        total_net = donation_net + tip_net
        total_calculated = total_net + total_fees
        
        # Vérifier l'intégrité : Net + Fees = Total Payé
        self.assertAlmostEqual(
            float(total_calculated),
            float(Decimal('33.33')),
            places=2,
            msg=f"Intégrité: Net ({total_net}) + Fees ({total_fees}) = {total_calculated} ≠ 33.33"
        )
        
        # Vérification globale d'intégrité
        self._assert_integrity_check(self.test_user, Decimal('33.33'))
        
        # Vérifier que les ratios sont corrects
        # Ratio donation : 33.00 / 33.33 = 0.9901
        # Ratio tip : 0.33 / 33.33 = 0.0099
        expected_fee_donation = Decimal('0.25') * (Decimal('33.00') / Decimal('33.33'))
        expected_fee_tip = Decimal('0.25') * (Decimal('0.33') / Decimal('33.33'))
        
        # Les frais doivent être proches des valeurs attendues (arrondi)
        self.assertAlmostEqual(float(fee_donation), float(expected_fee_donation), places=2)
        self.assertAlmostEqual(float(fee_tip), float(expected_fee_tip), places=2)
    
    def test_scenario_3_pure_donation_no_tip(self):
        """
        SCÉNARIO 3 : Don Pur (Sans Tip)
        
        Input : 100.00 € (Tip 0)
        
        Assertions :
        - 1 seule entrée PROJECT_ESCROW
        - OPERATING doit être vide ou 0
        - 100% des frais sont assignés au Projet
        """
        # Pas besoin de mock car balance_transaction est expandé dans le payload
        
        # Créer le payload webhook (sans tip)
        payload = self._create_stripe_webhook_payload(
            user_id=self.test_user.id,
            project_id=self.test_project.id,
            amount_cents=10000,  # 100.00 €
            donation_amount='100.00',
            tip_amount='0.00',
            fee_cents=183  # 1.83 € (exemple)
        )
        
        # Envoyer la requête POST au webhook
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        
        # Vérifier qu'il n'y a qu'1 transaction créée (donation uniquement)
        transactions = WalletTransaction.objects.filter(wallet__user=self.test_user)
        self.assertEqual(transactions.count(), 1, "Il doit y avoir exactement 1 transaction (donation)")
        
        # Récupérer la transaction donation
        donation_tx = transactions.filter(transaction_type='PLEDGE_DONATION').first()
        tip_tx = transactions.filter(transaction_type='DEPOSIT', related_project__isnull=True).first()
        
        # Assertions pour PROJECT_ESCROW
        self.assertIsNotNone(donation_tx, "Transaction donation doit exister")
        self.assertEqual(donation_tx.amount_gross, Decimal('100.00'), "Gross donation doit être 100.00")
        self.assertEqual(donation_tx.stripe_fee, Decimal('1.83'), "100% des frais doivent être assignés au projet")
        self.assertEqual(donation_tx.amount, Decimal('98.17'), "Net donation doit être 98.17 (100.00 - 1.83)")
        self.assertEqual(donation_tx.related_project, self.test_project)
        
        # OPERATING doit être vide (pas de tip)
        self.assertIsNone(tip_tx, "Il ne doit pas y avoir de transaction tip")
        
        # Vérifier dans la réponse JSON que tip est None
        self.assertIsNone(response_data.get('tip'), "Tip doit être None dans la réponse")
        
        # Vérification globale d'intégrité
        self._assert_integrity_check(self.test_user, Decimal('100.00'))
        
        # Vérifier que les frais totaux = frais donation (100% assignés au projet)
        total_fees = donation_tx.stripe_fee
        self.assertEqual(total_fees, Decimal('1.83'), "Tous les frais doivent être assignés au projet")
    
    def test_integrity_edge_case_large_amounts(self):
        """
        Test d'intégrité avec des montants importants.
        
        Vérifie que le système gère correctement les grands montants.
        """
        # Pas besoin de mock car balance_transaction est expandé dans le payload
        
        # Montant important : 10 000€ (1000€ donation + 9000€ tip)
        payload = self._create_stripe_webhook_payload(
            user_id=self.test_user.id,
            project_id=self.test_project.id,
            amount_cents=1000000,  # 10 000.00 €
            donation_amount='1000.00',
            tip_amount='9000.00',
            fee_cents=2900  # 29.00 € (0.29%)
        )
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification globale d'intégrité
        self._assert_integrity_check(self.test_user, Decimal('10000.00'))
        
        # Vérifier que les ratios sont corrects
        transactions = WalletTransaction.objects.filter(wallet__user=self.test_user)
        donation_tx = transactions.filter(transaction_type='PLEDGE_DONATION').first()
        tip_tx = transactions.filter(transaction_type='DEPOSIT', related_project__isnull=True).first()
        
        # Ratio donation : 10%, Ratio tip : 90%
        # Fee donation : 29.00 * 0.10 = 2.90
        # Fee tip : 29.00 * 0.90 = 26.10
        expected_fee_donation = Decimal('29.00') * (Decimal('1000.00') / Decimal('10000.00'))
        expected_fee_tip = Decimal('29.00') * (Decimal('9000.00') / Decimal('10000.00'))
        
        self.assertAlmostEqual(float(donation_tx.stripe_fee), float(expected_fee_donation), places=2)
        self.assertAlmostEqual(float(tip_tx.stripe_fee), float(expected_fee_tip), places=2)
    
    def test_integrity_edge_case_small_amounts(self):
        """
        Test d'intégrité avec des montants très petits.
        
        Vérifie que le système gère correctement les petits montants (arrondis).
        """
        # Pas besoin de mock car balance_transaction est expandé dans le payload
        
        # Montant très petit : 1.01€ (1.00€ donation + 0.01€ tip)
        payload = self._create_stripe_webhook_payload(
            user_id=self.test_user.id,
            project_id=self.test_project.id,
            amount_cents=101,  # 1.01 €
            donation_amount='1.00',
            tip_amount='0.01',
            fee_cents=2  # 0.02 €
        )
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification globale d'intégrité
        self._assert_integrity_check(self.test_user, Decimal('1.01'))
        
        transactions = WalletTransaction.objects.filter(wallet__user=self.test_user)
        donation_tx = transactions.filter(transaction_type='PLEDGE_DONATION').first()
        tip_tx = transactions.filter(transaction_type='DEPOSIT', related_project__isnull=True).first()
        
        # Vérifier que les frais totalisent exactement 0.02€
        total_fees = donation_tx.stripe_fee + tip_tx.stripe_fee
        self.assertEqual(total_fees, Decimal('0.02'), "Frais totaux doivent être 0.02€ exactement")
