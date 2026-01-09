"""
Contract tests pour les endpoints HelloAsso (mode simulé).

Vérifie que les endpoints respectent leur contrat :
- Status codes attendus (200, 400, 401, 404, 500)
- Structure payload
- Validation événements HelloAsso
- Idempotence
- Sécurité (anon forbidden, secrets missing)
"""
import pytest
import json
import hmac
import hashlib
from django.test import Client
from django.contrib.auth import get_user_model
from django.test import override_settings
from decimal import Decimal

from finance.models import WalletTransaction, UserWallet
from core.models import Projet

User = get_user_model()


@pytest.fixture
def test_user(db):
    """Utilisateur de test"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_project(db):
    """Projet de test"""
    return Projet.objects.create(
        titre='Test Project',
        description='Test description',
        categorie='Environnement',
        funding_type='DONATION'
    )


@pytest.fixture
def authenticated_client(test_user):
    """Client authentifié"""
    client = Client()
    client.force_login(test_user)
    return client


def _create_helloasso_signature(payload: bytes, secret: str) -> str:
    """Crée une signature HelloAsso pour les tests"""
    return hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestHelloAssoCheckoutContract:
    """Tests contract pour POST /api/payments/helloasso/start/"""
    
    def test_checkout_requires_authentication(self, client):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        response = client.post(
            '/api/payments/helloasso/start/',
            data=json.dumps({'amount': '100.00'}),
            content_type='application/json'
        )
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_checkout_requires_amount(self, authenticated_client):
        """Vérifie que l'endpoint requiert amount (400 si manquant)"""
        response = authenticated_client.post(
            '/api/payments/helloasso/start/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data, "Erreur doit être structurée"
        assert 'amount' in data['error'].lower(), "Erreur doit mentionner 'amount'"
    
    def test_checkout_validates_amount_format(self, authenticated_client):
        """Vérifie que l'endpoint valide le format amount (400 si invalide)"""
        response = authenticated_client.post(
            '/api/payments/helloasso/start/',
            data=json.dumps({'amount': 'invalid'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data
    
    def test_checkout_validates_amount_positive(self, authenticated_client):
        """Vérifie que l'endpoint valide amount > 0 (400 si <= 0)"""
        response = authenticated_client.post(
            '/api/payments/helloasso/start/',
            data=json.dumps({'amount': '0.00'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data
    
    def test_checkout_creates_payment_form(self, authenticated_client, test_project):
        """Vérifie que l'endpoint crée un formulaire de paiement (200)"""
        response = authenticated_client.post(
            '/api/payments/helloasso/start/',
            data=json.dumps({
                'amount': '100.00',
                'project_id': test_project.id
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'success' in data, "Réponse doit contenir 'success'"
        assert data['success'] is True
        assert 'payment_form_url' in data, "Réponse doit contenir 'payment_form_url'"
        assert 'payment_form_id' in data, "Réponse doit contenir 'payment_form_id'"
        assert 'expires_at' in data, "Réponse doit contenir 'expires_at'"
    
    def test_checkout_handles_missing_project(self, authenticated_client):
        """Vérifie que l'endpoint gère un projet introuvable (404)"""
        response = authenticated_client.post(
            '/api/payments/helloasso/start/',
            data=json.dumps({
                'amount': '100.00',
                'project_id': 99999  # Projet inexistant
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert 'error' in data


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestHelloAssoWebhookContract:
    """Tests contract pour POST /api/payments/helloasso/webhook/"""
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_accepts_post_only(self, client):
        """Vérifie que l'endpoint accepte uniquement POST"""
        response = client.get('/api/payments/helloasso/webhook/')
        assert response.status_code in [405, 404], f"Expected 405 or 404, got {response.status_code}"
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_requires_valid_json(self, client):
        """Vérifie que l'endpoint valide le JSON (400 si invalide)"""
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_requires_event_type(self, client):
        """Vérifie que l'endpoint requiert un type d'événement (400 si manquant)"""
        payload = {}  # Pas de 'eventType'
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = _create_helloasso_signature(payload_bytes, 'test_webhook_secret')
        
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_validates_signature(self, client, test_user):
        """Vérifie que l'endpoint valide la signature (401 si invalide)"""
        payload = {
            'eventType': 'Payment',
            'eventId': 'evt_test_123',
            'data': {
                'payment': {
                    'id': 'payment_test_123',
                    'amount': 10000,
                    'metadata': {
                        'user_id': str(test_user.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    }
                }
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        invalid_signature = 'invalid_signature'
        
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=invalid_signature
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert 'error' in data
        assert 'signature' in data['error'].lower() or 'invalid' in data['error'].lower()
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_handles_payment_event(self, client, test_user, test_project):
        """Vérifie que l'endpoint traite Payment (200)"""
        payload = {
            'eventType': 'Payment',
            'eventId': 'evt_test_123',
            'data': {
                'payment': {
                    'id': 'payment_test_123',
                    'amount': 10000,  # 100.00 EUR en centimes
                    'fee': 80,  # 0.80 EUR en centimes
                    'metadata': {
                        'user_id': str(test_user.id),
                        'project_id': str(test_project.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    }
                }
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = _create_helloasso_signature(payload_bytes, 'test_webhook_secret')
        
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'status' in data, "Réponse doit contenir 'status'"
        assert data['status'] == 'success'
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_ignores_unknown_events(self, client):
        """Vérifie que l'endpoint ignore les événements inconnus (200)"""
        payload = {
            'eventType': 'UnknownEvent',
            'eventId': 'evt_test_123',
            'data': {}
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = _create_helloasso_signature(payload_bytes, 'test_webhook_secret')
        
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('status') == 'ignored', "Événement inconnu doit être ignoré"
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_handles_missing_user_id(self, client):
        """Vérifie que l'endpoint gère l'absence de user_id (400)"""
        payload = {
            'eventType': 'Payment',
            'eventId': 'evt_test_123',
            'data': {
                'payment': {
                    'id': 'payment_test_123',
                    'amount': 10000,
                    'metadata': {
                        # Pas de user_id
                    }
                }
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = _create_helloasso_signature(payload_bytes, 'test_webhook_secret')
        
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data
        assert 'user_id' in data['error'].lower()


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestHelloAssoIdempotence:
    """Tests d'idempotence pour HelloAsso webhook"""
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_idempotence_replay_event(self, client, test_user, test_project):
        """Vérifie que replay event.id est no-op (idempotence)"""
        payload = {
            'eventType': 'Payment',
            'eventId': 'evt_test_idempotence',
            'data': {
                'payment': {
                    'id': 'payment_test_idempotence',
                    'amount': 10000,
                    'fee': 80,
                    'metadata': {
                        'user_id': str(test_user.id),
                        'project_id': str(test_project.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    }
                }
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = _create_helloasso_signature(payload_bytes, 'test_webhook_secret')
        
        # Premier appel
        response1 = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response1.status_code == 200, f"Premier appel doit réussir, got {response1.status_code}"
        data1 = response1.json()
        assert data1['status'] == 'success'
        
        # Compter les transactions créées
        transactions_count_1 = WalletTransaction.objects.filter(wallet__user=test_user).count()
        assert transactions_count_1 > 0, "Au moins une transaction doit être créée"
        
        # Replay du même événement
        response2 = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response2.status_code == 200, f"Replay doit retourner 200, got {response2.status_code}"
        data2 = response2.json()
        assert data2['status'] == 'success'
        assert 'message' in data2, "Message doit indiquer que l'événement est déjà traité"
        assert 'déjà traité' in data2['message'].lower() or 'already' in data2['message'].lower()
        
        # Vérifier qu'aucune nouvelle transaction n'a été créée
        transactions_count_2 = WalletTransaction.objects.filter(wallet__user=test_user).count()
        assert transactions_count_2 == transactions_count_1, "Aucune nouvelle transaction ne doit être créée (idempotence)"


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestHelloAssoSecurity:
    """Tests de sécurité pour HelloAsso"""
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='',  # Secret manquant
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_handles_missing_secret(self, client, test_user):
        """Vérifie que l'endpoint gère l'absence de secret (accepte sans signature en dev)"""
        payload = {
            'eventType': 'Payment',
            'eventId': 'evt_test_123',
            'data': {
                'payment': {
                    'id': 'payment_test_123',
                    'amount': 10000,
                    'metadata': {
                        'user_id': str(test_user.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    }
                }
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Sans signature (secret manquant)
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json'
        )
        
        # En mode dev, on accepte sans signature si secret manquant
        assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestHelloAssoLedger:
    """Tests ledger pour HelloAsso (net_amount, fees stockés)"""
    
    @override_settings(
        HELLOASSO_WEBHOOK_SECRET='test_webhook_secret',
        HELLOASSO_SIMULATED_MODE=True
    )
    def test_webhook_stores_net_amount_and_fees(self, client, test_user, test_project):
        """Vérifie que l'endpoint stocke net_amount et fees correctement"""
        payload = {
            'eventType': 'Payment',
            'eventId': 'evt_test_ledger',
            'data': {
                'payment': {
                    'id': 'payment_test_ledger',
                    'amount': 10000,  # 100.00 EUR en centimes
                    'fee': 80,  # 0.80 EUR en centimes
                    'metadata': {
                        'user_id': str(test_user.id),
                        'project_id': str(test_project.id),
                        'donation_amount': '100.00',
                        'tip_amount': '0.00'
                    }
                }
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        signature = _create_helloasso_signature(payload_bytes, 'test_webhook_secret')
        
        response = client.post(
            '/api/payments/helloasso/webhook/',
            data=payload_bytes,
            content_type='application/json',
            HTTP_X_HELLOASSO_SIGNATURE=signature
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Vérifier que la transaction est créée avec les bons montants
        transaction = WalletTransaction.objects.filter(
            wallet__user=test_user,
            transaction_type='PLEDGE_DONATION'
        ).first()
        
        assert transaction is not None, "Transaction doit être créée"
        assert transaction.amount_gross == Decimal('100.00'), "amount_gross doit être 100.00"
        assert transaction.stripe_fee == Decimal('0.80'), "fees doivent être 0.80"
        assert transaction.amount == Decimal('99.20'), "amount_net doit être 99.20 (100.00 - 0.80)"
        assert transaction.related_project == test_project, "Transaction doit être liée au projet"

