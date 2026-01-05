"""
Tests de permissions pour les endpoints Polls (Sondages).

Vérifie que les permissions sont correctement appliquées selon les rôles :
- Utilisateur anonyme → 200 (GET) / 401 (POST/PUT/DELETE/actions)
- Utilisateur authentifié → 200 pour toutes les opérations (sauf open/close si pas owner)
- Admin → 200 pour toutes les opérations

Endpoints testés (4) :
1. GET/POST /api/polls/ - IsAuthenticatedOrReadOnly
2. GET/PUT/DELETE /api/polls/<id>/ - IsAuthenticatedOrReadOnly
3. POST /api/polls/<id>/open/ - IsAuthenticated (owner or admin)
4. POST /api/polls/<id>/close/ - IsAuthenticated (owner or admin)
5. POST /api/polls/<id>/vote/ - IsAuthenticated
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from core.models import Poll, PollOption

User = get_user_model()


@pytest.fixture
def client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def regular_user(db):
    """Utilisateur authentifié (non-admin)"""
    return User.objects.create_user(
        username='regular',
        email='regular@example.com',
        password='testpass123'
    )


@pytest.fixture
def other_user(db):
    """Autre utilisateur authentifié (non-admin)"""
    return User.objects.create_user(
        username='other',
        email='other@example.com',
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
def test_poll(db, regular_user):
    """Sondage de test créé par regular_user"""
    poll = Poll.objects.create(
        title='Test Poll',
        question='Test question?',
        voting_method='binary',
        status=Poll.STATUS_DRAFT,
        created_by=regular_user,
    )
    PollOption.objects.create(poll=poll, label='Option 1', position=0)
    PollOption.objects.create(poll=poll, label='Option 2', position=1)
    return poll


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
    
    if user:
        client.force_authenticate(user=user)
    # Si user est None, on laisse le client non authentifié (pas besoin de force_authenticate)
    
    method_func = getattr(client, method.lower())
    if data:
        response = method_func(url, data, format='json')
    else:
        response = method_func(url)
    
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
class TestPollListCreatePermissions:
    """Tests de permissions pour GET/POST /api/polls/"""
    
    def test_anonymous_can_list_polls(self, client):
        """Un utilisateur anonyme peut lister les sondages → 200"""
        url = reverse('poll-list')
        assert_permission(client, url, 'get', None, status.HTTP_200_OK)
    
    def test_anonymous_cannot_create_poll(self, client):
        """Un utilisateur anonyme ne peut pas créer un sondage → 401"""
        url = reverse('poll-list')
        data = {
            'title': 'New Poll',
            'question': 'New question?',
            'voting_method': 'binary',
            'status': Poll.STATUS_DRAFT,
        }
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_authenticated_user_can_list_polls(self, client, regular_user):
        """Un utilisateur authentifié peut lister les sondages → 200"""
        url = reverse('poll-list')
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_authenticated_user_can_create_poll(self, client, regular_user):
        """Un utilisateur authentifié peut créer un sondage → 201"""
        url = reverse('poll-list')
        data = {
            'title': 'New Poll',
            'question': 'New question?',
            'voting_method': 'binary',
            'status': Poll.STATUS_DRAFT,
            'options': [
                {'label': 'Option 1', 'position': 0},
                {'label': 'Option 2', 'position': 1},
            ],
        }
        assert_permission(client, url, 'post', regular_user, status.HTTP_201_CREATED, data=data)
    
    def test_admin_can_list_polls(self, client, admin_user):
        """Un admin peut lister les sondages → 200"""
        url = reverse('poll-list')
        assert_permission(client, url, 'get', admin_user, status.HTTP_200_OK)
    
    def test_admin_can_create_poll(self, client, admin_user):
        """Un admin peut créer un sondage → 201"""
        url = reverse('poll-list')
        data = {
            'title': 'New Poll Admin',
            'question': 'New question?',
            'voting_method': 'binary',
            'status': Poll.STATUS_DRAFT,
            'options': [
                {'label': 'Option 1', 'position': 0},
                {'label': 'Option 2', 'position': 1},
            ],
        }
        assert_permission(client, url, 'post', admin_user, status.HTTP_201_CREATED, data=data)


@pytest.mark.django_db
@pytest.mark.critical
class TestPollRetrieveUpdateDestroyPermissions:
    """Tests de permissions pour GET/PUT/DELETE /api/polls/<id>/"""
    
    def test_anonymous_can_retrieve_poll(self, client, test_poll):
        """Un utilisateur anonyme peut récupérer un sondage → 200"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'get', None, status.HTTP_200_OK)
    
    def test_anonymous_cannot_update_poll(self, client, test_poll):
        """Un utilisateur anonyme ne peut pas mettre à jour un sondage → 401"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        data = {'title': 'Updated Title'}
        assert_permission(client, url, 'put', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_anonymous_cannot_delete_poll(self, client, test_poll):
        """Un utilisateur anonyme ne peut pas supprimer un sondage → 401"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'delete', None, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_retrieve_poll(self, client, regular_user, test_poll):
        """Un utilisateur authentifié peut récupérer un sondage → 200"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'get', regular_user, status.HTTP_200_OK)
    
    def test_owner_can_update_poll(self, client, regular_user, test_poll):
        """Le propriétaire peut mettre à jour son sondage → 200"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        data = {
            'title': test_poll.title,
            'question': 'Updated question?',
            'voting_method': test_poll.voting_method,
            'status': test_poll.status,
        }
        assert_permission(client, url, 'put', regular_user, status.HTTP_200_OK, data=data)
    
    def test_other_user_cannot_update_poll(self, client, other_user, test_poll):
        """Un autre utilisateur ne peut pas mettre à jour le sondage → 403"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        data = {'title': 'Updated Title'}
        assert_permission(client, url, 'put', other_user, status.HTTP_403_FORBIDDEN, data=data)
    
    def test_owner_can_delete_poll(self, client, regular_user, test_poll):
        """Le propriétaire peut supprimer son sondage → 204"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'delete', regular_user, status.HTTP_204_NO_CONTENT)
    
    def test_admin_can_update_poll(self, client, admin_user, test_poll):
        """Un admin peut mettre à jour n'importe quel sondage → 200"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        data = {
            'title': test_poll.title,
            'question': 'Updated question by admin?',
            'voting_method': test_poll.voting_method,
            'status': test_poll.status,
        }
        assert_permission(client, url, 'put', admin_user, status.HTTP_200_OK, data=data)
    
    def test_admin_can_delete_poll(self, client, admin_user, test_poll):
        """Un admin peut supprimer n'importe quel sondage → 204"""
        url = reverse('poll-detail', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'delete', admin_user, status.HTTP_204_NO_CONTENT)


@pytest.mark.django_db
@pytest.mark.critical
class TestPollOpenClosePermissions:
    """Tests de permissions pour POST /api/polls/<id>/open/ et /close/"""
    
    def test_anonymous_cannot_open_poll(self, client, test_poll):
        """Un utilisateur anonyme ne peut pas ouvrir un sondage → 401"""
        url = reverse('poll-open', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data={})
    
    def test_anonymous_cannot_close_poll(self, client, test_poll):
        """Un utilisateur anonyme ne peut pas fermer un sondage → 401"""
        url = reverse('poll-close', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data={})
    
    def test_owner_can_open_poll(self, client, regular_user, test_poll):
        """Le propriétaire peut ouvrir son sondage → 200"""
        url = reverse('poll-open', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', regular_user, status.HTTP_200_OK, data={})
    
    def test_owner_can_close_poll(self, client, regular_user, test_poll):
        """Le propriétaire peut fermer son sondage → 200"""
        # Ouvrir d'abord le sondage
        test_poll.status = Poll.STATUS_OPEN
        test_poll.save()
        url = reverse('poll-close', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', regular_user, status.HTTP_200_OK, data={})
    
    def test_other_user_cannot_open_poll(self, client, other_user, test_poll):
        """Un autre utilisateur ne peut pas ouvrir le sondage → 403"""
        url = reverse('poll-open', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', other_user, status.HTTP_403_FORBIDDEN, data={})
    
    def test_other_user_cannot_close_poll(self, client, other_user, test_poll):
        """Un autre utilisateur ne peut pas fermer le sondage → 403"""
        test_poll.status = Poll.STATUS_OPEN
        test_poll.save()
        url = reverse('poll-close', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', other_user, status.HTTP_403_FORBIDDEN, data={})
    
    def test_admin_can_open_poll(self, client, admin_user, test_poll):
        """Un admin peut ouvrir n'importe quel sondage → 200"""
        url = reverse('poll-open', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', admin_user, status.HTTP_200_OK, data={})
    
    def test_admin_can_close_poll(self, client, admin_user, test_poll):
        """Un admin peut fermer n'importe quel sondage → 200"""
        test_poll.status = Poll.STATUS_OPEN
        test_poll.save()
        url = reverse('poll-close', kwargs={'pk': test_poll.id})
        assert_permission(client, url, 'post', admin_user, status.HTTP_200_OK, data={})


@pytest.mark.django_db
@pytest.mark.critical
class TestPollVotePermissions:
    """Tests de permissions pour POST /api/polls/<id>/vote/"""
    
    def test_anonymous_cannot_vote(self, client, test_poll):
        """Un utilisateur anonyme ne peut pas voter → 401"""
        url = reverse('poll-vote', kwargs={'pk': test_poll.id})
        data = {'options': [1]}
        assert_permission(client, url, 'post', None, status.HTTP_401_UNAUTHORIZED, data=data)
    
    def test_authenticated_user_can_vote(self, client, regular_user, test_poll):
        """Un utilisateur authentifié peut voter → 200 (ou 400 si poll fermé)"""
        # Ouvrir le sondage d'abord
        test_poll.status = Poll.STATUS_OPEN
        test_poll.opens_at = timezone.now()
        test_poll.save()
        
        url = reverse('poll-vote', kwargs={'pk': test_poll.id})
        data = {'options': [test_poll.options.first().id]}
        # Peut retourner 200 (succès) ou 400 (poll fermé/invalide)
        assert_permission(client, url, 'post', regular_user, [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST], data=data)
    
    def test_admin_can_vote(self, client, admin_user, test_poll):
        """Un admin peut voter → 200 (ou 400 si poll fermé)"""
        # Ouvrir le sondage d'abord
        test_poll.status = Poll.STATUS_OPEN
        test_poll.opens_at = timezone.now()
        test_poll.save()
        
        url = reverse('poll-vote', kwargs={'pk': test_poll.id})
        data = {'options': [test_poll.options.first().id]}
        # Peut retourner 200 (succès) ou 400 (poll fermé/invalide)
        assert_permission(client, url, 'post', admin_user, [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST], data=data)

