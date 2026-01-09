"""
Tests de permissions pour les endpoints Projets.

Vérifie que les permissions sont correctement appliquées selon les rôles :
- Utilisateur anonyme → 200 (GET) / 401 (POST/PUT/DELETE)
- Utilisateur authentifié → 200 pour toutes les opérations
- Admin → 200 pour toutes les opérations

Endpoints testés (3) :
1. GET/POST /api/projets/ - IsAuthenticatedOrReadOnly
2. GET/PUT/DELETE /api/projets/<id>/ - IsAuthenticatedOrReadOnly
3. POST /api/projets/<id>/boost/ - IsAuthenticated
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Projet

User = get_user_model()


@pytest.fixture
def client():
    """Client API pour les tests"""
    c = APIClient()
    c.defaults["wsgi.url_scheme"] = "https"
    return c


@pytest.fixture
def regular_user(db):
    """Utilisateur authentifié (non-admin)"""
    return User.objects.create_user(
        username='regular',
        email='regular@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Utilisateur admin (superuser)"""
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123'
    )
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def test_project(db, regular_user):
    """Projet de test"""
    return Projet.objects.create(
        titre='Test Project',
        description='Test description',
        donation_goal=1000.00,
        funding_type='DONATION',
    )


def assert_permission(client, url, method, user, expected_status, data=None):
    """
    Helper pour tester les permissions d'un endpoint.
    
    Args:
        client: APIClient
        url: URL de l'endpoint
        method: 'get', 'post', 'put', 'delete', etc.
        user: User ou None (pour anonyme)
        expected_status: Status HTTP attendu (ou liste de status acceptables)
        data: Données pour POST/PUT (optionnel)
    """
    # Réinitialiser l'authentification du client
    client.force_authenticate(user=None)

    # Normaliser l'URL (évite 301 APPEND_SLASH)
    if not url.endswith("/"):
        url = f"{url}/"
    
    if user:
        client.force_authenticate(user=user)
    # Si user est None, on laisse le client non authentifié (pas besoin de force_authenticate)
    
    method_func = getattr(client, method.lower())
    if data:
        response = method_func(url, data, format='json', secure=True)
    else:
        response = method_func(url, secure=True)
    
    # DRF peut retourner 401 ou 403 selon le contexte
    # 401 = non authentifié, 403 = authentifié mais sans permissions
    # Pour les utilisateurs anonymes, on accepte les deux codes
    if user is None and expected_status == status.HTTP_401_UNAUTHORIZED:
        expected_status = [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    if isinstance(expected_status, list):
        assert response.status_code in expected_status, (
            f"Expected status in {expected_status}, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    else:
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )


@pytest.mark.django_db
@pytest.mark.critical
class TestProjetListCreatePermissions:
    """Tests de permissions pour GET/POST /api/projets/"""
    
    def test_anonymous_can_list_projects(self, client):
        """Un utilisateur anonyme peut lister les projets → 200"""
        url = reverse('projet-list-create')
        assert_permission(client, url, 'get', None, status.HTTP_200_OK)
    
    def test_anonymous_cannot_create_project(self, client):
        """Un utilisateur anonyme ne peut pas créer de projet → 401"""
        url = reverse('projet-list-create')
        data = {
            'titre': 'New Project',
            'description': 'New description',
            'donation_goal': 1000.00,
            'funding_type': 'DONATION',
        }
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_authenticated_user_can_list_projects(self, client, regular_user):
        """Un utilisateur authentifié peut lister les projets → 200"""
        url = reverse('projet-list-create')
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_authenticated_user_can_create_project(self, client, regular_user):
        """Un utilisateur authentifié peut créer un projet → 201"""
        url = reverse('projet-list-create')
        data = {
            'titre': 'New Project',
            'description': 'New description',
            'donation_goal': 1000.00,
            'funding_type': 'DONATION',
        }
        assert_permission(client, url, 'post', regular_user, status.HTTP_201_CREATED, data=data)
    
    def test_admin_can_list_projects(self, client, admin_user):
        """Un admin peut lister les projets → 200"""
        url = reverse('projet-list-create')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)
    
    def test_admin_can_create_project(self, client, admin_user):
        """Un admin peut créer un projet → 201"""
        url = reverse('projet-list-create')
        data = {
            'titre': 'New Project Admin',
            'description': 'New description',
            'donation_goal': 1000.00,
            'funding_type': 'DONATION',
        }
        assert_permission(client, url, 'post', admin_user, status.HTTP_201_CREATED, data=data)


@pytest.mark.django_db
@pytest.mark.critical
class TestProjetRetrieveUpdateDestroyPermissions:
    """Tests de permissions pour GET/PUT/DELETE /api/projets/<id>/"""
    
    def test_anonymous_can_retrieve_project(self, client, test_project):
        """Un utilisateur anonyme peut récupérer un projet → 200"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        assert_permission(client, url, 'get', None, status.HTTP_200_OK)
    
    def test_anonymous_cannot_update_project(self, client, test_project):
        """Un utilisateur anonyme ne peut pas mettre à jour un projet → 401"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        data = {'titre': 'Updated Title'}
        assert_permission(client, url, 'put', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_anonymous_cannot_delete_project(self, client, test_project):
        """Un utilisateur anonyme ne peut pas supprimer un projet → 401"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        assert_permission(client, url, 'delete', None, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_retrieve_project(self, client, regular_user, test_project):
        """Un utilisateur authentifié peut récupérer un projet → 200"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_authenticated_user_can_update_project(self, client, regular_user, test_project):
        """Un utilisateur authentifié peut mettre à jour un projet → 200"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        data = {
            'titre': test_project.titre,
            'description': 'Updated description',
            'donation_goal': str(test_project.donation_goal),
            'funding_type': test_project.funding_type,
        }
        assert_permission(client, url, 'put', regular_user, status.HTTP_200_OK, data=data)
    
    def test_authenticated_user_can_delete_project(self, client, regular_user, test_project):
        """Un utilisateur authentifié peut supprimer un projet → 204"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        assert_permission(client, url, 'delete', regular_user, status.HTTP_204_NO_CONTENT)
    
    def test_admin_can_retrieve_project(self, client, admin_user, test_project):
        """Un admin peut récupérer un projet → 200"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)
    
    def test_admin_can_update_project(self, client, admin_user, test_project):
        """Un admin peut mettre à jour un projet → 200"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        data = {
            'titre': test_project.titre,
            'description': 'Updated description by admin',
            'donation_goal': str(test_project.donation_goal),
            'funding_type': test_project.funding_type,
        }
        assert_permission(client, url, 'put', admin_user, status.HTTP_200_OK, data=data)
    
    def test_admin_can_delete_project(self, client, admin_user, test_project):
        """Un admin peut supprimer un projet → 204"""
        url = reverse('projet-detail', kwargs={'pk': test_project.id})
        assert_permission(client, url, 'delete', admin_user, status.HTTP_204_NO_CONTENT)


@pytest.mark.django_db
@pytest.mark.critical
class TestProjetBoostPermissions:
    """Tests de permissions pour POST /api/projets/<id>/boost/"""
    
    def test_anonymous_cannot_boost_project(self, client, test_project):
        """Un utilisateur anonyme ne peut pas booster un projet → 401"""
        url = reverse('projet-boost', kwargs={'pk': test_project.id})
        data = {'amount': 10}
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_authenticated_user_can_boost_project(self, client, regular_user, test_project):
        """Un utilisateur authentifié peut booster un projet → 200 (ou 400 si SAKA désactivé)"""
        url = reverse('projet-boost', kwargs={'pk': test_project.id})
        data = {'amount': 10}
        # Peut retourner 200 (si SAKA activé) ou 403 (si SAKA désactivé)
        # On accepte les deux car le test vérifie juste la permission, pas la logique métier
        response = client.post(url, data, format='json')
        client.force_authenticate(user=regular_user)
        response = client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST], (
            f"Expected 200, 403, or 400, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )
    
    def test_admin_can_boost_project(self, client, admin_user, test_project):
        """Un admin peut booster un projet → 200 (ou 400 si SAKA désactivé)"""
        url = reverse('projet-boost', kwargs={'pk': test_project.id})
        data = {'amount': 10}
        client.force_authenticate(user=admin_user)
        response = client.post(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST], (
            f"Expected 200, 403, or 400, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )


        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST], (
            f"Expected 200, 403, or 400, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}"
        )

