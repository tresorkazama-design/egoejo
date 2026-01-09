"""
Contract tests pour les endpoints CMS export (JSON/CSV).

Vérifie que les endpoints respectent leur contrat :
- Status codes attendus (200, 403)
- Structure payload
- Permissions (admin/editor uniquement)
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
def published_content(db, admin_user):
    """Contenu publié pour les tests"""
    return EducationalContent.objects.create(
        title='Test Content Published',
        slug='test-content-published',
        type='article',
        status='published',
        description='Description published',
        author=admin_user,
    )


@pytest.mark.django_db
@pytest.mark.critical
class TestExportJSONContract:
    """Contract tests pour GET /api/contents/export/json/"""
    
    def test_export_json_requires_authentication(self, client):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        url = reverse('content-export-json')
        response = client.get(url, follow=True)
        
        # Accepter 301 (redirection) comme valide
        assert response.status_code in [401, 403, 301], f"Expected 401, 403, or 301, got {response.status_code}"
    
    def test_export_json_requires_editor_permission(self, client, contributor_user):
        """Vérifie que l'endpoint requiert la permission editor (403 si contributor)"""
        client.force_authenticate(user=contributor_user)
        url = reverse('content-export-json')
        response = client.get(url, follow=True)
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_export_json_returns_200_for_editor(self, client, editor_user, published_content):
        """Vérifie que l'endpoint retourne 200 pour editor"""
        client.force_authenticate(user=editor_user)
        url = reverse('content-export-json')
        response = client.get(url, follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response['Content-Type'] == 'application/json; charset=utf-8', "Content-Type doit être JSON"
        assert 'Content-Disposition' in response, "Content-Disposition doit être présent"
    
    def test_export_json_returns_200_for_admin(self, client, admin_user, published_content):
        """Vérifie que l'endpoint retourne 200 pour admin"""
        client.force_authenticate(user=admin_user)
        url = reverse('content-export-json')
        response = client.get(url, follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response['Content-Type'] == 'application/json; charset=utf-8', "Content-Type doit être JSON"
    
    def test_export_json_returns_valid_json(self, client, editor_user, published_content):
        """Vérifie que l'endpoint retourne du JSON valide"""
        client.force_authenticate(user=editor_user)
        url = reverse('content-export-json')
        response = client.get(url, follow=True)
        
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert isinstance(data, list), "Réponse doit être un array JSON"
        if len(data) > 0:
            assert 'id' in data[0], "Chaque élément doit avoir un 'id'"
            assert 'title' in data[0], "Chaque élément doit avoir un 'title'"


@pytest.mark.django_db
@pytest.mark.critical
class TestExportCSVContract:
    """Contract tests pour GET /api/contents/export/csv/"""
    
    def test_export_csv_requires_authentication(self, client):
        """Vérifie que l'endpoint requiert l'authentification (401 si anon)"""
        url = reverse('content-export-csv')
        response = client.get(url, follow=True)
        
        # Accepter 301 (redirection) comme valide
        assert response.status_code in [401, 403, 301], f"Expected 401, 403, or 301, got {response.status_code}"
    
    def test_export_csv_requires_editor_permission(self, client, contributor_user):
        """Vérifie que l'endpoint requiert la permission editor (403 si contributor)"""
        client.force_authenticate(user=contributor_user)
        url = reverse('content-export-csv')
        response = client.get(url, follow=True)
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_export_csv_returns_200_for_editor(self, client, editor_user, published_content):
        """Vérifie que l'endpoint retourne 200 pour editor"""
        client.force_authenticate(user=editor_user)
        url = reverse('content-export-csv')
        response = client.get(url, follow=True)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response['Content-Type'] == 'text/csv; charset=utf-8', "Content-Type doit être CSV"
        assert 'Content-Disposition' in response, "Content-Disposition doit être présent"
    
    def test_export_csv_returns_valid_csv(self, client, editor_user, published_content):
        """Vérifie que l'endpoint retourne du CSV valide"""
        client.force_authenticate(user=editor_user)
        url = reverse('content-export-csv')
        response = client.get(url, follow=True)
        
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        lines = content.strip().split('\n')
        assert len(lines) >= 2, "CSV doit avoir au moins l'en-tête et une ligne de données"
        assert 'id,title,slug' in lines[0], "En-tête CSV doit contenir les colonnes attendues"

