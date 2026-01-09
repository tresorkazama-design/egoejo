"""
Tests CRUD complets pour le CMS (EducationalContent).

Vérifie :
- Création (déjà testé dans test_content_permissions.py)
- Lecture (déjà testé dans test_content_permissions.py)
- Mise à jour (update/edit) - si présent
- Suppression (delete) - si présent
"""
import pytest
import uuid
import time
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status

from core.models import EducationalContent
from core.permissions import (
    CONTENT_EDITOR_GROUP_NAME,
    CONTENT_CONTRIBUTOR_GROUP_NAME,
)


@pytest.fixture
def client():
    """Client API pour les tests"""
    return APIClient()


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
def content_draft(db, contributor_user):
    """Contenu en brouillon créé par contributor"""
    unique_slug = f'test-content-draft-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
    return EducationalContent.objects.create(
        title='Draft Content',
        slug=unique_slug,
        type='article',
        status='draft',
        description='Description draft',
        author=contributor_user,
    )


@pytest.fixture
def content_pending(db, contributor_user):
    """Contenu en attente créé par contributor"""
    unique_slug = f'test-content-pending-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
    return EducationalContent.objects.create(
        title='Pending Content',
        slug=unique_slug,
        type='article',
        status='pending',
        description='Description pending',
        author=contributor_user,
    )


@pytest.mark.django_db
@pytest.mark.critical
class TestContentRead:
    """Tests de lecture (CRUD - Read)"""
    
    def test_anonymous_can_list_published_contents(self, client):
        """Un utilisateur anonyme peut lister les contenus publiés"""
        # Créer un contenu publié
        content = EducationalContent.objects.create(
            title='Published Content',
            slug=f'published-{int(time.time() * 1000)}',
            type='article',
            status='published',
            description='Description published',
        )
        
        url = '/api/contents/'
        response = client.get(url, {'status': 'published'})
        
        assert response.status_code == status.HTTP_200_OK
        # Vérifier que le contenu est dans les résultats
        results = response.json() if hasattr(response, 'json') else response.data
        if isinstance(results, dict) and 'results' in results:
            assert any(c.get('id') == content.id for c in results['results'])
        elif isinstance(results, list):
            assert any(c.get('id') == content.id for c in results)
    
    def test_anonymous_can_retrieve_published_content(self, client):
        """Un utilisateur anonyme peut voir un contenu publié"""
        content = EducationalContent.objects.create(
            title='Published Content',
            slug=f'published-retrieve-{int(time.time() * 1000)}',
            type='article',
            status='published',
            description='Description published',
        )
        
        url = f'/api/contents/{content.id}/'
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json() if hasattr(response, 'json') else response.data
        assert data.get('id') == content.id
        assert data.get('title') == 'Published Content'
    
    def test_anonymous_cannot_see_draft_content(self, client, content_draft):
        """Un utilisateur anonyme ne peut pas voir un contenu en brouillon"""
        url = f'/api/contents/{content_draft.id}/'
        response = client.get(url)
        
        # Le contenu peut être retourné (selon le queryset), mais ne devrait pas être visible publiquement
        # Vérifier que le status n'est pas 'draft' dans la réponse publique
        if response.status_code == status.HTTP_200_OK:
            data = response.json() if hasattr(response, 'json') else response.data
            # Si le contenu est retourné, vérifier qu'il n'est pas en draft
            # (le queryset peut filtrer automatiquement)
            assert data.get('status') != 'draft' or response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.critical
class TestContentCreate:
    """Tests de création (CRUD - Create) - Complément aux tests permissions"""
    
    def test_create_content_sets_status_pending(self, client, contributor_user):
        """Vérifie qu'un contenu créé a le status 'pending' par défaut"""
        client.force_authenticate(user=contributor_user)
        unique_slug = f'test-create-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        url = '/api/contents/'
        response = client.post(url, {
            'title': 'New Content',
            'slug': unique_slug,
            'type': 'article',
            'description': 'Test description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        content = EducationalContent.objects.get(slug=unique_slug)
        assert content.status == 'pending', "Le status doit être 'pending' par défaut"
        assert content.author == contributor_user, "L'auteur doit être défini"
    
    def test_create_content_with_all_fields(self, client, contributor_user):
        """Vérifie qu'un contenu peut être créé avec tous les champs"""
        client.force_authenticate(user=contributor_user)
        unique_slug = f'test-create-full-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}'
        
        url = '/api/contents/'
        response = client.post(url, {
            'title': 'Full Content',
            'slug': unique_slug,
            'type': 'podcast',
            'category': 'racines-philosophie',
            'description': 'Description complète',
            'tags': ['Steiner', 'Biodynamie'],
            'external_url': 'https://example.com/podcast',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        content = EducationalContent.objects.get(slug=unique_slug)
        assert content.type == 'podcast'
        assert content.category == 'racines-philosophie'
        assert 'Steiner' in content.tags
        assert content.external_url == 'https://example.com/podcast'


@pytest.mark.django_db
class TestContentUpdate:
    """Tests de mise à jour (CRUD - Update) - Si l'endpoint existe"""
    
    def test_update_content_not_implemented(self, client, contributor_user, content_draft):
        """Vérifie que l'update n'est pas implémenté (ViewSet n'a pas UpdateModelMixin)"""
        client.force_authenticate(user=contributor_user)
        url = f'/api/contents/{content_draft.id}/'
        
        # Tenter un PUT/PATCH
        response_put = client.put(url, {
            'title': 'Updated Title',
            'slug': content_draft.slug,
            'type': 'article',
            'description': 'Updated description',
        })
        
        # Le ViewSet n'a pas UpdateModelMixin, donc PUT/PATCH devrait retourner 405 ou 404
        assert response_put.status_code in [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ], f"Update ne devrait pas être disponible, got {response_put.status_code}"


@pytest.mark.django_db
class TestContentDelete:
    """Tests de suppression (CRUD - Delete) - Si l'endpoint existe"""
    
    def test_delete_content_not_implemented(self, client, admin_user, content_draft):
        """Vérifie que la suppression n'est pas implémentée (ViewSet n'a pas DestroyModelMixin)"""
        client.force_authenticate(user=admin_user)
        url = f'/api/contents/{content_draft.id}/'
        
        # Tenter un DELETE
        response = client.delete(url)
        
        # Le ViewSet n'a pas DestroyModelMixin, donc DELETE devrait retourner 405 ou 404
        assert response.status_code in [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN
        ], f"Delete ne devrait pas être disponible, got {response.status_code}"

