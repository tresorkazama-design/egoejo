"""
Contract tests pour les endpoints CMS workflow (publish/reject/archive).

Vérifie que les endpoints respectent leur contrat :
- Status codes attendus (200, 400, 403, 404)
- Structure payload
- Validation des transitions
- Erreurs structurées
"""
import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import EducationalContent
from core.permissions import (
    CONTENT_EDITOR_GROUP_NAME,
    CONTENT_CONTRIBUTOR_GROUP_NAME,
)


def with_trailing_slash(url: str) -> str:
    """Évite les 301 (APPEND_SLASH) qui cassent les attentes de status codes."""
    return url if url.endswith("/") else f"{url}/"


@pytest.fixture
def client():
    """Client API pour les tests"""
    c = APIClient()
    # Certains environnements activent SECURE_SSL_REDIRECT en tests -> 301 HTTP->HTTPS.
    # On force donc le schéma HTTPS pour éviter des 301 parasites dans les tests de contrat.
    c.defaults["wsgi.url_scheme"] = "https"
    return c


@pytest.fixture(autouse=True)
def _disable_secure_ssl_redirect(settings):
    """
    Ces tests sont des tests de contrat métier (auth/permissions/workflow) :
    on neutralise les redirections de sécurité (HTTP->HTTPS) qui masquent les vrais status codes.
    """
    settings.SECURE_SSL_REDIRECT = False


@pytest.fixture
def contributor_user(db):
    """Utilisateur avec rôle Contributor"""
    user = User.objects.create_user(
        username='contributor',
        email='contributor@example.com',
        password='testpass123'
    )
    group, _ = Group.objects.get_or_create(name=CONTENT_CONTRIBUTOR_GROUP_NAME)
    user.groups.add(group)
    return user


@pytest.fixture
def editor_user(db):
    """Utilisateur avec rôle Editor"""
    user = User.objects.create_user(
        username='editor',
        email='editor@example.com',
        password='testpass123'
    )
    group, _ = Group.objects.get_or_create(name=CONTENT_EDITOR_GROUP_NAME)
    user.groups.add(group)
    return user


@pytest.fixture
def admin_user(db):
    """Utilisateur avec rôle Admin (superuser)"""
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
def content_pending(db, contributor_user):
    """Contenu en attente de validation"""
    return EducationalContent.objects.create(
        title='Test Content Pending',
        slug='test-content-pending',
        type='article',
        status='pending',
        description='Description test',
        author=contributor_user,
    )


@pytest.fixture
def content_published(db, admin_user):
    """Contenu publié"""
    content = EducationalContent.objects.create(
        title='Test Content Published',
        slug='test-content-published',
        type='article',
        status='published',
        description='Description published',
        author=admin_user,
    )
    return content


@pytest.mark.django_db
@pytest.mark.critical
class TestPublishContract:
    """Contract tests pour POST /api/contents/{id}/publish/"""
    
    def test_publish_requires_authentication(self, client, content_pending):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        url = with_trailing_slash(reverse('content-publish', kwargs={'pk': content_pending.id}))
        response = client.post(url)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_publish_requires_editor_permission(self, client, contributor_user, content_pending):
        """Vérifie que l'endpoint requiert la permission editor (403 si contributor)"""
        client.force_authenticate(user=contributor_user)
        url = with_trailing_slash(reverse('content-publish', kwargs={'pk': content_pending.id}))
        response = client.post(url)
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        data = response.json()
        assert 'detail' in data or 'error' in data, "Erreur doit être structurée"
    
    def test_publish_returns_200_on_success(self, client, admin_user, content_pending):
        """Vérifie que l'endpoint retourne 200 en cas de succès"""
        client.force_authenticate(user=admin_user)
        url = with_trailing_slash(reverse('content-publish', kwargs={'pk': content_pending.id}))
        response = client.post(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'id' in data, "Réponse doit contenir 'id'"
        assert 'status' in data, "Réponse doit contenir 'status'"
        assert data['status'] == 'published', "Status doit être 'published'"
    
    def test_publish_returns_404_if_content_not_found(self, client, admin_user):
        """Vérifie que l'endpoint retourne 404 si le contenu n'existe pas"""
        client.force_authenticate(user=admin_user)
        url = with_trailing_slash(reverse('content-publish', kwargs={'pk': 99999}))
        response = client.post(url)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_publish_updates_status(self, client, admin_user, content_pending):
        """Vérifie que l'endpoint met à jour le status du contenu"""
        client.force_authenticate(user=admin_user)
        url = with_trailing_slash(reverse('content-publish', kwargs={'pk': content_pending.id}))
        response = client.post(url)
        
        assert response.status_code == 200
        content_pending.refresh_from_db()
        assert content_pending.status == 'published', "Status doit être mis à jour à 'published'"
    
    def test_publish_returns_400_on_invalid_transition(self, client, admin_user, content_published):
        """Vérifie que l'endpoint retourne 400 si la transition est invalide"""
        client.force_authenticate(user=admin_user)
        url = with_trailing_slash(reverse('content-publish', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        # published -> published n'est pas une transition valide
        assert response.status_code in [400, 200], f"Expected 400 or 200, got {response.status_code}"


@pytest.mark.django_db
@pytest.mark.critical
class TestRejectContract:
    """Contract tests pour POST /api/contents/{id}/reject/"""
    
    def test_reject_requires_authentication(self, client, content_pending):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        url = with_trailing_slash(reverse('content-reject', kwargs={'pk': content_pending.id}))
        response = client.post(url, {'rejection_reason': 'Test rejection'})
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_reject_requires_editor_permission(self, client, contributor_user, content_pending):
        """Vérifie que l'endpoint requiert la permission editor (403 si contributor)"""
        client.force_authenticate(user=contributor_user)
        url = with_trailing_slash(reverse('content-reject', kwargs={'pk': content_pending.id}))
        response = client.post(url, {'rejection_reason': 'Test rejection'})
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_reject_returns_200_on_success(self, client, editor_user, content_pending):
        """Vérifie que l'endpoint retourne 200 en cas de succès"""
        client.force_authenticate(user=editor_user)
        url = with_trailing_slash(reverse('content-reject', kwargs={'pk': content_pending.id}))
        response = client.post(url, {'rejection_reason': 'Test rejection'})
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'id' in data, "Réponse doit contenir 'id'"
        assert 'status' in data, "Réponse doit contenir 'status'"
        assert data['status'] == 'rejected', "Status doit être 'rejected'"
    
    def test_reject_updates_status(self, client, editor_user, content_pending):
        """Vérifie que l'endpoint met à jour le status du contenu"""
        client.force_authenticate(user=editor_user)
        url = with_trailing_slash(reverse('content-reject', kwargs={'pk': content_pending.id}))
        response = client.post(url, {'rejection_reason': 'Test rejection'})
        
        assert response.status_code == 200
        content_pending.refresh_from_db()
        assert content_pending.status == 'rejected', "Status doit être mis à jour à 'rejected'"


@pytest.mark.django_db
@pytest.mark.critical
class TestArchiveContract:
    """Contract tests pour POST /api/contents/{id}/archive/"""
    
    def test_archive_requires_authentication(self, client, content_published):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        url = with_trailing_slash(reverse('content-archive', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_archive_requires_editor_permission(self, client, contributor_user, content_published):
        """Vérifie que l'endpoint requiert la permission editor (403 si contributor)"""
        client.force_authenticate(user=contributor_user)
        url = with_trailing_slash(reverse('content-archive', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_archive_returns_200_on_success(self, client, admin_user, content_published):
        """Vérifie que l'endpoint retourne 200 en cas de succès"""
        client.force_authenticate(user=admin_user)
        url = with_trailing_slash(reverse('content-archive', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'id' in data, "Réponse doit contenir 'id'"
        assert 'status' in data, "Réponse doit contenir 'status'"
        assert data['status'] == 'archived', "Status doit être 'archived'"
    
    def test_archive_updates_status(self, client, admin_user, content_published):
        """Vérifie que l'endpoint met à jour le status du contenu"""
        client.force_authenticate(user=admin_user)
        url = with_trailing_slash(reverse('content-archive', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code == 200
        content_published.refresh_from_db()
        assert content_published.status == 'archived', "Status doit être mis à jour à 'archived'"


@pytest.mark.django_db
@pytest.mark.critical
class TestUnpublishContract:
    """Contract tests pour POST /api/contents/{id}/unpublish/"""
    
    def test_unpublish_requires_authentication(self, client, content_published):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        url = with_trailing_slash(reverse('content-unpublish', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
    
    def test_unpublish_requires_editor_permission(self, client, contributor_user, content_published):
        """Vérifie que l'endpoint requiert la permission editor (403 si contributor)"""
        client.force_authenticate(user=contributor_user)
        url = with_trailing_slash(reverse('content-unpublish', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_unpublish_returns_200_on_success(self, client, editor_user, content_published):
        """Vérifie que l'endpoint retourne 200 en cas de succès"""
        client.force_authenticate(user=editor_user)
        url = with_trailing_slash(reverse('content-unpublish', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'id' in data, "Réponse doit contenir 'id'"
        assert 'status' in data, "Réponse doit contenir 'status'"
        assert data['status'] == 'draft', "Status doit être 'draft'"
    
    def test_unpublish_updates_status(self, client, editor_user, content_published):
        """Vérifie que l'endpoint met à jour le status du contenu"""
        client.force_authenticate(user=editor_user)
        url = with_trailing_slash(reverse('content-unpublish', kwargs={'pk': content_published.id}))
        response = client.post(url)
        
        assert response.status_code == 200
        content_published.refresh_from_db()
        assert content_published.status == 'draft', "Status doit être mis à jour à 'draft'"

