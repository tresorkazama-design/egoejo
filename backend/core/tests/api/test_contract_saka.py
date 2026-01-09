"""
Contract tests pour les endpoints SAKA critiques

Vérifie que les endpoints SAKA respectent leur contrat :
- /api/saka/silo/ (GET)
- /api/saka/compost-preview/ (GET)
- /api/saka/grant/ (POST)
- /api/saka/transactions/ (GET)
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaSiloContract:
    """Tests contract pour /api/saka/silo/"""
    
    def test_saka_silo_requires_authentication(self, client):
        """Vérifie que l'endpoint nécessite une authentification (401)"""
        response = client.get('/api/saka/silo/', follow=True)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_saka_silo_returns_expected_structure(self, authenticated_client, user):
        """Vérifie que la réponse a la structure attendue"""
        response = authenticated_client.get('/api/saka/silo/', follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Vérifier champs obligatoires
        required_fields = ['enabled', 'total_balance', 'total_composted', 'total_cycles']
        for field in required_fields:
            assert field in data, f"Champ obligatoire '{field}' manquant"
        
        # Vérifier types
        assert isinstance(data['enabled'], bool), "'enabled' doit être un booléen"
        assert isinstance(data['total_balance'], (int, float)), "'total_balance' doit être un nombre"
        assert isinstance(data['total_composted'], (int, float)), "'total_composted' doit être un nombre"
        assert isinstance(data['total_cycles'], int), "'total_cycles' doit être un entier"


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaCompostPreviewContract:
    """Tests contract pour /api/saka/compost-preview/"""
    
    def test_compost_preview_requires_authentication(self, client):
        """Vérifie que l'endpoint nécessite une authentification (401)"""
        response = client.get('/api/saka/compost-preview/', follow=True)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_compost_preview_returns_expected_structure(self, authenticated_client, user):
        """Vérifie que la réponse a la structure attendue"""
        response = authenticated_client.get('/api/saka/compost-preview/', follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Vérifier champ obligatoire
        assert 'enabled' in data, "Champ obligatoire 'enabled' manquant"
        assert isinstance(data['enabled'], bool), "'enabled' doit être un booléen"


@pytest.mark.django_db
@pytest.mark.critical
class TestSakaGrantContract:
    """Tests contract pour /api/saka/grant/ (POST)"""
    
    def test_saka_grant_requires_authentication(self, client):
        """Vérifie que l'endpoint nécessite une authentification (401)"""
        # Ne pas follow les redirections : un 301 (http->https) transformerait POST en GET (et retournerait 405)
        response = client.post('/api/saka/grant/', {}, follow=False, secure=True)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_saka_grant_requires_valid_payload(self, authenticated_client, user, settings):
        """Vérifie que l'endpoint valide le payload (400 si invalide)"""
        # Endpoint test-only : activer le mode E2E pour tester la validation du payload
        settings.E2E_TEST_MODE = True

        # Test avec payload vide
        response = authenticated_client.post('/api/saka/grant/', {}, follow=False, secure=True)
        
        # Doit retourner 400 (Bad Request) si payload invalide
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        
        if response.status_code in [400, 422]:
            data = response.json()
            # Vérifier que l'erreur est structurée (DRF peut renvoyer {field: [messages]})
            assert isinstance(data, dict), "Erreur doit être un objet JSON"
            assert (
                'error' in data
                or 'detail' in data
                or 'errors' in data
                or len(data.keys()) > 0
            ), "Erreur doit être structurée"


@pytest.fixture
def user(db):
    """Utilisateur de test"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(user):
    """Client API authentifié"""
    client = APIClient()
    client.defaults["wsgi.url_scheme"] = "https"
    client.force_authenticate(user=user)
    return client




@pytest.fixture
def authenticated_client(user):
    """Client API authentifié"""
    client = APIClient()
    client.defaults["wsgi.url_scheme"] = "https"
    client.force_authenticate(user=user)
    return client

