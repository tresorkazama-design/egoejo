"""
Tests de permissions pour les endpoints CMS (contenu éducatif).

Vérifie que les permissions sont correctement appliquées selon les rôles :
- Utilisateur anonyme → 403
- Contributor → peut créer, ne peut pas publish/reject/archive
- Editor → peut créer, publish, reject, archive
- Admin → peut tout faire
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


@pytest.fixture
def client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def anonymous_user():
    """Utilisateur anonyme (non authentifié)"""
    return None


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
    """Contenu en attente de validation (créé par contributor)"""
    return EducationalContent.objects.create(
        title='Test Content',
        slug='test-content',
        type='article',
        status='pending',
        description='Description test',
        author=contributor_user,
    )


@pytest.fixture
def content_published(db, editor_user):
    """Contenu publié (créé par editor)"""
    return EducationalContent.objects.create(
        title='Published Content',
        slug='published-content',
        type='article',
        status='published',
        description='Description publiée',
        author=editor_user,
    )


@pytest.mark.django_db
@pytest.mark.critical
class TestContentCreatePermissions:
    """Tests de permissions pour la création de contenu"""
    
    def test_anonymous_cannot_create_content(self, client, anonymous_user):
        """Un utilisateur anonyme ne peut pas créer de contenu"""
        url = reverse('content-list')
        response = client.post(url, {
            'title': 'Test',
            'slug': 'test',
            'type': 'article',
            'description': 'Test description',
        })
        
        # DRF peut retourner 401 ou 403 pour les utilisateurs anonymes selon le contexte
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
    
    def test_contributor_can_create_content(self, client, contributor_user):
        """Un contributor peut créer un contenu"""
        client.force_authenticate(user=contributor_user)
        url = reverse('content-list')
        response = client.post(url, {
            'title': 'Test Content',
            'slug': 'test-content',
            'type': 'article',
            'description': 'Test description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert EducationalContent.objects.filter(slug='test-content').exists()
        content = EducationalContent.objects.get(slug='test-content')
        assert content.status == 'pending'  # Créé en pending
        assert content.author == contributor_user
    
    def test_editor_can_create_content(self, client, editor_user):
        """Un editor peut créer un contenu"""
        client.force_authenticate(user=editor_user)
        url = reverse('content-list')
        response = client.post(url, {
            'title': 'Test Content',
            'slug': 'test-content-editor',
            'type': 'article',
            'description': 'Test description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_admin_can_create_content(self, client, admin_user):
        """Un admin peut créer un contenu"""
        client.force_authenticate(user=admin_user)
        url = reverse('content-list')
        response = client.post(url, {
            'title': 'Test Content',
            'slug': 'test-content-admin',
            'type': 'article',
            'description': 'Test description',
        })
        
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.critical
class TestContentPublishPermissions:
    """Tests de permissions pour la publication de contenu"""
    
    def test_anonymous_cannot_publish(self, client, anonymous_user, content_pending):
        """Un utilisateur anonyme ne peut pas publier"""
        url = reverse('content-publish', kwargs={'pk': content_pending.id})
        response = client.post(url, follow=True)
        
        # DRF peut retourner 401 ou 403 pour les utilisateurs anonymes selon le contexte
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
    
    def test_contributor_cannot_publish(self, client, contributor_user, content_pending):
        """Un contributor ne peut pas publier"""
        client.force_authenticate(user=contributor_user)
        url = reverse('content-publish', kwargs={'pk': content_pending.id})
        response = client.post(url, follow=True)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        content_pending.refresh_from_db()
        assert content_pending.status == 'pending'  # Status inchangé
    
    def test_editor_can_publish(self, client, editor_user, content_pending):
        """Un editor peut publier"""
        client.force_authenticate(user=editor_user)
        url = reverse('content-publish', kwargs={'pk': content_pending.id})
        response = client.post(url, follow=True)
        
        assert response.status_code == status.HTTP_200_OK
        content_pending.refresh_from_db()
        assert content_pending.status == 'published'
    
    def test_admin_can_publish(self, client, admin_user, content_pending):
        """Un admin peut publier"""
        client.force_authenticate(user=admin_user)
        url = reverse('content-publish', kwargs={'pk': content_pending.id})
        response = client.post(url, follow=True)
        
        assert response.status_code == status.HTTP_200_OK
        content_pending.refresh_from_db()
        assert content_pending.status == 'published'


@pytest.mark.django_db
@pytest.mark.critical
class TestContentRejectPermissions:
    """Tests de permissions pour le rejet de contenu"""
    
    def test_anonymous_cannot_reject(self, client, anonymous_user, content_pending):
        """Un utilisateur anonyme ne peut pas rejeter"""
        url = reverse('content-reject', kwargs={'pk': content_pending.id})
        response = client.post(url, {'rejection_reason': 'Test rejection'}, follow=True)
        
        # DRF peut retourner 401 ou 403 pour les utilisateurs anonymes selon le contexte
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
    
    def test_contributor_cannot_reject(self, client, contributor_user, content_pending):
        """Un contributor ne peut pas rejeter"""
        client.force_authenticate(user=contributor_user)
        url = reverse('content-reject', kwargs={'pk': content_pending.id})
        response = client.post(url, {'rejection_reason': 'Test rejection'}, follow=True)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        content_pending.refresh_from_db()
        assert content_pending.status == 'pending'  # Status inchangé
    
    def test_editor_can_reject(self, client, editor_user, content_pending):
        """Un editor peut rejeter"""
        client.force_authenticate(user=editor_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_pending.id}/reject/'
        response = client.post(url, {'rejection_reason': 'Test rejection'})
        
        assert response.status_code == status.HTTP_200_OK
        content_pending.refresh_from_db()
        assert content_pending.status == 'rejected'
    
    def test_admin_can_reject(self, client, admin_user, content_pending):
        """Un admin peut rejeter"""
        client.force_authenticate(user=admin_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_pending.id}/reject/'
        response = client.post(url, {'rejection_reason': 'Test rejection'})
        
        assert response.status_code == status.HTTP_200_OK
        content_pending.refresh_from_db()
        assert content_pending.status == 'rejected'


@pytest.mark.django_db
@pytest.mark.critical
class TestContentArchivePermissions:
    """Tests de permissions pour l'archivage de contenu"""
    
    def test_anonymous_cannot_archive(self, client, anonymous_user, content_published):
        """Un utilisateur anonyme ne peut pas archiver"""
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/archive/'
        response = client.post(url)
        
        # DRF peut retourner 401 ou 403 pour les utilisateurs anonymes selon le contexte
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
    
    def test_contributor_cannot_archive(self, client, contributor_user, content_published):
        """Un contributor ne peut pas archiver"""
        client.force_authenticate(user=contributor_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/archive/'
        response = client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        content_published.refresh_from_db()
        assert content_published.status == 'published'  # Status inchangé
    
    def test_editor_can_archive(self, client, editor_user, content_published):
        """Un editor peut archiver"""
        client.force_authenticate(user=editor_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/archive/'
        response = client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Note : Le statut sera "archived" après l'implémentation
        content_published.refresh_from_db()
        assert content_published.status == 'archived'
    
    def test_admin_can_archive(self, client, admin_user, content_published):
        """Un admin peut archiver"""
        client.force_authenticate(user=admin_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/archive/'
        response = client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        content_published.refresh_from_db()
        assert content_published.status == 'archived'


@pytest.mark.django_db
@pytest.mark.critical
class TestContentUnpublishPermissions:
    """Tests de permissions pour la dépublication de contenu"""
    
    def test_anonymous_cannot_unpublish(self, client, anonymous_user, content_published):
        """Un utilisateur anonyme ne peut pas dépublication"""
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/unpublish/'
        response = client.post(url)
        
        # DRF peut retourner 401 ou 403 pour les utilisateurs anonymes selon le contexte
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
    
    def test_contributor_cannot_unpublish(self, client, contributor_user, content_published):
        """Un contributor ne peut pas dépublication"""
        client.force_authenticate(user=contributor_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/unpublish/'
        response = client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        content_published.refresh_from_db()
        assert content_published.status == 'published'  # Status inchangé
    
    def test_editor_can_unpublish(self, client, editor_user, content_published):
        """Un editor peut dépublication"""
        client.force_authenticate(user=editor_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/unpublish/'
        response = client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        content_published.refresh_from_db()
        assert content_published.status == 'draft'
    
    def test_admin_can_unpublish(self, client, admin_user, content_published):
        """Un admin peut dépublication"""
        client.force_authenticate(user=admin_user)
        # Utiliser l'URL directe avec slash final pour éviter les redirections
        url = f'/api/contents/{content_published.id}/unpublish/'
        response = client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        content_published.refresh_from_db()
        assert content_published.status == 'draft'


@pytest.mark.django_db
@pytest.mark.critical
class TestContentReadPermissions:
    """Tests de permissions pour la lecture de contenu (devrait être public)"""
    
    def test_anonymous_can_list_contents(self, client, anonymous_user):
        """Un utilisateur anonyme peut lister les contenus"""
        url = reverse('content-list')
        response = client.get(url, follow=True)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_anonymous_can_retrieve_content(self, client, anonymous_user, content_published):
        """Un utilisateur anonyme peut voir un contenu publié"""
        url = reverse('content-detail', kwargs={'pk': content_published.id})
        response = client.get(url, follow=True)
        
        assert response.status_code == status.HTTP_200_OK

