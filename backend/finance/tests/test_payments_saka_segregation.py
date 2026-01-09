"""
Tests de conformité SAKA/EUR pour les paiements.

Vérifie que :
- Aucun chemin de paiement ne touche SAKA
- Aucune mutation de SakaWallet lors d'un paiement EUR
- Aucune référence SAKA dans les services de paiement
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import override_settings
from finance.models import WalletTransaction, UserWallet
from finance.ledger_services.ledger import process_stripe_payment_webhook
from finance.ledger_services.helloasso_ledger import process_helloasso_payment_webhook
from core.models import Projet

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestPaymentSakaSegregation:
    """Tests que les paiements EUR ne touchent jamais SAKA"""
    
    @pytest.fixture
    def test_user(self, db):
        """Utilisateur de test"""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def test_project(self, db):
        """Projet de test"""
        return Projet.objects.create(
            titre='Test Project',
            description='Test description',
            categorie='Environnement',
            funding_type='DONATION'
        )
    
    def test_stripe_webhook_does_not_touch_saka(self, test_user, test_project):
        """Vérifie qu'un webhook Stripe ne modifie pas SAKA"""
        # Vérifier l'état initial SAKA (si le modèle existe)
        try:
            from core.models import SakaWallet
            initial_saka_balance = None
            saka_wallet = None
            try:
                saka_wallet = SakaWallet.objects.get(user=test_user)
                initial_saka_balance = saka_wallet.balance
            except SakaWallet.DoesNotExist:
                pass  # Pas de wallet SAKA, c'est OK
        except ImportError:
            # Modèle SAKA n'existe pas encore, c'est OK
            saka_wallet = None
            initial_saka_balance = None
        
        # Créer un webhook Stripe
        webhook_event = {
            'id': 'evt_test_123',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'amount': 10000,  # 100.00 EUR
                    'currency': 'eur',
                    'metadata': {
                        'user_id': str(test_user.id),
                        'project_id': str(test_project.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    },
                    'charges': {
                        'data': [{
                            'id': 'ch_test_123',
                            'balance_transaction': {
                                'fee': 183  # 1.83 EUR
                            }
                        }]
                    }
                }
            }
        }
        
        # Traiter le webhook
        result = process_stripe_payment_webhook(
            webhook_event_data=webhook_event,
            user=test_user,
            project=test_project
        )
        
        # Vérifier que le webhook a réussi
        assert result['status'] == 'success'
        
        # Vérifier qu'une transaction EUR a été créée
        transactions = WalletTransaction.objects.filter(wallet__user=test_user)
        assert transactions.count() > 0, "Une transaction EUR doit être créée"
        
        # Vérifier que SAKA n'a pas été modifié
        if saka_wallet is not None:
            saka_wallet.refresh_from_db()
            assert saka_wallet.balance == initial_saka_balance, \
                "VIOLATION SAKA/EUR: Le solde SAKA a été modifié lors d'un paiement EUR"
        
        # Vérifier qu'aucune transaction SAKA n'a été créée
        try:
            from core.models import SakaTransaction
            saka_transactions = SakaTransaction.objects.filter(user=test_user)
            assert saka_transactions.count() == 0, \
                "VIOLATION SAKA/EUR: Des transactions SAKA ont été créées lors d'un paiement EUR"
        except ImportError:
            pass  # Modèle SAKA n'existe pas encore
    
    def test_helloasso_webhook_does_not_touch_saka(self, test_user, test_project):
        """Vérifie qu'un webhook HelloAsso ne modifie pas SAKA"""
        # Vérifier l'état initial SAKA
        try:
            from core.models import SakaWallet
            initial_saka_balance = None
            saka_wallet = None
            try:
                saka_wallet = SakaWallet.objects.get(user=test_user)
                initial_saka_balance = saka_wallet.balance
            except SakaWallet.DoesNotExist:
                pass
        except ImportError:
            saka_wallet = None
            initial_saka_balance = None
        
        # Créer un webhook HelloAsso
        webhook_event = {
            'eventType': 'Payment',
            'eventId': 'evt_test_123',
            'data': {
                'payment': {
                    'id': 'payment_test_123',
                    'amount': 10000,  # 100.00 EUR
                    'fee': 80,  # 0.80 EUR
                    'metadata': {
                        'user_id': str(test_user.id),
                        'project_id': str(test_project.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    }
                }
            }
        }
        
        # Traiter le webhook
        result = process_helloasso_payment_webhook(
            webhook_event_data=webhook_event,
            user=test_user,
            project=test_project
        )
        
        # Vérifier que le webhook a réussi
        assert result['status'] == 'success'
        
        # Vérifier qu'une transaction EUR a été créée
        transactions = WalletTransaction.objects.filter(wallet__user=test_user)
        assert transactions.count() > 0, "Une transaction EUR doit être créée"
        
        # Vérifier que SAKA n'a pas été modifié
        if saka_wallet is not None:
            saka_wallet.refresh_from_db()
            assert saka_wallet.balance == initial_saka_balance, \
                "VIOLATION SAKA/EUR: Le solde SAKA a été modifié lors d'un paiement EUR"
    
    def test_payment_services_do_not_import_saka(self):
        """Vérifie que les services de paiement n'importent pas SAKA"""
        import inspect
        import finance.ledger_services.ledger as ledger_module
        import finance.ledger_services.helloasso_ledger as helloasso_ledger_module
        
        # Vérifier les imports du module ledger
        ledger_source = inspect.getsource(ledger_module)
        assert 'SakaWallet' not in ledger_source, \
            "VIOLATION SAKA/EUR: Le module ledger importe SakaWallet"
        assert 'SakaTransaction' not in ledger_source, \
            "VIOLATION SAKA/EUR: Le module ledger importe SakaTransaction"
        assert 'saka' not in ledger_source.lower() or 'saka' in '# SAKA' or 'saka' in '"""', \
            "VIOLATION SAKA/EUR: Le module ledger contient des références SAKA"
        
        # Vérifier les imports du module helloasso_ledger
        helloasso_source = inspect.getsource(helloasso_ledger_module)
        assert 'SakaWallet' not in helloasso_source, \
            "VIOLATION SAKA/EUR: Le module helloasso_ledger importe SakaWallet"
        assert 'SakaTransaction' not in helloasso_source, \
            "VIOLATION SAKA/EUR: Le module helloasso_ledger importe SakaTransaction"
    
    def test_wallet_transaction_has_no_saka_reference(self, test_user, test_project):
        """Vérifie qu'une WalletTransaction n'a pas de référence SAKA"""
        # Créer une transaction EUR
        wallet, _ = UserWallet.objects.get_or_create(user=test_user)
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            amount=Decimal('100.00'),
            amount_gross=Decimal('100.00'),
            transaction_type='PLEDGE_DONATION',
            related_project=test_project
        )
        
        # Vérifier que la transaction n'a pas de champ SAKA
        transaction_fields = [f.name for f in transaction._meta.get_fields()]
        saka_fields = [f for f in transaction_fields if 'saka' in f.lower()]
        assert len(saka_fields) == 0, \
            f"VIOLATION SAKA/EUR: WalletTransaction contient des champs SAKA: {saka_fields}"

