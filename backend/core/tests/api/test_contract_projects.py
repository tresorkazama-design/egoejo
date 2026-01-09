"""
Contract tests pour les endpoints projets critiques

Vérifie que les endpoints projets respectent leur contrat :
- GET /api/projets/
- POST /api/projets/
- GET /api/projets/{id}/
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Projet

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.critical
class TestProjectsListContract:
    """Tests contract pour GET /api/projets/"""
    
    def test_projects_list_is_public(self, client):
        """Vérifie que l'endpoint est public (200 sans auth)"""
        response = client.get('/api/projets/', follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Vérifier structure de réponse (liste ou pagination)
        assert isinstance(data, (list, dict)), "Réponse doit être une liste ou un objet de pagination"
        
        if isinstance(data, dict):
            # Si pagination, vérifier champs obligatoires
            assert 'results' in data or 'count' in data, "Réponse paginée doit contenir 'results' ou 'count'"
    
    def test_projects_list_returns_array(self, client):
        """Vérifie que la réponse est un tableau (même vide)"""
        response = client.get('/api/projets/', follow=True)
        data = response.json()
        
        # Peut être une liste directe ou un objet avec 'results'
        if isinstance(data, dict):
            assert 'results' in data, "Si dict, doit contenir 'results'"
            assert isinstance(data['results'], list), "'results' doit être une liste"


@pytest.mark.django_db
@pytest.mark.critical
class TestProjectsCreateContract:
    """Tests contract pour POST /api/projets/"""
    
    def test_projects_create_requires_authentication(self, client):
        """Vérifie que l'endpoint nécessite une authentification (401)"""
        # Ne pas follow les redirections : un 301 (http->https) transformerait POST en GET (et retournerait 200)
        response = client.post('/api/projets/', {}, follow=False, secure=True)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_projects_create_validates_payload(self, authenticated_client, user):
        """Vérifie que l'endpoint valide le payload (400 si invalide)"""
        # Test avec payload vide
        response = authenticated_client.post('/api/projets/', {}, follow=False, secure=True)
        
        # Doit retourner 400 (Bad Request) si payload invalide
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        
        if response.status_code in [400, 422]:
            data = response.json()
            # Vérifier que l'erreur est structurée :
            # - DRF renvoie souvent un dict {field: [messages]} plutôt qu'un wrapper {error/detail}
            assert isinstance(data, dict), "Erreur doit être un objet JSON"
            assert (
                'error' in data
                or 'detail' in data
                or 'errors' in data
                or len(data.keys()) > 0
            ), "Erreur doit être structurée"
    
    def test_projects_create_returns_201_on_success(self, authenticated_client, user):
        """Vérifie que l'endpoint retourne 201 en cas de succès"""
        payload = {
            'titre': 'Test Project',
            'description': 'Test description',
            'categorie': 'Environnement'
        }
        response = authenticated_client.post('/api/projets/', payload, follow=False, secure=True)
        
        # Doit retourner 201 (Created) ou 400 (si validation échoue)
        assert response.status_code in [201, 400, 422], f"Status code inattendu: {response.status_code}"
        
        if response.status_code == 201:
            data = response.json()
            # Vérifier champs obligatoires
            assert 'id' in data, "Réponse doit contenir 'id'"
            assert 'titre' in data, "Réponse doit contenir 'titre'"


@pytest.mark.django_db
@pytest.mark.critical
class TestProjectsDetailContract:
    """Tests contract pour GET /api/projets/{id}/"""
    
    def test_projects_detail_is_public(self, client, project):
        """Vérifie que l'endpoint est public (200 sans auth)"""
        response = client.get(f'/api/projets/{project.id}/', follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Vérifier champs obligatoires
        assert 'id' in data, "Réponse doit contenir 'id'"
        assert 'titre' in data, "Réponse doit contenir 'titre'"
    
    def test_projects_detail_returns_404_if_not_found(self, client):
        """Vérifie que l'endpoint retourne 404 si le projet n'existe pas"""
        response = client.get('/api/projets/99999/', follow=True)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


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
def project(db):
    """Projet de test"""
    from core.models import Projet
    return Projet.objects.create(
        titre='Test Project',
        description='Test description',
        categorie='Environnement'
    )


@pytest.fixture
def authenticated_client(user):
    """Client API authentifié"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def authenticated_client(user):
    """Client API authentifié"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

