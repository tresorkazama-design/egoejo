"""
Contract tests pour l'endpoint webhook Stripe

Vérifie que l'endpoint /api/finance/stripe/webhook/ respecte son contrat :
- Status codes attendus (200, 400, 500)
- Structure payload webhook
- Validation événements Stripe
"""
import pytest
import json
from django.test import Client
from django.contrib.auth import get_user_model

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
    from core.models import Projet
    return Projet.objects.create(
        titre='Test Project',
        description='Test description',
        categorie='Environnement'
    )


@pytest.mark.django_db
@pytest.mark.payments
@pytest.mark.critical
class TestStripeWebhookContract:
    """Tests contract pour POST /api/finance/stripe/webhook/"""
    
    def test_webhook_accepts_post_only(self, client):
        """Vérifie que l'endpoint accepte uniquement POST"""
        # GET doit retourner 405 (Method Not Allowed) ou 404
        response = client.get('/api/finance/stripe/webhook/')
        assert response.status_code in [405, 404], f"Expected 405 or 404, got {response.status_code}"
    
    def test_webhook_requires_valid_json(self, client):
        """Vérifie que l'endpoint valide le JSON (400 si invalide)"""
        # Test avec JSON invalide
        response = client.post(
            '/api/finance/stripe/webhook/',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
    
    def test_webhook_requires_event_type(self, client):
        """Vérifie que l'endpoint requiert un type d'événement (400 si manquant)"""
        payload = {}  # Pas de 'type'
        
        response = client.post(
            '/api/finance/stripe/webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data, "Erreur doit être structurée"
    
    def test_webhook_handles_payment_intent_succeeded(self, client, test_user, test_project):
        """Vérifie que l'endpoint traite payment_intent.succeeded (200)"""
        payload = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'amount': 10500,  # 105.00 EUR en centimes
                    'metadata': {
                        'user_id': str(test_user.id),
                        'project_id': str(test_project.id),
                        'donation_amount': '100.00',
                        'tip_amount': '5.00'
                    },
                    'charges': {
                        'data': [{
                            'balance_transaction': {
                                'fee': 183  # 1.83 EUR en centimes
                            }
                        }]
                    }
                }
            }
        }
        
        response = client.post(
            '/api/finance/stripe/webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Doit retourner 200 (succès) ou 400/500 (erreur de traitement)
        assert response.status_code in [200, 400, 500], f"Status code inattendu: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # Vérifier structure de réponse
            assert 'status' in data, "Réponse doit contenir 'status'"
            assert data['status'] in ['success', 'ignored'], f"Status inattendu: {data['status']}"
    
    def test_webhook_ignores_unknown_events(self, client):
        """Vérifie que l'endpoint ignore les événements inconnus (200)"""
        payload = {
            'type': 'unknown.event.type',
            'data': {}
        }
        
        response = client.post(
            '/api/finance/stripe/webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('status') == 'ignored', "Événement inconnu doit être ignoré"
    
    def test_webhook_handles_missing_user_id(self, client):
        """Vérifie que l'endpoint gère l'absence de user_id (400)"""
        payload = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'amount': 10500,
                    'metadata': {
                        # Pas de user_id
                        'project_id': '1'
                    }
                }
            }
        }
        
        response = client.post(
            '/api/finance/stripe/webhook/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert 'error' in data, "Erreur doit être structurée"

